import asyncio
import json
import threading

import aiohttp
import redis
import requests
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.utils import Error
from django.utils import timezone

from accaunts.models import Ban, CustomUser, DetailUser
from configs.settings import (HOST_URL, ID_SHIFT, REDIS_PASSWORD,
                              REDIS_URL_STACK)
from ws_chat.tasks import (ban_user_for_bad_request, send_balance_to_single,
                           setup_check_request_status)

from . import models, serializers
from .models import BanTime, BotWork, RefillRequest, WithdrawalRequest

r = redis.Redis(encoding="utf-8", decode_responses=True, host=REDIS_URL_STACK, password=REDIS_PASSWORD)  # подключаемся к редису


class RequestConsumer(AsyncWebsocketConsumer):
    """Базовый класс для создания заявок"""
    # поля ниже заполнены как для RefillConsumer - создание заявки на пополнение счёта
    # название операции заявки
    operation = 'refill'
    # модель для хранения заявки в БД
    model = models.RefillRequest
    # сериализатор для заявки
    model_serializer = serializers.RefillRequestModelSerializer
    # задержка между повторными запросами
    connection_delay = 3
    # задержка между обновлениями статуса
    status_delay = 3

    async def connect(self):
        """Подключение юзеров"""
        user_pk = str(self.scope['user'].pk)  # получаем pk пользователя который подключился с фронта
        # r.set(f"{self.operation}:{user_pk}", self.channel_name, ex=10*60)  # записываем в редис channel_name подключенного юзера
        await self.accept()  # подтверждение

        # продолжение обработки заявки при разрыве соединения
        if r.get(f"user_{self.operation}:{user_pk}"):
            request_pk = int(r.getex(f"user_{self.operation}:{user_pk}", ex=10*60))
            start_time = int(r.getex(f"user_{self.operation}:{user_pk}:start", ex=10*60))
            await self.send(json.dumps({"status": "continue", "detail": request_pk, "start": start_time}))
            # достаёт заявку из бд
            try:
                user_request = await self.model.objects.aget(pk=request_pk)
            except self.model.DoesNotExist as err:
                user_request = self.model(request_id=request_pk+ID_SHIFT)
                user_request.user = self.scope.get('user')
                await self.send(json.dumps({"status": "process", "detail": "Создаём новый запрос в базе данных..."}))
            except Error as err:
                await self.send(json.dumps({"status": "error", "detail": f"Ошибка базы данных."}))
                return
            # отправляет имя бота на фронт
            message = {"status": "get_name","detail": user_request.bot_name}
            await self.send(json.dumps(message))
            # посылает заявку на фронт
            serializer = self.model_serializer(user_request)
            serializer_data = await sync_to_async(getattr)(serializer, 'data')
            await self.send(json.dumps(serializer_data))
            # начинает обрабатывать заявку
            await self.send_request_status(request_pk, self.status_delay)
            r.delete(f"user_{self.operation}:{user_pk}")
            r.delete(f"user_{self.operation}:{user_pk}:start")

    async def disconnect(self, code):
        """Отключение пользователя"""
        # r.delete(f"{self.operation}:{self.scope['user'].pk}")  # удаляет запись об юзере из редиса при отключении
        pass

    async def receive(self, text_data=None, bytes_data=None):
        """Принятие сообщения"""

        text_data_json = json.loads(text_data)
        # если в полученном json есть ключ create, под которым должен храниться json для создания запроса
        if text_data_json.get('create'):
            if r.getex(f"user_{self.operation}:{self.scope['user'].pk}", ex=10*60):
                await self.send(json.dumps({'status': 'error', 'detail': 'Вы уже создали запрос.'}))
            else:
                try:
                    await self.create_request(text_data_json['create'])
                except json.decoder.JSONDecodeError:
                    await self.send(json.dumps({'status': 'error', 'detail': 'Неверный формат запроса.'}))
        else:
            await self.send(json.dumps({'status': 'error', 'detail': 'Отсутствует "create" в json.'}))

    async def check_conditions(self, text_data_json):
        """Проверяет условия создания заявки. OK - заявку можно продолжать создавать"""
        return "OK"

    async def get_bot_name(self, response):
        """Получает имя бота из запроса"""
        if type(response) == dict:
            return response.get('name')
        elif type(response) == list and len(response) > 0 and type(response[0]) == dict:
            return response[0].get('name')
        return "Can't find name in server response."

    async def freeze_balance(self, amount):
        """Замораживает средства перед выводом"""
        pass

    def get_request(self, spisok):
        response = requests.get("http://178.211.139.11:8888/refill/get_bot_info?bot_id=0").json()
        print(response, "ETO RESPONSE IN REQUEST")
        spisok.append(response)
    async def create_request(self, text_data_json):
        """Создаёт новую заявку"""
        # отключение бота
        s = await BotWork.objects.afirst()
        if s.work and self.operation == 'refill':
            message = {"status": "error", "detail": "Идут работы!!!"}
            await self.send(json.dumps(message))
            return
        if s.work_t and self.operation == 'withdraw':
            message = {"status": "error", "detail": "Идут работы!!!"}
            await self.send(json.dumps(message))
            return
        # проверяет правильность полученных данных
        if text_data_json.get('user') is None:
            text_data_json['user'] = {"id": self.scope['user'].pk}
        serializer = self.model_serializer(data=text_data_json)
        if serializer.is_valid():
            user = self.scope['user']
            # проверяет условия, специфичные для типа операции
            check_result = await self.check_conditions(text_data_json)
            if check_result != "OK":
                message = {"status": "error", "detail": check_result}
                await self.send(json.dumps(message))
                return
            
            # проверяет, создаётся ли заявка для текущего юзера
            if user.pk != serializer.validated_data['user']['id']:
                message = {"status": "error", "detail": "Нельзя создать заявку для другого пользователя."}
                await self.send(json.dumps(message))
                return

            # проверяет, находится ли юзер в бане
            try:
                # ban_tuple = await Ban.objects.aget_or_create(user=user)
                ban_tuple = await Ban.objects.aget(user=user)
            except (Error, Ban.DoesNotExist) as err:
                await self.send(json.dumps({"status": "error", "detail": "Ошибка доступа к базе данных."}))
                return
            # ban = await sync_to_async(ban_tuple.__getitem__)(0)
            # if ban.ban_site:
            if ban_tuple.ban_site:
                message = {"status": "error", "detail": "На сервере ведутся технические работы."}
                await self.send(json.dumps(message))
                return

            # поиск свободного бота
            amount = serializer.validated_data.get('amount')
            url_get_free_bot = f"{HOST_URL}{self.operation}/get_free?bet={amount}"

            # -1 - нет свободных ботов
            bot_id = -1
            retries = 0
            MAX_RETRIES = 100
            timeout = aiohttp.ClientTimeout(total=2)
            async with aiohttp.ClientSession(timeout=timeout, raise_for_status=True) as session:
            # пока не нашли свободного бота
                while bot_id == -1:
                    retries += 1
                    # если слишком много запрсов, то перестаём искать
                    if retries > MAX_RETRIES:
                        message = {"status": "error", "detail": "Нет свободных ботов."}
                        await self.send(json.dumps(message))
                        return
                    # пытается получить от сервера ответ
                    try:
                        resp = await session.get(url_get_free_bot)
                        bot_response = await resp.json()
                        resp.close()
                    except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError, asyncio.exceptions.TimeoutError) as err:
                        # при этих ошибках можно попробовать продолжить посылать запросы серверу
                        await self.send(json.dumps({"status": "process", "detail": f"Ошибка подключения к серверу ботов."}))
                        await asyncio.sleep(self.connection_delay)
                        continue
                    except aiohttp.ClientError as err:
                        await self.send(json.dumps({"status": "error", "detail": f"Ошибка подключения к серверу ботов."}))
                        return

                    if 'bot_id' not in bot_response:
                        message = {"status": "error", "detail": "Отсутствует bot_id."}
                        await self.send(json.dumps(message))
                        return
                    bot_id = bot_response['bot_id']

                    # -1 в id бота - на сервере нет свободных ботов
                    if bot_id == -1:
                        # отсылаем на фронт ответ о том, что поиск ещё идёт
                        message = {"status": "process", "detail": "Поиск свободных ботов..."}
                        await self.send(json.dumps(message))
                        await asyncio.sleep(self.connection_delay)
                    else:
                        # записывает в redis пользователя, который будет использовать бота
                        r.set(f'bot:{bot_id}', user.pk, ex=60)
                        break

                # проверяет, не успел ли кто-то занять бота
                bot_owner = r.getex(f"bot:{bot_id}", ex=60)

                # если бота кто-то использовал, то прерывает создание заявки
                if bot_owner is None:
                    message = {"status": "error", "detail": "Игровой бот занят."}
                    await self.send(json.dumps(message))
                    return
                # если бота занял другой пользователь, то прерывает создание заявки
                if int(bot_owner) != user.pk:
                    message = {"status": "error", "detail": "Игровой бот занят."}
                    await self.send(json.dumps(message))
                    return 
                # получает имя бота по его id 
                url_get_bot_info = f"{HOST_URL}{self.operation}/get_bot_info?bot_id={bot_id}"
                # получает список ботов из ответа сервера
                print(url_get_bot_info)
                spisok = []
                try:
                    resp = await session.get(url_get_bot_info)
                    # t1 = threading.Thread(target=self.get_request, args=(spisok,))
                    # t1.start()
                    # t1.join()
                    # print(spisok, "<<<<<<<<<<<<<<<<<<<SPISOK")
                    bot_list = await resp.json()
                    # bot_list = spisok[0]
                    # print(bot_list, "ETO BOT_LIST")
                except (aiohttp.ClientError, asyncio.exceptions.TimeoutError) as err:
                    print(err.__dict__)
                    await self.send(json.dumps({"status": "error", "detail": f"Ошибка получения имени бота.",}))
                    return
                finally:
                    resp.close()
                # получает имя бота, с которым нужно будет взаимодействовать пользователю
                bot_name = await self.get_bot_name(bot_list)
                # посылаем имя бота на фронт для отображения пользователю
                message = {"status": "get_name", "detail": bot_name}
                await self.send(json.dumps(message))

                # создаёт заявку и сохраняет её в бд
                try:
                    new_request = await sync_to_async(serializer.save)()
                except Error as err:
                    await self.send(json.dumps({"status": "error", "detail": "Невозможно сохранить заявку в базе данных."}))
                    return

                # создаёт заявку на сервере ботов
                # ID_SHIFT используется для сдвига значений id запросов на сервере ботов, т.к. первые id уже могут быть заняты
                new_request.request_id = new_request.pk + ID_SHIFT
                new_request.bot_name = bot_name
                try:
                    await sync_to_async(new_request.save)()
                except Error as err:
                    await self.send(json.dumps({"status": "process", "detail": f"Loosing request ID: {new_request.request_id}"}))
                url_request_create = f"{HOST_URL}{self.operation}/create?id={new_request.request_id}&bot_id={bot_id}&site_id={user.random_id}&bet={new_request.amount}"
                if self.operation == 'withdraw':
                    url_request_create += f"&balance={new_request.balance}"
                if not new_request.game_id is None:
                    url_request_create += f"&game_id={new_request.game_id}"

                try:
                    resp = await session.get(url_request_create)
                    bot_response = await resp.json()
                    resp.close()
                except (aiohttp.ClientError, asyncio.exceptions.TimeoutError) as err:
                    await self.send(json.dumps({"status": "error", "detail": "Сервер ботов недоступен."}))
                    return

            # проверяет, создалась ли заявка на сервере
            if bot_response.get('ok') == False:
                message = {"status": "error","detail": f"Ошибка создания заявки на сервере ботов: {bot_response.get('message')})"}
                await self.send(json.dumps(message))
                return
            
            # запоминает в редис заявку пользователя для её обработки в случае перезагрузки страницы
            r.set(f"user_{self.operation}:{user.pk}", new_request.pk, ex=10*60)
            start_time = round(timezone.now().timestamp())
            r.set(f"user_{self.operation}:{user.pk}:start", start_time, ex=10*60)
            # если заявка на сервере создалась, то отправляет заявку на клиент
            response_serializer = self.model_serializer(new_request)
            serializer_data = await sync_to_async(getattr)(response_serializer, 'data')
            await self.send(json.dumps(serializer_data))

            # удаляет из redis запись о занятии пользователем бота
            r.delete(f"bot:{bot_id}")
            # отложенное задание - проверить статус заявки через 15 минут
            setup_check_request_status(HOST_URL, self.operation, ID_SHIFT, new_request.pk, self.scope['user'].pk, 11*60)
            # операции с балансом
            await self.freeze_balance(amount)
            # запускает процесс мониторинга состояния заявки
            await self.send_request_status(new_request.pk, self.status_delay)
            r.delete(f"user_{self.operation}:{user.pk}")
            r.delete(f"user_{self.operation}:{user.pk}:start")
            return
        
        # отрабатывает если данные для создания заявки, полученные от клиента, были неправильными
        message = {"status": "error","detail": "Неверный формат данных."}
        await self.send(json.dumps(message))

    async def send_request_status(self, request_pk, delay):
        """Получает от сервера ботов и посылает клиенту статус заявки"""
        # создаёт url для получения статуса заявки
        url_get_status = f"{HOST_URL}{self.operation}/get?id={request_pk + ID_SHIFT}"
        # считает количество повторений цикла для избежания зацикливания
        retries = 0
        max_retries = 250
        # в цикле с интервалом delay получает статус заявки и отсылает его на клиент
        timeout = aiohttp.ClientTimeout(total=2)
        async with aiohttp.ClientSession(timeout=timeout, raise_for_status=True) as session:
            while retries < max_retries:
                retries += 1
                req_txt = None
                try:
                    resp = await session.get(url_get_status)
                    req_txt = await resp.text()
                    info = await resp.json()
                    resp.close()
                except (aiohttp.ClientConnectionError, aiohttp.ServerTimeoutError, asyncio.exceptions.TimeoutError) as err:
                    await self.send(json.dumps({"status": "process", "detail": f"{type(err)}"}))
                    await asyncio.sleep(delay)
                    continue
                except aiohttp.ClientError as err:
                    await self.send(json.dumps({"status": "process", "detail": f"Error while fetching request status from bot server. {type(err)}"}))
                # пересылает ответ сервера на фронт для обработки
                if req_txt:
                    await self.send(req_txt)
                else:
                    await self.send(json.dumps({"status": "process", "detail": f"{type(err)}"}))
                    await asyncio.sleep(delay)
                    continue

                # проверяет статус заявки
                if info.get('done'):
                    # достаёт заявку из бд
                    try:
                        user_request = await self.model.objects.aget(pk=request_pk)
                    except self.model.DoesNotExist as err:
                        user_request = self.model(request_id=request_pk+ID_SHIFT)
                        user_request.user = self.scope.get('user')
                        await self.send(json.dumps({"status": "process", "detail": "Can't find user request. New one is created"}))
                    except Error as err:
                        await self.send(json.dumps({"status": "error", "detail": f"Ошибка базы данных."}))
                        return
                    # проверяет, не была ли заявка закрыта ранее
                    if user_request.status != 'open' or r.getex(f'close_{request_pk}:{self.operation}:bool', ex=10*60):
                        serializer = self.model_serializer(user_request)
                        serializer_data = await sync_to_async(getattr)(serializer, 'data')
                        await self.send(json.dumps(serializer_data))
                        await self.send(json.dumps({"status": "error", "detail": "Открыто более одной вкладки!"}))
                        return
                    # закрывает заявку в БД
                    # отмечает заявку как закрытую
                    r.set(f'close_{request_pk}:{self.operation}:bool', "closed", ex=10*60)
                    # изменяет статус заявки
                    user_request.close_reason = info.get('close_reason')
                    user_request.note = info.get('note')       
                    user_request.game_id = info.get('game_id')         
                    user_request.date_closed = timezone.now()
                    if info.get('close_reason') == 'Success':
                        user_request.status = 'succ'
                    else:
                        user_request.status = 'fail'
                    # производит проверку количества аккаунтов у одного game_id(не более 4)
                    if await WithdrawalRequest.objects.filter(game_id=user_request.game_id).distinct(
                            'user').acount() >= 4:
                        ban = await Ban.objects.aget(user=user_request.user)
                        ban.ban_site = True
                        await sync_to_async(ban.save)()
                        message = {"status": "error", "detail": "user banned"}
                        await self.send(json.dumps(message))
                        user_request.status = 'fail'
                        await sync_to_async(user_request.save)()
                        return
                    else:
                        # производит операции с балансом пользователя
                        try:
                            await self.process_balance(user_request, info)
                            await sync_to_async(user_request.save)()
                        except Error as err:
                            await self.send(json.dumps({"status": "error", "detail": f"Ошибка базы данных. Заявка не сохранена."}))
                            return
                        # банит пользователя, если его забанил сервер
                        if info.get('ban'):
                            try:
                                ban = await Ban.objects.aget(user_id=user_request.user_id)
                                ban.ban_site = True
                                await sync_to_async(ban.save)()
                            except Error as err:
                                await self.send(json.dumps({"status": "error", "detail": f"Ошибка базы данных."}))
                                return
                        # банит пользователя если у него три подряд закрытые заявки с причинами закрытия
                        ban_user_for_bad_request.apply_async(args=(self.scope['user'].pk, self.operation))
                        # посылает закрытую заявку на клиент
                        serializer = self.model_serializer(user_request)
                        serializer_data = await sync_to_async(getattr)(serializer, 'data')
                        await self.send(json.dumps(serializer_data))
                        send_balance_to_single.apply_async(args=(self.scope['user'].id,))
                        # закрываем соединение
                        await self.close(1000)
                        return
                # задержка перед следующим опросом сервера
                await asyncio.sleep(delay)

        # отрабатывает если цикл выше закончился по причине большого количества повторений
        message = {"status": "error", "detail": "Превышено максимальное количество запросов на сервер ботов."}
        await self.send(json.dumps(message))

    async def process_balance(self, user_request, response):
        """Производит операции с балансом пользователя"""
        # начисление на баланс пользователя полученных кредитов
        user_request.amount = response.get('refiil')
        if user_request.amount > 0:
            detail_user = await DetailUser.objects.aget(user_id=user_request.user_id)
            detail_user.balance += user_request.amount
            await sync_to_async(detail_user.save)()

    async def send_ban(self, event):
        """Отправляет пользователю сообщение о том, что он забанен"""
        message = event['detail']
        await self.send(json.dumps(message))


