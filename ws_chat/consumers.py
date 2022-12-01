import base64
import datetime
import json
import os

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

    @sync_to_async()
    def base64_to_image(self, file):
        '''преобразование байт строки в файл и сохранение его'''
        file_type = file.split(';')[0].split('/')[1]
        string_file = file.split(';')[1][7:]
        save_date = datetime.datetime.now()
        byte_file = string_file.encode(encoding='ascii')
        new_file = base64.decodebytes(byte_file)
        user = str(self.scope['user'])
        save_name = f'media/support_chat/{user}/{save_date}.{file_type}'
        try:
            os.mkdir(f'media/support_chat/{user}')
            with open(save_name, 'wb') as f:
                f.write(new_file)
        except:
            with open(save_name, 'wb') as f:
                f.write(new_file)

        return save_name

    @sync_to_async
    def save_user_message(self, room, user, message, file_path=''):  # сохраняет сообщение в бд
        if user:
            user = CustomUser.objects.get(username=user).pk
            user_mess = Message(user_posted_id=user, message=message, file_message=file_path[6:])
            user_mess.save()
            room.message.add(user_mess, bulk=False)
            room.save()
            async_to_sync(self.get_all_room)()
            return user_mess

    @sync_to_async()
    def get_all_room(self):
        '''отправляет комнаты в админ чат при коннекте или при появлении нового сообщения'''
        try:
            rooms = UserChatRoom.objects.all()
            serializer = OnlyRoomSerializer(rooms, many=True)
            room_list = []
            for i in serializer.data:
                room_list.append(i['room_id'])
            async_to_sync(self.channel_layer.group_send)('admin_group', {'type': 'get_rooms', 'room_name': room_list})
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
                async_to_sync(self.channel_layer.send)(channel, {"type": "support_chat_message",
                                                                 "chat_type": "support",
                                                                 "message": i['message'],
                                                                 "user": i['user_posted']['username'],
                                                                 "file_path": i['file_message']
                                                                 })
        except:
            pass

    async def send_support_chat_message(self, channel_name, message, user, file_path=None):
        '''Отправка сообщения в суппорт чат . Аргументы channel_name,message,user '''
        await self.channel_layer.send(
            channel_name, {"type": "support_chat_message",
                           "chat_type": "support",
                           "message": message,
                           "user": user,
                           "file_path": f'/{file_path}'
                           })

    @sync_to_async()
    def get_user_status(self, username):
        '''Проверяет являеться ли пользователь стафом или суперюзером'''
        user = CustomUser.objects.get(username=username)
        if user.is_staff or user.is_superuser:
            return True

    async def connect(self):
        '''Подключение юзеров'''
        connect_chat_room = str(self.scope["url_route"]["kwargs"]["user"])  # имя комнаты
        user = str(self.scope['user'])  # получаем имя пользователя который подключился с фронта
        admin_status = await self.get_user_status(user)
        if admin_status:
            await self.channel_layer.group_add('admin_group', self.channel_name)
        await self.channel_layer.group_add(f'{user}_room', self.channel_name)  # добавляем в группу юзеров
        self.room_name = 'go'  # задаем статический румнейм для общего чата
        self.room_group_name = "chat_%s" % self.room_name  # формируем рум груп нейм
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)  # добавляем в группу юзеров
        await self.accept()  # подтверждение
        await self.send_online(0)  # отправляем количество вебсокет подключений на фронт
        if connect_chat_room == 'go':  # проверка подключение из админки или нет .'go' - это не админка
            await self.send_json(self.channel_name, user)  # выгружает свою историю чата в суппорт чат
        else:
            await self.get_all_room()

    async def disconnect(self, code):
        """Отключение пользователя"""
        await self.channel_layer.group_discard(f'{str(self.scope["user"])}_room', self.channel_name)
        await self.channel_layer.group_discard('admin_group', self.channel_name)
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
        if text_data_json.get('bet') is not None:
            user = self.scope.get('user')
            if user and user.is_authenticated:
                user_pk = user.pk
                bet = text_data_json.get('bet')
                print(f"receive method in consumers.py: Receiving bet from user({user_pk}): {bet}")
                await self.save_bet(bet, user_pk)
            await self.channel_layer.group_send(
                self.room_group_name, {
                    "type": "get_bid",
                    "bid": text_data_json,
                }
            )
        # if text_data_json.get('bet'):
        #     # expected to have bet like {"bet": {"credits": 1000, "placed": "black"}}
        #     user = self.scope.get('user')
        #     if user and user.is_authenticated:
        #         user_pk = user.pk
        #         bet = text_data_json.get('bet')
        #         print(f"receive method in consumers.py: Receiving bet from user({user_pk}): {bet}")
        #         await self.save_bet(bet, user_pk)
        if text_data_json.get("message") is not None and text_data_json.get("chat_type") is None:
            message = text_data_json.get("message")
            user = text_data_json["user"]
            avatar = text_data_json["avatar"]
            rubin = text_data_json.get("rubin")
            # online = self.channel_layer.receive_count

        '''первичное получение и обработка сообщений'''
        if text_data_json.get('chat_type') == 'support':  # сообщение из support чата
            file_path = ''
            if text_data_json.get('file'):
                filed = text_data_json.get('file')
                file_path = await self.base64_to_image(filed)
            user = str(self.scope.get('user'))
            room = await self.create_or_get_support_chat_room(user)  # получает рум из бд
            await self.save_user_message(room, user, text_data_json["message"], file_path)  # сохранение сообщения
            admin_status = await self.get_user_status(user)
            if not admin_status:
                await self.send_support_chat_message(self.channel_name,
                                                     text_data_json["message"],
                                                     user, file_path)  # из супорт чата на сайте себе
            await self.channel_layer.group_send('admin_group', {"type": "support_chat_message",
                                                                "chat_type": "support",
                                                                "message": text_data_json["message"],
                                                                "user": user,
                                                                "file_path": f'/{file_path}'
                                                                })  # отправка сообщения пользователя админам

        elif text_data_json.get('chat_type') == 'support_admin':
            '''Получем сообщение от админа из админки'''
            file_path = ''
            if text_data_json.get('file'):
                filed = text_data_json.get('file')
                file_path = await self.base64_to_image(filed)

            if text_data_json.get('receiver_user_room'):
                receive_user = text_data_json.get('receiver_user_room')
                await self.get_all_room()
                await self.send_json(self.channel_name, receive_user)
            else:
                sender_user = str(self.scope['user'])
                receive = text_data_json.get('receive')
                room = await self.create_or_get_support_chat_room(receive)  # получаем комнату с сообщениями
                await self.save_user_message(room, sender_user,
                                             text_data_json["message"], file_path)  # сохранении сообщение админа в бд
                await self.send_support_chat_message(self.channel_name, text_data_json["message"],
                                                     sender_user, file_path)  # отправка сообщения самому себе в админку
                await self.channel_layer.group_send(f'{receive}_room', {"type": "support_chat_message",
                                                                        "chat_type": "support",
                                                                        "message": text_data_json["message"],
                                                                        "file_path": f'/{file_path}',
                                                                        "user": sender_user, })  # отправка сообщения пользователю в рум


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
        await self.send(text_data=json.dumps({"message": message,
                                              "chat_type": chat_type,
                                              "user": user,
                                              "avatar": avatar,
                                              "rubin": rubin,
                                              # "online": online
                                              }))

    async def support_chat_message(self, event):
        user = event.get('user')
        message = event.get("message")
        file_path = event.get('file_path')
        chat_type = event.get('chat_type')
        await self.send(text_data=json.dumps({"message": message,
                                              "chat_type": chat_type,
                                              "user": user,
                                              "file_path": file_path,
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
        message = event.get('winner')
        await self.send(text_data=json.dumps({
            "stop": "stopping",
            "winner": message,
        }))

    async def go_back(self, event):
        await self.send(text_data=json.dumps({
            'back': 'go-back',
        }))

    async def get_bid(self, event):
        data = event.get('bid')
        # amount = event['bidCount']
        print(data, 'ETO DATA V GET_BID')
        await self.send(text_data=json.dumps({
            "bid": data,
        }))

    async def get_balance(self, event):
        print('send new balance to user')
        message = event.get('balance_update')
        print(message)
        await self.send(text_data=json.dumps(message))

    async def save_as_nested(keys_storage_name: str, dict_key: (str | int), dictionary: dict) -> None:
        """
        Creates a nested structure imitation in redis.

        Args:
            keys_storage_name (str): name of the list where dict_key will be stored;
            dict_key (str|int): name of the key to acces dict;
            dictionary (dict): dict to store.
        """
        async with r.pipeline() as pipe:
            pipe.rpush(keys_storage_name, dict_key)
            pipe.hmset(dict_key, dictionary)
            pipe.execute()
        print(f"Hi from save_as_nested. {r.hgetall(dict_key)}")

    async def save_bet(self, bet, user_pk):
        storage_name = tasks.KEYS_STORAGE_NAME
        print(f"Saving bet in {storage_name}")
        bet["channel_name"] = self.channel_name
        await tasks.save_as_nested(storage_name, user_pk, bet)

    async def send_new_level(self, event):
        """Отправляет по каналу сообщение о новом уровне"""
        message = dict()
        message["lvlup"] = event.get("lvlup")
        print("send new level")
        await self.send(json.dumps(message))

    async def send_rewards(self, event):
        """Отправляет по каналу сообщение о начисленных наградах"""
        message = dict()
        message["rewards"] = event.get("rewards")
        print("send reward")
        await self.send(json.dumps(message))
