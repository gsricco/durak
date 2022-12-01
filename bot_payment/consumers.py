import json
import requests
import asyncio
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from accaunts.models import CustomUser, Ban
from . import models, serializers

r = redis.Redis()  # подключаемся к редису

# from . import tasks

# url сервера с ботами
HOST_URL = "http://195.3.220.151:8888/"

class RefillConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        '''Подключение юзеров'''
        user_pk = str(self.scope['user'].pk)  # получаем pk пользователя который подключился с фронта
        r.set(f"refill:{user_pk}", self.channel_name, ex=10*60)  # записываем в редис channel_name подключенного юзера
        await self.accept()  # подтверждение

    async def disconnect(self, code):
        """Отключение пользователя"""
        r.delete(f"refill:{self.scope['user'].pk}")  # удаляет запись об юзере из редиса при отключении

    async def receive(self, text_data=None, bytes_data=None):
        """Принятие сообщения"""

        text_data_json = json.loads(text_data)
        if text_data_json.get('create'):
            await self.create_refill_request(json.loads(text_data_json['create']))
        else:
            await self.send(json.dumps({'status': 'error', 'detail': 'missing "create" in json'}))

    async def create_refill_request(self, text_data_json):
        """Создаёт новую заявку на пополнение"""
        serializer = serializers.RefillRequestModelSerializer(data=text_data_json)
        if serializer.is_valid():
            user = self.scope['user']
            # проверяет, создаётся ли заявка для текущего юзера
            if user.pk != serializer.validated_data['user_id']['id']:
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
            url_get_free_bot = f"{HOST_URL}refill/get_free?bet={amount}"

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

                try:
                    req = await sync_to_async(requests.get)(url_get_free_bot)
                except requests.exceptions.ConnectionError:
                    message = {"status": "error","detail": "Connection error"}
                    await self.send(json.dumps(message))
                    return

                if req.status_code != 200:
                    message = {"status": "error","detail": f"bot server unavailable (status code: {req.status_code})"}
                    await self.send(json.dumps(message))
                    return

                bot_response = req.json()
                if 'bot_id' not in bot_response:
                    message = {"status": "error","detail": "missing bot_id"}
                    await self.send(json.dumps(message))
                    return

                bot_id = bot_response['bot_id']
                if bot_id == -1:
                    message = {"status": "process","detail": "no free bots"}
                    await self.send(json.dumps(message))
                    await asyncio.sleep(3)
                else:
                    r.set(f'bot:{bot_id}', user.pk, ex=60)
                    break

            # проверяем, не успел ли кто-то занять бота
            bot_owner = r.getex(f"bot:{bot_id}", ex=30)

            if bot_owner is None:
                message = {"status": "error","detail": "None get when trying to get a bot_owner"}
                await self.send(json.dumps(message))
                return

            if int(bot_owner) != user.pk:
                message = {"status": "error","detail": "bot were taken"}
                await self.send(json.dumps(message))
                return
            
            # получаем имя бота
            url_get_bot_info = f"{HOST_URL}refill/get_bot_info?bot_id={bot_id}"
            try:
                req = await sync_to_async(requests.get)(url_get_bot_info)
            except requests.exceptions.ConnectionError:
                message = {"status": "error", "detail": "Connection error"}
                await self.send(json.dumps(message))
                return
            
            if req.status_code != 200:
                message = {"status": "error","detail": f"bot server unavailable (status code: {req.status_code})"}
                await self.send(json.dumps(message))
                return
            
            bot_list = req.json()
            # todo: проверка bot_list на наличи значений.
            bot_name = bot_list[0].get('name')
            # посылаем имя бота на фронт для отображения пользователю
            message = {"status": "get_name","detail": bot_name}
            await self.send(json.dumps(message))

            # создаёт заявку и сохраняет её в бд
            refill_request = await sync_to_async(serializer.save)()

            # создаёт заявку на сервере ботов
            url_refill_create = f"{HOST_URL}refill/create?id={refill_request.pk}&bot_id={bot_id}&site_id={user.pk}&bet={refill_request.amount}"
            if not refill_request.game_id is None:
                url_refill_create += f"&game_id={refill_request.game_id}"
            
            try:
                req = await sync_to_async(requests.get)(url_refill_create)
            except requests.exceptions.ConnectionError:
                message = {"status": "error", "detail": "bot were taken"}
                await self.send(json.dumps(message))
                return
            
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
            
            # если заявка на сервере создалась (см. выше), то отправляем заявку на клиент
            response_serializer = serializers.RefillRequestModelSerializer(refill_request)
            serializer_data = await sync_to_async(getattr)(response_serializer, 'data')
            await self.send(json.dumps(serializer_data))
            r.delete(f"bot:{bot_id}")

            await self.send_request_status(refill_request.pk, 3)

            return
        
        message = {"status": "error","detail": "bad data"}
        await self.send(json.dumps(message))

    async def send_request_status(self, request_id, delay):
        """Получает от сервера ботов и посылает клиенту статус заявки на пополнение"""
        # создаёт url для получения статуса заявки
        url_get_status = f"{HOST_URL}refill/get?id={request_id}"
        # считает количество повторений цикла для избежания зацикливания
        retries = 0
        max_retries = 150
        # в цикле с интервалом delay получаем статус заявки и отсылаем его на клиент
        while retries < max_retries:
            retries += 1
            try:
                req = await sync_to_async(requests.get)(url_get_status, timeout=2)
            except requests.ConnectionError:
                message = {"status": "error", "detail": "Connection error"}
                await asyncio.sleep(delay)
                await self.send(json.dumps(message))
                continue
            except requests.Timeout:
                await asyncio.sleep(delay)
                continue

            
            if req.status_code != 200:
                message = {"status": "error", "detail": f"Get status code from server: {req.status_code}"}
                await self.send(json.dumps(message))
                await asyncio.sleep(delay)
                continue

            await self.send(req.text)

            info = req.json()
            if info.get('closed'):
                # fail_close_reasons = (
                #     'NoMessage',
                #     'ClientScoreLessThanMinimum',
                #     'ClientBanned',
                #     'Timeout',
                #     'Error',
                # )
                refill_request = await models.RefillRequest.objects.aget(pk=request_id)
                refill_request.close_reason = info.get('close_reason')
                refill_request.note = info.get('note')
                refill_request.amount = info.get('refiil')
                if info.get('close_reason') == 'Success':
                    refill_request.status = 'succ'
                else:
                    refill_request.status = 'fail'
                await sync_to_async(refill_request.save)()
                
                serializer = serializers.RefillRequestModelSerializer(refill_request)
                serializer_data = await sync_to_async(getattr)(serializer, 'data')
                await self.send(json.dumps(serializer_data))

                return

            await asyncio.sleep(delay)

        message = {"status": "error", "detail": "Too many requests"}
        await self.send(json.dumps(message))
