import json
import requests
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from accaunts.models import CustomUser, Ban, DetailUser
from . import models, serializers
from django.utils import timezone

r = redis.Redis()  # подключаемся к редису

# url сервера с ботами
HOST_URL = "http://195.3.220.151:8888/"
ID_SHIFT = 0

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
        r.set(f"{self.operation}:{user_pk}", self.channel_name, ex=10*60)  # записываем в редис channel_name подключенного юзера
        await self.accept()  # подтверждение

        # продолжение обработки заявки при разрыве соединения
        if r.get(f"user_{self.operation}:{user_pk}"):
            request_pk = int(r.getex(f"user_{self.operation}:{user_pk}", ex=10*60))
            await self.send(json.dumps({"status": "continue", "detail": request_pk}))
            await self.send_request_status(request_pk, self.status_delay)
            r.delete(f"user_{self.operation}:{user_pk}")

    async def disconnect(self, code):
        """Отключение пользователя"""
        r.delete(f"{self.operation}:{self.scope['user'].pk}")  # удаляет запись об юзере из редиса при отключении

    async def receive(self, text_data=None, bytes_data=None):
        """Принятие сообщения"""

        text_data_json = json.loads(text_data)
        # если в полученном json есть ключ create, под которым должен храниться json для создания запроса
        if text_data_json.get('create'):
            if r.getex(f"user_{self.operation}:{self.scope['user'].pk}", ex=10*60):
                await self.send(json.dumps({'status': 'error', 'detail': 'you already have a request.'}))
            else:
                await self.create_request(json.loads(text_data_json['create']))
        else:
            await self.send(json.dumps({'status': 'error', 'detail': 'missing "create" in json'}))

    async def check_conditions(self, text_data_json):
        """Проверяет условия создания заявки. OK - заявку можно продолжать создавать"""
        return "OK"

    async def get_bot_name(self, response):
        """Получает имя бота из запроса"""
        return response[0].get('name')

    async def create_request(self, text_data_json):
        """Создаёт новую заявку"""
        # проверяет правильность полученных данных
        serializer = self.model_serializer(data=text_data_json)
        if serializer.is_valid():
            user = self.scope['user']
            # проверяет условия, специфичные для типа операции
            check_result = await self.check_conditions(text_data_json)
            if check_result != "OK":
                message = {"status": "error","detail": check_result}
                await self.send(json.dumps(message))
                return
            
            # проверяет, создаётся ли заявка для текущего юзера
            if user.pk != serializer.validated_data['user']['id']:
                message = {"status": "error","detail": "can't create request for other user"}
                await self.send(json.dumps(message))
                return

            # проверяет, находится ли юзер в бане
            ban_tuple = await Ban.objects.aget_or_create(user=user)
            ban = await sync_to_async(ban_tuple.__getitem__)(0)
            if ban.ban:
                message = {"status": "error","detail": "user banned"}
                await self.send(json.dumps(message))
                return

            # поиск свободного бота
            amount = serializer.validated_data.get('amount')
            url_get_free_bot = f"{HOST_URL}{self.operation}/get_free?bet={amount}"

            # -1 - нет свободных ботов
            bot_id = -1
            retries = 0
            MAX_RETRIES = 100
            # пока не нашли свободного бота
            while bot_id == -1:
                retries += 1
                # если слишком много запрсов, то перестаём искать
                if retries > MAX_RETRIES:
                    message = {"status": "error","detail": "Can't find a free bot"}
                    await self.send(json.dumps(message))
                    return

                # запрос на сервер для поиска свободного бота
                try:
                    req = await sync_to_async(requests.get)(url_get_free_bot, timeout=2)
                except requests.exceptions.ConnectionError:
                    message = {"status": "process","detail": "Connection error"}
                    await self.send(json.dumps(message))
                    return
                except requests.exceptions.Timeout:
                    message = {"status": "process","detail": "Timeout"}
                    await self.send(json.dumps(message))
                    await asyncio.sleep(self.connection_delay)
                    continue

                # если был получен ответ с ошибкой
                if req.status_code != 200:
                    message = {"status": "error","detail": f"bot server unavailable (status code: {req.status_code})"}
                    await self.send(json.dumps(message))
                    return

                # получение id свободного бота
                bot_response = req.json()
                if 'bot_id' not in bot_response:
                    message = {"status": "error", "detail": "missing bot_id"}
                    await self.send(json.dumps(message))
                    return
                bot_id = bot_response['bot_id']

                # -1 в id бота - на сервере нет свободных ботов
                if bot_id == -1:
                    # отсылаем на фронт ответ о том, что поиск ещё идёт
                    message = {"status": "process","detail": "finding free bots"}
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
                message = {"status": "error","detail": "None get when trying to get a bot_owner"}
                await self.send(json.dumps(message))
                return

            # если бота занял другой пользователь, то прерывает создание заявки
            if int(bot_owner) != user.pk:
                message = {"status": "error","detail": "bot were taken"}
                await self.send(json.dumps(message))
                return
            
            # получает имя бота по его id 
            url_get_bot_info = f"{HOST_URL}{self.operation}/get_bot_info?bot_id={bot_id}"
            try:
                req = await sync_to_async(requests.get)(url_get_bot_info, timeout=3)
            except requests.exceptions.ConnectionError:
                message = {"status": "error", "detail": "Connection error"}
                await self.send(json.dumps(message))
                return
            except requests.exceptions.Timeout:
                message = {"status": "error", "detail": "Timeout"}
                await self.send(json.dumps(message))
                return
            
            # если код ответа не успешный, то прерывает создание заявки
            if req.status_code != 200:
                message = {"status": "error","detail": f"bot server unavailable (status code: {req.status_code})"}
                await self.send(json.dumps(message))
                return
            
            # получает список ботов из ответа сервера
            bot_list = req.json()

            # получает имя бота, с которым нужно будет взаимодействовать пользователю
            bot_name = await self.get_bot_name(bot_list)

            # посылаем имя бота на фронт для отображения пользователю
            message = {"status": "get_name","detail": bot_name}
            await self.send(json.dumps(message))

            # создаёт заявку и сохраняет её в бд
            new_request = await sync_to_async(serializer.save)()

            # создаёт заявку на сервере ботов
            new_request.request_id = new_request.pk + ID_SHIFT
            await sync_to_async(new_request.save)()
            url_request_create = f"{HOST_URL}{self.operation}/create?id={new_request.request_id}&bot_id={bot_id}&site_id={user.pk}&bet={new_request.amount}"
            if not new_request.game_id is None:
                url_request_create += f"&game_id={new_request.game_id}"
            
            try:
                req = await sync_to_async(requests.get)(url_request_create, timeout=2)
            except requests.exceptions.ConnectionError:
                message = {"status": "error", "detail": "Connection error"}
                await self.send(json.dumps(message))
                return
            except requests.exceptions.Timeout:
                message = {"status": "error", "detail": "Timeout"}
                await self.send(json.dumps(message))
                return
            
            # если статус ответа не был успешен, то заканчивает создание заявки
            if req.status_code != 200:
                message = {"status": "error","detail": f"bot server unavailable (status code: {req.status_code})"}
                await self.send(json.dumps(message))
                return

            # проверяет, создалась ли заявка на сервере
            bot_response = req.json()
            if bot_response.get('ok') == False:
                message = {"status": "error","detail": f"Error while creating a request: {bot_response.get('message')})"}
                await self.send(json.dumps(message))
                return
            
            # запоминает в редис заявку пользователя для её обработки в случае перезагрузки страницы
            r.set(f"user_{self.operation}:{user.pk}", new_request.pk, ex=10*60)
            # если заявка на сервере создалась, то отправляет заявку на клиент
            response_serializer = self.model_serializer(new_request)
            serializer_data = await sync_to_async(getattr)(response_serializer, 'data')
            await self.send(json.dumps(serializer_data))
            # удаляет из redis запись о занятии пользователем бота
            r.delete(f"bot:{bot_id}")

            # запускает процесс мониторинга состояния заявки
            await self.send_request_status(new_request.pk, self.status_delay)
            r.delete(f"user_{self.operation}:{user.pk}")

            return
        
        # отрабатывает если данные для создания заявки, полученные от клиента, были неправильными
        message = {"status": "error","detail": "bad data"}
        await self.send(json.dumps(message))

    async def send_request_status(self, request_pk, delay):
        """Получает от сервера ботов и посылает клиенту статус заявки"""
        # создаёт url для получения статуса заявки
        url_get_status = f"{HOST_URL}{self.operation}/get?id={request_pk + ID_SHIFT}"
        # считает количество повторений цикла для избежания зацикливания
        retries = 0
        max_retries = 250
        # в цикле с интервалом delay получает статус заявки и отсылает его на клиент
        while retries < max_retries:
            retries += 1
            # получает статус заявки от сервера
            try:
                req = await sync_to_async(requests.get)(url_get_status, timeout=3)
            except requests.ConnectionError:
                message = {"status": "process", "detail": "Connection error"}
                await asyncio.sleep(delay)
                await self.send(json.dumps(message))
                continue
            except requests.Timeout:
                await asyncio.sleep(delay)
                continue

            # если статус ответа сервера не успешный, то, после задержки, опрашивает сервер ещё раз
            if req.status_code != 200:
                message = {"status": "process", "detail": f"Get status code from server: {req.status_code}"}
                await self.send(json.dumps(message))
                await asyncio.sleep(delay)
                continue
            
            # пересылает ответ сервера на фронт для обработки
            await self.send(req.text)

            # проверяет статус заявки
            info = req.json()
            if info.get('done'):
                # достаёт заявку из бд
                user_request = await self.model.objects.aget(pk=request_pk)
                # проверяет, не была ли заявка закрыта ранее
                if user_request.status != 'open' or r.getex(f'close_{request_pk}:{self.operation}:bool', ex=10*60):
                    serializer = self.model_serializer(user_request)
                    serializer_data = await sync_to_async(getattr)(serializer, 'data')
                    await self.send(json.dumps(serializer_data))
                    await self.send(json.dumps({"status": "error", "detail": "second page prevented"}))
                    return
                # закрывает заявку в БД
                # отмечает заявку как закрытую
                r.set(f'close_{request_pk}:{self.operation}:bool', "closed", ex=10*60)
                # изменяет статус заявки
                user_request.close_reason = info.get('close_reason')
                user_request.note = info.get('note')                
                user_request.date_closed = timezone.now()
                if info.get('close_reason') == 'Success':
                    user_request.status = 'succ'
                else:
                    user_request.status = 'fail'
                # производит операции с балансом пользователя
                await self.process_balance(user_request, info)
                await sync_to_async(user_request.save)()
                # банит пользователя, если его забанил сервер
                if info.get('ban'):
                    ban = await Ban.objects.aget(user=user_request.user)
                    ban.ban = True
                    await sync_to_async(ban.save)()
                # посылает закрытую заявку на клиент
                serializer = self.model_serializer(user_request)
                serializer_data = await sync_to_async(getattr)(serializer, 'data')
                await self.send(json.dumps(serializer_data))

                return
            # задержка перед следующим опросом сервера
            await asyncio.sleep(delay)

        # отрабатывает если цикл выше закончился по причине большого количества повторений
        message = {"status": "error", "detail": "Too many requests"}
        await self.send(json.dumps(message))

    async def process_balance(self, user_request, response):
        """Производит операции с балансом пользователя"""
        # начисление на баланс пользователя полученных кредитов
        user_request.amount = response.get('refiil')
        if user_request.amount > 0:
            detail_user = await DetailUser.objects.aget(user=user_request.user)
            detail_user.balance += user_request.amount
            await sync_to_async(detail_user.save)()


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
    """Consumer для создание заявок на вывод кредитов"""
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
        if detail_user.balance < text_data_json.get('amount', 0):
            return "Not enough credits."
        return "OK"

    async def process_balance(self, user_request, response):
            """Производит операции с балансом пользователя"""
            # начисление на баланс пользователя полученных кредитов
            user_request.amount = response.get('withdraw')
            if user_request.amount > 0:
                detail_user = await DetailUser.objects.aget(user=user_request.user)
                detail_user.balance -= user_request.amount
                await sync_to_async(detail_user.save)()

    async def get_bot_name(self, response):
        """Получает имя бота из запроса"""
        return response.get('name')