class RefillConsumer(RequestConsumer):
    """Consumer для создания заявок на пополнение счёта"""
    # название операции заявки
    operation = 'refill'
    # модель для хранения заявки в БД
    model = models.RefillRequest
    # сериализатор для заявки
    model_serializer = serializers.RefillRequestModelSerializer
    # задержка между повторными запросами
    connection_delay = 3


class WithdrawConsumer(RequestConsumer):
    """Consumer для создания заявок на вывод кредитов"""
    # название операции заявки
    operation = 'withdraw'
    # модель для хранения заявки в БД
    model = models.WithdrawalRequest
    # сериализатор для заявки
    model_serializer = serializers.WithdrawRequestModelSerializer
    # задержка между повторными запросами
    connection_delay = 10

    async def check_conditions(self, text_data_json):
        user = self.scope['user']
        detail_user = await DetailUser.objects.aget(user=user)
        if detail_user.balance < int(text_data_json.get('amount', 0)):
            return "Недостаточно кредитов."
        return "OK"

    async def process_balance(self, user_request, response):
        """Производит операции с балансом пользователя"""
        # начисление на баланс пользователя полученных кредитов
        user_request.amount = response.get('withdraw')
        detail_user = await DetailUser.objects.aget(user_id=user_request.user_id)
        frozen_balance_remain = detail_user.frozen_balance - user_request.amount
        new_balance = max(0, detail_user.balance + frozen_balance_remain)
        detail_user.balance = new_balance
        detail_user.frozen_balance = 0
        await sync_to_async(detail_user.save)()

    async def freeze_balance(self, amount):
        """Замораживает средства перед выводом"""
        if amount > 0:
            detail_user = await DetailUser.objects.aget(user_id=self.scope['user'].id)
            new_balance = max(0, detail_user.balance - amount)
            detail_user.frozen_balance = detail_user.balance - new_balance
            detail_user.balance = new_balance
            await sync_to_async(detail_user.save)()
            send_balance_to_single.apply_async(args=(self.scope['user'].id,))
