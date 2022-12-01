import json
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from accaunts.models import CustomUser
from . import models, serializers

r = redis.Redis()  # подключаемся к редису

# from . import tasks


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
            await self.create_refill_request(text_data_json)

    async def create_refill_request(self, text_data_json):
        """Создаёт новую заявку на пополнение"""
        serializer = serializers.RefillRequestModelSerializer(data=text_data_json)
        if serializer.is_valid():
            if self.scope['user'].pk != serializer.validated_data['user_id']['id']:
                await self.send({"status": "error","detail": "can't create request for other user"})

            refill_request = sync_to_async(serializer.save)()
            response_serializer = serializers.RefillRequestModelSerializer(refill_request)
            return self.send(response_serializer.data)
        
        await self.send({"status": "error","detail": "bad data"})
        