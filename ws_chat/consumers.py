import base64
import datetime
import json
import os
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from accaunts.models import CustomUser
from support_chat.models import Message, UserChatRoom
from support_chat.serializers import RoomSerializer, OnlyRoomSerializer
# хранит победную карту текущего раунда
from .tasks import ROUND_RESULT_FIELD_NAME
from . import tasks
# подключаемся к редису
r = redis.Redis()


class ChatConsumer(AsyncWebsocketConsumer):

    @sync_to_async
    def create_or_get_support_chat_room(self, user):  # получает или создает чат рум
        chat_room, created = UserChatRoom.objects.get_or_create(room_id=user)
        return chat_room

    async def save_user_message_all_chat(self, all_chat_message):
        """Cохраняет последние 1-50 сообщений из общего чата в Редис"""
        if r.llen("all_chat_50") == 50:
            r.lpop("all_chat_50")
        r.rpush("all_chat_50", json.dumps(all_chat_message))

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
        """Cохраняет сообщения из чата поддержки в БД"""
        if user:
            try:
                user = CustomUser.objects.get(username=user).pk
                user_mess = Message(user_posted_id=user, message=message)
                user_mess.full_clean()
                user_mess.save()
                room.message.add(user_mess, bulk=False)
                return user_mess
            except ValidationError:
                print("Message support_chat more 500")

    @sync_to_async()
    def get_all_room(self):
        """Отправляет комнаты в админ чат при коннекте или при появлении нового сообщения"""
        try:
            rooms = UserChatRoom.objects.all()
            serializer = OnlyRoomSerializer(rooms, many=True)
            room_list = []
            for i in serializer.data:
                room_list.append(i['room_id'])
            async_to_sync(self.channel_layer.group_send)('admin_group',
                                                         {
                                                             'type': 'get_rooms',
                                                             'room_name': room_list
                                                          })
        except:
            print('error get_all_room')

    async def send_online(self, num):
        """Отправка онлайна при коннекте и дисконнекте пользователя"""
        online = self.channel_layer.receive_count + num
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "get_online",
            "get_online": online
        })

    async def init_users_chat(self, channel):
        """Отправляет историю сообщений(до 50шт) общего чата, выгружая её из Редиса"""
        message_with_list = []
        for message in r.lrange("all_chat_50", 0, 49):
            message_with_list.append(json.loads(message))
        await self.channel_layer.send(channel, {"type": "chat_message",
                                                "chat_type": "all_chat_list",
                                                "message": "list",
                                                "list": message_with_list,
                                                })

    @sync_to_async()
    def init_support_chat(self, channel, room_name):
        """Отправка истории сообщений в чат поддержки"""
        try:
            room_data = UserChatRoom.objects.get(room_id=room_name)  # получаем комнату
            serializer = RoomSerializer(room_data)  # сериализуем ее
            async_to_sync(self.channel_layer.send)(channel, {"type": "support_chat_message",
                                                                 "chat_type": "support",
                                                                 "list_message": serializer.data.get('message')})
        except:
            pass

    async def send_support_chat_message(self, channel_name, message, user, file_path=None):
        """Отправка сообщения в суппорт чат . Аргументы channel_name,message,user """
        await self.channel_layer.send(
            channel_name, {"type": "support_chat_message",
                           "chat_type": "support",
                           "message": message,
                           "user": user,
                           "file_path": f'/{file_path}'
                           })

    @sync_to_async()
    def eval_xp_and_lvl(self, user):
        """
        Отправляет информацию об уровне пользователя.
        Рассчитывает в процентах сколько опыта у пользователя для данного уровня
        """
        max_exp = user.level.experience_range.upper
        min_exp = user.level.experience_range.lower
        delta_exp = max_exp - min_exp
        exp = user.experience
        percent_exp_line = (exp - min_exp) / (delta_exp / 100)
        message = {
            "lvlup": {
                "new_lvl": user.level.level + 1,
                "levels": user.level.level},
            "expr": {
                        "start": min_exp,
                        "end": max_exp,
                        "percent": percent_exp_line,
                    }}
        return message

    async def send_lvl_and_exp(self, event):
        """Отправляет уровень и опыт пользователю при подключении"""
        user = self.scope['user']
        if not user.is_authenticated:
            return
        else:
            message = await self.eval_xp_and_lvl(user)
            await self.send(text_data=json.dumps(message))

    async def connect(self):
        """Подключение пользователя"""
        recieve_user = str(self.scope["url_route"]["kwargs"][
                               "user"])  # сюда с фронта передаём имя комнаты для выгрузки сообщения в админ чат
        user = str(self.scope['user'])  # TODO получаем имя пользователя который подключился с фронта
        if self.scope['user'].is_authenticated:
            if self.scope['user'].is_staff:
                await self.channel_layer.group_add('admin_group', self.channel_name)
            else:
                await self.channel_layer.group_add(f'{user}_room', self.channel_name)  # TODO добавляем в группу юзеров
        self.room_name = 'go'  # задаем статический румнейм для общего чата
        self.room_group_name = "chat_%s" % self.room_name  # формируем рум груп нейм
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)  # добавляем в группу юзеров
        await self.accept()
        await self.channel_layer.send(self.channel_name, {
            "type": 'roulette_countdown_state',
        })
        # подтверждение
        await self.send_online(0)  # TODO:отправляем количество вебсокет подключений на фронт
        if recieve_user == 'go':  # проверка подключение из админки или нет. 'go' - это не админка
            # выгружает свою историю чата поддержки
            await self.init_support_chat(self.channel_name, user)  # TODO: должен выгружать только на странице чата поддержки, в суппорт чат
            await self.init_users_chat(self.channel_name)
        else:
            await self.get_all_room()
        await self.channel_layer.send(self.channel_name, {
            "type": "send_lvl_and_exp"
        })

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
        if text_data_json.get("message") is not None and text_data_json.get("chat_type") is None:
            message = text_data_json.get("message")
            user = text_data_json["user"]
            avatar = text_data_json["avatar"]
            rubin = text_data_json.get("rubin")
            # online = self.channel_layer.receive_count

        '''первичное получение и обработка сообщений'''
        if text_data_json.get('chat_type') == 'support':  # сообщение из support чата
            if len(text_data_json.get("message")) > 500:
                print("message all_chat more 500")
            else:
                file_path = ''
                if text_data_json.get('file'):
                    filed = text_data_json.get('file')
                    file_path = await self.base64_to_image(filed)
                user = str(self.scope.get('user'))
                room = await self.create_or_get_support_chat_room(user)  # получает рум из бд
                # сохранение сообщения
                await self.save_user_message(room, user, text_data_json["message"], file_path)
                if not self.scope.get('user').is_staff:
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
                await self.init_support_chat(self.channel_name, receive_user)
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
            all_chat_message = {"type": "chat_message",
                                "chat_type": text_data_json.get('chat_type'),
                                "message": text_data_json["message"],
                                "user": text_data_json["user"],
                                "avatar": text_data_json["avatar"],
                                "rubin": text_data_json.get("rubin"),
                                }
            if len(all_chat_message["message"]) <= 250:
                await self.channel_layer.group_send(self.room_group_name, all_chat_message)
                await self.save_user_message_all_chat(all_chat_message)

    async def get_online(self, event):
        """Получение онлайна для нового юзера"""
        online = event['get_online']
        t = datetime.datetime.now()
        await self.send(text_data=json.dumps({
            "get_online": online,
            "time": str(int(t.timestamp() * 1000))
        }))

    async def get_rooms(self, event):
        room_name = event.get('room_name')
        await self.send(text_data=json.dumps({
            "room_name": room_name
        }))

    async def chat_message(self, event):
        """Общий чат - обмен сообщениями"""
        chat_type = event.get('chat_type')
        user = event.get('user')
        message = event.get("message")
        avatar = event.get("avatar")
        rubin = event.get("rubin")
        list = event.get('list')
        await self.send(text_data=json.dumps({"message": message,
                                              "chat_type": chat_type,
                                              "user": user,
                                              "avatar": avatar,
                                              "rubin": rubin,
                                              "list": list
                                              }))

    async def support_chat_message(self, event):
        list_message = event.get('list_message')
        user = event.get('user')
        message = event.get("message")
        file_path = event.get('file_path')
        chat_type = event.get('chat_type')
        await self.send(text_data=json.dumps({"message": message,
                                              "list_message":list_message,
                                              "chat_type": chat_type,
                                              "user": user,
                                              "file_path": file_path,
                                              }))

    async def roulette_countdown_starter(self, event):
        """Начинает отсчёт рулетки"""
        curr_round = event.get('round')
        await self.send(text_data=json.dumps({
            "roulette": 20,
            "round": curr_round,
        }))

    # начинает крутиться рулетка
    async def rolling(self, event):
        """Начинает прокрутку рулетки"""
        winner = event.get('winner')
        print(winner)
        await self.send(text_data=json.dumps({
            "roll": 'rolling',
            "winner": winner,
        }))

    async def stopper(self, event):
        """Сигнализирует об остановке прокрутки рулетки"""
        winner = event.get('winner')
        await self.send(text_data=json.dumps({
            "stop": "stopping",
            "w": winner,
        }))

    async def go_back(self, event):
        """Откатывает рулетку на первоначальное состояние"""
        await self.send(text_data=json.dumps({
            'back': 'go-back',
        }))

    async def get_bid(self, event):
        """Обрабатывает ставки пользователей"""
        data = event.get('bid')
        await self.send(text_data=json.dumps({
            "bid": data,
        }))

    async def get_balance(self, event):
        """Отправляет изменения баланса пользователя"""
        message = event.get('balance_update')
        await self.send(text_data=json.dumps(message))

    # async def save_as_nested(keys_storage_name: str, dict_key: (str | int), dictionary: dict) -> None:
    #     """
    #     Creates a nested structure imitation in redis.
    #
    #     Args:
    #         keys_storage_name (str): name of the list where dict_key will be stored;
    #         dict_key (str|int): name of the key to acces dict;
    #         dictionary (dict): dict to store.
    #     """
    #     async with r.pipeline() as pipe:
    #         pipe.rpush(keys_storage_name, dict_key)
    #         pipe.hmset(dict_key, dictionary)
    #         pipe.execute()


    async def save_bet(self, bet, user_pk):
        storage_name = tasks.KEYS_STORAGE_NAME
        print(f"Saving bet in {storage_name}")
        bet["channel_name"] = self.channel_name
        await tasks.save_as_nested(storage_name, user_pk, bet)

    async def init_xp_and_lvl(self, event):
        message = event
        print(message)
        await self.send(json.dumps(message))

    async def send_new_level(self, event):
        """Отправляет по каналу сообщение о новом уровне"""
        message = dict()
        message["lvlup"] = event.get("lvlup")
        message['expr'] = event.get("expr")
        await self.send(json.dumps(message))

    async def send_rewards(self, event):
        """Отправляет по каналу сообщение о начисленных наградах"""
        message = dict()
        message["rewards"] = event.get("rewards")
        await self.send(json.dumps(message))

    async def roulette_countdown_state(self, event):
        """Отправляет новому клиенту состояние рулетки при уже начавшемся отсчёте"""
        state = r.get('state')

        t = r.get('start:time')
        message = {'init': {"state": state.decode('utf-8'),
                            "t": str(t.decode('utf-8'))}
                   }
        if state.decode('utf-8') == 'rolling':
            round_result = r.get(ROUND_RESULT_FIELD_NAME).decode("utf-8")
            message['init']['winner'] = round_result
        await self.send(json.dumps(message))
