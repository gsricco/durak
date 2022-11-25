import json
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from accaunts.models import CustomUser
from support_chat.models import Message, UserChatRoom
from support_chat.serializers import RoomSerializer, OnlyRoomSerializer

r = redis.Redis()  # подключаемся к редису

from . import tasks


class ChatConsumer(AsyncWebsocketConsumer):

    @sync_to_async
    def create_or_get_support_chat_room(self, user):  # получает или создает чат рум
        chat_room, created = UserChatRoom.objects.get_or_create(room_id=user)
        return chat_room

    @sync_to_async
    def save_user_message(self, room, user, message):  # сохраняет сообщение в бд
        if user:
            user = CustomUser.objects.get(username=user).pk
            user_mess = Message(user_posted_id=user, message=message)
            user_mess.save()
            room.message.add(user_mess, bulk=False)
            return user_mess

    @sync_to_async()
    def get_all_room(self):
        try:
            print("отработал get_all_room")
            rooms = UserChatRoom.objects.all()
            serializer = OnlyRoomSerializer(rooms, many=True)
            # print(serializer.data)
            for i in serializer.data:
                # print(i['room_id'])# отправляем все сообщения поочереди
                async_to_sync(self.channel_layer.send)(self.channel_name, {"type": "get_rooms",
                                                                           "room_name": i['room_id']
                                                                           })
        except:
            print('error get_all_room')

    async def send_online(self, num):
        '''функция отправки онлайна. вызывается при коннекте и дисконнекте'''
        online = self.channel_layer.receive_count + num
        await self.channel_layer.group_send(self.room_group_name, {"type": "get_online", "get_online": online})

    @sync_to_async()
    def send_json(self, channel, room_name):
        '''отправка истории сообщений'''
        try:
            room_data = UserChatRoom.objects.get(room_id=room_name)  # получаем комнату
            serializer = RoomSerializer(room_data)  # сериализуем ее
            for i in serializer.data.get('message'):  # отправляем все сообщения поочереди
                async_to_sync(self.channel_layer.send)(channel, {"type": "chat_message",
                                                                 "chat_type": "support",
                                                                 "message": i['message'],
                                                                 "user": i['user_posted']['username'],
                                                                 })
        except:
            pass

    async def send_support_chat_message(self, channel_name, message, user):
        '''Отправка сообщения в суппорт чат . Аргументы channel_name,message,user '''
        await self.channel_layer.send(
            channel_name, {"type": "chat_message",
                           "chat_type": "support",
                           "message": message,
                           "user": user, })

    async def connect(self):
        '''Подключение юзеров'''
        recieve_user = str(self.scope["url_route"]["kwargs"][
                               "user"])  # сюда с фронта передаём имя комнаты для выгрузки сообщения в админ чат
        print(recieve_user, '------->>>connect', 'чью историю подкгружаем в админку')
        user = str(self.scope['user'])  # получаем имя пользователя который подключился с фронта
        r.set(user, self.channel_name)  # записываем в редис имя и channel_name подключенного юзера
        self.room_name = 'go'  # задаем статический румнейм для общего чата
        self.room_group_name = "chat_%s" % self.room_name  # формируем рум груп нейм
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)  # добавляем в группу юзеров
        await self.accept()  # подтверждение
        await self.send_online(0)  # отправляем количество вебсокет подключений на фронт
        if recieve_user == 'go':  # проверка подключение из админки или нет .'go' - это не админка
            await self.send_json(self.channel_name, user)  # выгружает свою историю чата в суппорт чат
        else:
            print('это админка')
            await self.get_all_room()
            await self.send_json(self.channel_name, recieve_user)  # выгружает выбранную историю в админ чат

    async def disconnect(self, code):
        """Отключение пользователя"""
        r.delete(str(self.scope['user']))  # удаляет запись об юзере из редиса при отключении
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)  # убирает юзера из группы
        await self.send_online(-1)  # отправляет онлайн

    async def receive(self, text_data=None, bytes_data=None):
        """Принятие сообщения"""

        text_data_json = json.loads(text_data)
        if text_data_json.get('online') == "online":
            online = self.channel_layer.receive_count
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "get_online",
                                       "get_online": online
                                       }
            )
        if text_data_json.get('bidCount') is not None:
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "get_bid",
                    "bid": text_data_json,
                }
            )
        if text_data_json.get('bet'):
            # expected to have bet like {"bet": {"credits": 1000, "placed": "black"}}
            user = self.scope.get('user')
            if user and user.is_authenticated:
                user_pk = user.pk
                bet = text_data_json.get('bet')
                print(f"receive method in consumers.py: Receiving bet from user({user_pk}): {bet}")
                await self.save_bet(bet, user_pk)
        if text_data_json.get("message") is not None and text_data_json.get("chat_type") is None:
            message = text_data_json.get("message")
            user = text_data_json["user"]
            avatar = text_data_json["avatar"]
            rubin = text_data_json.get("rubin")
            # online = self.channel_layer.receive_count

        '''первичное получение и обработка сообщений'''
        # text_data_json = json.loads(text_data)  # десериализует json
        # print(text_data_json, '------------json support_admin')
        if text_data_json.get('chat_type') == 'support':  # проверяет пришло ли сообщение из support чата
            room = await self.create_or_get_support_chat_room(
                text_data_json.get('user'))  # получает или создает рум в бд
            await self.save_user_message(room, str(self.scope['user']),
                                         text_data_json["message"])  # сохранении сообщение в полученой комнате
            byte_user_channel_name = r.get('admin')  # проверяем есть ли дамин в онлайне(НУЖНО ДОДЕЛАТЬ)
            if byte_user_channel_name:
                user_channel_name = bytes.decode(byte_user_channel_name, encoding='utf-8')  # получаем channel_name админа
                await self.send_support_chat_message(user_channel_name, text_data_json["message"],
                                                 text_data_json["user"])  # отправляем сообщение из супорт чата админу
            await self.send_support_chat_message(self.channel_name, text_data_json["message"], text_data_json[
                "user"])  # отправляем сообщение из супорт чата на сайте себе
        elif text_data_json.get('chat_type') == 'all_chat':
            '''Общий чат на всех страницах. Получаем сообщение и рассылаем его всем'''
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message",
                                       "chat_type": text_data_json.get('chat_type'),
                                       "message": text_data_json["message"],
                                       "user": text_data_json["user"],
                                       "avatar": text_data_json["avatar"],
                                       "rubin": text_data_json.get("rubin"),
                                       })

        elif text_data_json.get('chat_type') == 'support_admin':
            '''Получем сообщение от админа из админки'''

            receive_user = self.scope["url_route"]["kwargs"]["user"]
            print(receive_user, '-------support_admin', 'получатель')
            sender_user = str(self.scope['user'])
            print(sender_user, '-----------support_admin', 'отправитель')
            byte_user_channel_name = r.get(receive_user)  # получаем channel_name юзера из редиса в виде байт строки
            if byte_user_channel_name:
                user_channel_name = bytes.decode(byte_user_channel_name,
                                                 encoding='utf-8')  # преобразуем байт channel_name в строку
                print(user_channel_name, '--------support_chat user_channel_name')
                print(self.channel_name, '--------support_chat self.channel_name')
                await self.send_support_chat_message(user_channel_name, text_data_json["message"],
                                                     sender_user)  # отправка сообщения пользователю из админку
            room = await self.create_or_get_support_chat_room(receive_user)  # получаем комнату с сообщениями
            await self.save_user_message(room, sender_user,
                                         text_data_json["message"])  # сохранении сообщение админа в бд
            await self.send_support_chat_message(self.channel_name, text_data_json["message"],
                                                 sender_user)  # отправка сообщения самому себе в админку

    async def get_online(self, event):
        online = event['get_online']
        await self.send(text_data=json.dumps({
            "get_online": online
        }))

    async def get_rooms(self, event):
        room_name = event.get('room_name')
        await self.send(text_data=json.dumps({
            "room_name": room_name
        }))

    async def chat_message(self, event):
        chat_type = event.get('chat_type')
        user = event.get('user')
        message = event.get("message")
        avatar = event.get("avatar")
        rubin = event.get("rubin")
        # online = event.get("online")
        await self.send(text_data=json.dumps({"message": message,
                                              "chat_type": chat_type,
                                              "user": user,
                                              "avatar": avatar,
                                              "rubin": rubin,
                                              # "online": online
                                              }))
# начинает отсчёт
    async def korney_task(self, event):
        data = event.get('data')
        await self.send(text_data=json.dumps({
            "roulette": 20,
            "data": data
        }))
# начинает крутиться рулетка
    async def rolling(self, event):
        await self.send(text_data=json.dumps({
            "roll": 'rolling',
        }))

    async def stopper(self, event):
        await self.send(text_data=json.dumps({
            "stop": "stopping",
        }))

    async def go_back(self, event):
        await self.send(text_data=json.dumps({
            'back': 'go-back',
        }))

    async def get_bid(self, event):
        data = event.get('bid')
        # amount = event['bidCount']
        await self.send(text_data=json.dumps({
            "bid": data,
        }))

    async def save_bet(self, bet, user_pk):
        storage_name = tasks.KEYS_STORAGE_NAME
        print(f"Saving bet in {storage_name}")
        bet["channel_name"] = self.channel_name
        print(type(self.channel_name))
        print(self.channel_name)
        tasks.save_as_nested.apply_async(args=(storage_name, user_pk, bet))

    async def send_new_level(self, event):
        message = dict()
        message["lvlup"] = event["lvlup"]
        print("send new level")
        await self.send(json.dumps(message))