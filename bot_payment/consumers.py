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
                req = requests.get(url_get_bot_info)
            except requests.exceptions.ConnectionError:
                message = {"status": "error", "detail": "bot were taken"}
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

            # todo: создание заявки


            # создаёт заявку
            refill_request = await sync_to_async(serializer.save)()  
            response_serializer = serializers.RefillRequestModelSerializer(refill_request)
            await self.send(json.dumps(response_serializer.data))
            r.delete(f"bot:{bot_id}")
            return
        
        message = {"status": "error","detail": "bad data"}
        await self.send(json.dumps(message))
        