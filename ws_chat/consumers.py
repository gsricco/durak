import base64
import datetime
import json
import os
from random import choices
from caseapp.serializers import OwnedCaseTimeSerializer, ItemSerializer, ItemForUserSerializer, OwnedCaseSerializer, \
    ItemForCaseSerializer, CaseAndCaseItemSerializer
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ValidationError
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
import redis
from django.shortcuts import get_object_or_404

from accaunts.models import CustomUser, Ban
from configs.settings import BASE_DIR
from accaunts.models import CustomUser, Level, ItemForUser
from caseapp.models import OwnedCase, Case, ItemForCase, Item
from support_chat.models import Message, UserChatRoom
from support_chat.serializers import RoomSerializer, OnlyRoomSerializer
# хранит победную карту текущего раунда
from .tasks import ROUND_RESULT_FIELD_NAME
from . import tasks
# подключаемся к редису
r = redis.Redis(encoding="utf-8", decode_responses=True)

from django.contrib.auth.decorators import user_passes_test


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
        """Преобразование байт строки в файл и сохранение его"""
        file_type = file.split(';')[0].split('/')[1]
        string_file = file.split(';')[1][7:]
        save_date = datetime.datetime.now()
        byte_file = string_file.encode(encoding='ascii')
        new_file = base64.decodebytes(byte_file)
        user = self.scope['user']
        save_name = f'media/support_chat/{user.pk}/{save_date}.{file_type}'
        if os.path.isdir(f'{BASE_DIR}/media/support_chat'):
            print('in if$1')
            if os.path.isdir(f'{BASE_DIR}/media/support_chat/{user.pk}'):
                print('in if$2')
                with open(save_name, 'wb') as f:
                    f.write(new_file)
            else:
                print('in else$2')
                os.mkdir(f'media/support_chat/{user.pk}')
                with open(save_name, 'wb') as f:
                    f.write(new_file)
        else:
            print('in else$1')
            os.mkdir('media/support_chat')
            os.mkdir(f'media/support_chat/{user.pk}')
            with open(save_name, 'wb') as f:
                f.write(new_file)
        return save_name

    @sync_to_async
    def save_user_message(self, room, user, message, file_path=''):  # сохраняет сообщение в бд
        """Cохраняет сообщения из чата поддержки в БД"""
        if user:
            user = CustomUser.objects.get(username=user).pk
            user_mess = Message(user_posted_id=user, message=message, file_message=file_path[6:])
            # user_mess.full_clean()
            user_mess.save()
            room.message.add(user_mess, bulk=False)
            room.save()
            async_to_sync(self.get_all_room)()
            return user_mess

    @sync_to_async()
    def get_all_room(self):
        """Отправляет комнаты в админ чат при коннекте или при появлении нового сообщения"""
        if UserChatRoom.objects.all().exists():
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
        # else:
        #     print('error get_all_room')

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
        if UserChatRoom.objects.filter(room_id=room_name).exists():
            room_data = UserChatRoom.objects.get(room_id=room_name)  # получаем комнату
            serializer = RoomSerializer(room_data)  # сериализуем ее
            async_to_sync(self.channel_layer.send)(channel, {"type": "support_chat_message",
                                                             "chat_type": "support",
                                                             "list_message": serializer.data.get('message')})



    @sync_to_async()
    def get_ban_chat_user(self, user):
        """Проверка бана пользователя в общем чате"""
        user = CustomUser.objects.get(username=user).pk
        try:
            if get_object_or_404(Ban, user=user).ban_chat:
                return True
            else:
                return False
        except:
            return False

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
        # last_level = Level.objects.last()
        # max_level_number = last_level.level
        # max_level_exp = last_level.experience_range.upper
        current_level = user.level.level
        max_exp = user.level.experience_range.upper
        min_exp = user.level.experience_range.lower
        delta_exp = max_exp - min_exp
        exp = user.experience
        percent_exp_line = (exp - min_exp) / (delta_exp / 100)
        message = {}

        if Level.objects.filter(level=current_level + 1).exists():
            next_lvl = Level.objects.get(level=current_level + 1)
            message = {
                "lvlup": {
                    "new_lvl": next_lvl.level,
                    "levels": current_level,
                },
                "expr": {
                    "current_exp": exp,
                    "max_current_lvl_exp": user.level.experience_range.upper,
                    "percent": percent_exp_line,
                },
                "lvl_info": {
                    'cur_lvl_img': user.level.img_name,
                    'cur_lvl_case_count': user.level.amount,
                    'next_lvl_img': next_lvl.img_name,
                    'next_lvl_case_count': next_lvl.amount,
                }
            }

        else:
            if Level.objects.filter(level=current_level - 1).exists():
                previous_lvl = Level.objects.get(level=current_level - 1)
                message = {"lvlup": {
                    "new_lvl": current_level,
                    "levels": previous_lvl.level,
                },
                    "expr": {
                        "current_exp": previous_lvl.experience_range.upper,
                        "max_current_lvl_exp": previous_lvl.experience_range.upper,
                        "percent": 100,
                    },
                    "lvl_info": {
                        'max_lvl': True,
                        'cur_lvl_img': previous_lvl.img_name,
                        'cur_lvl_case_count': previous_lvl.amount,
                        'next_lvl_img': user.level.img_name,
                        'next_lvl_case_count': user.level.amount,
                    }
                }
        return message

    async def send_lvl_and_exp(self, event):
        """Отправляет уровень и опыт пользователю при подключении"""
        user = self.scope['user']
        if not user.is_authenticated:
            return
        else:
            message = await self.eval_xp_and_lvl(user)
            await self.send(text_data=json.dumps(message))
    async def send_task_lvl_and_exp(self, event):
        """Отправляет уровень и опыт пользователю при подключении"""
        message = {}
        message['lvlup'] = event.get('lvlup')
        message['expr'] = event.get('expr')
        message['lvl_info'] = event.get('lvl_info')
        await self.send(text_data=json.dumps(message))
    @sync_to_async()
    def get_cases_info(self):
        '''функция отправки информации о кейсах'''
        # поулчаем все выданные и не открытые кейсы
        users = self.scope['user']
        owned_cases_for_user = OwnedCase.objects.filter(owner=users.pk)
        not_owned_case = owned_cases_for_user.filter(date_opened=None)
        # получаем все имена кейсов из бд и делаем из них дикт
        all_case_name = Case.objects.all()
        case_count_for_name = {}
        for case_name in all_case_name:
            # case_item_series = ItemForCaseSerializer(case_name.itemforcase_set.all(), many=True)
            case_count_for_name[case_name.name] = {'count': 0,
                                                   'open_lvl': case_name.user_lvl_for_open,
                                                   # 'case_info': case_item_series.data
                                                   }

        # подсчитываем сколько каких кейсов есть у юзера
        for case in not_owned_case:
            case_count_for_name[str(case.case)]['count'] += 1
        last_open_owned_case = owned_cases_for_user.exclude(date_opened=None).order_by("-date_opened").first()
        case_time = {'date_opened': '', 'seconds_since_prev_open': 3600, 'can_be_opened': True}
        if last_open_owned_case:
            serializer = OwnedCaseTimeSerializer(last_open_owned_case)
            case_time = serializer.data
        message = {'cases': {'open_time': case_time, 'user_cases': case_count_for_name}}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "send_cases_info",
                                   "cases": message
                                   })

    @sync_to_async()
    def get_items_for_cases(self):
        cases_items = Case.objects.all()
        serializer = CaseAndCaseItemSerializer(cases_items, many=True)
        message = {}
        for case in serializer.data:
            message[case['name']] = {'image': case['image'],
                                     'items': case['itemforcase_set']
                                     }
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "send_cases_items",
                                   "cases_items": message
                                   })

    @sync_to_async()
    def get_user_items(self):
        '''Send user item functions'''
        user = self.scope['user']
        if user.is_authenticated:
            user_items = ItemForUser.objects.filter(user=user)
            serializer = ItemForUserSerializer(user_items, many=True)
            message = {
                'type': 'send_user_item',
                'user_items': serializer.data
            }
            async_to_sync(self.channel_layer.send)(self.channel_name, message)

    @sync_to_async()
    def open_case(self, case):
        '''Open case function'''
        user = self.scope['user']
        case_id = Case.objects.filter(name=case).first()
        if case_id:
            owned_case = OwnedCase.objects.filter(owner=user.pk) \
                .filter(date_opened=None) \
                .filter(case=case_id) \
                .last()
            if owned_case:
                if owned_case.owner.pk != user.pk:
                    print({"details": "Access forbidden"})

                if owned_case.item is not None:
                    print({"details": "Case is already opened"})

                last_user_case = OwnedCase.objects.filter(owner_id=user.pk) \
                    .exclude(date_opened=None) \
                    .order_by("-date_opened") \
                    .first()

                if last_user_case is not None:
                    delta_time = datetime.datetime.now(datetime.timezone.utc) - last_user_case.date_opened
                    if delta_time < datetime.timedelta(hours=1):
                        print({"details": "Wait before you can open next case"})

                case = owned_case.case
                case_items = ItemForCase.objects.filter(case=case)
                weights = [float(item['chance']) for item in case_items.values('chance')]
                print(weights, 'веса итема')
                chosen_item_in_case = choices(case_items, weights=weights, k=1)[0]
                print(chosen_item_in_case)
                chosen_item = Item.objects.get(pk=chosen_item_in_case.item.pk)
                owned_case.item = chosen_item
                # сохраняет время открытия кейса
                # owned_case.date_opened = datetime.datetime.now()
                # время открытия для тестов - 1ч
                # owned_case.date_opened = datetime.datetime.now() - datetime.timedelta(seconds=3400)
                owned_case.save()
                # отправляет результат рандома открытия кейса
                async_to_sync(self.channel_layer.send)(self.channel_name, {'type': 'case_roll',
                                                                           'case_roll_result': chosen_item.name
                                                                           })
                # отправляет пользователю всё предметы
                # async_to_sync(self.get_user_items)()
                # проверка является ли выпавший предмет деньгами
                # если да пополняет баланс , если нет добавляет предмет в инвентарь
                if chosen_item.is_money:
                    user.detailuser.balance += chosen_item.selling_price
                    user.detailuser.save()
                    print('это бабки')
                    async_to_sync(self.channel_layer.send)(self.channel_name, {
                        'type': 'get_balance',
                        'balance_update': {
                            'current_balance': user.detailuser.balance
                        }
                    })
                else:
                    ItemForUser.objects.create(user=user, user_item=chosen_item)
            else:
                print('Нет выданного кейса')
        else:
            print('Нет такого кейса')

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
        if text_data_json.get('get_cases_items'):
            await self.get_items_for_cases()
        # получение предметов в инвентарь
        if text_data_json.get('item'):
            await self.get_user_items()
        # кнопка открытия кейса
        if text_data_json.get('open_case'):
            this_case = text_data_json.get('open_case')
            await self.open_case(this_case)
            await self.get_user_items()
            await self.get_cases_info()
        # информация о кейсах
        if text_data_json.get('cases'):
            await self.get_cases_info()

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
                room = await self.create_or_get_support_chat_room(user)
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
            '''Общий чат на всех страницах. Получаем сообщение и рассылаем его всем.
            Проводим проверку на длинну сообщения не более 250 символов.
            Проводим проверку на бан пользователя.'''
            all_chat_message = {"type": "chat_message",
                                "chat_type": text_data_json.get('chat_type'),
                                "message": text_data_json["message"],
                                "user": text_data_json["user"],
                                "avatar": text_data_json["avatar"],
                                "rubin": text_data_json.get("rubin"),
                                }
            if len(all_chat_message["message"]) <= 250:
                if await self.get_ban_chat_user(text_data_json["user"]):
                    print("user is banned ===", all_chat_message)
                    await self.send(text_data=json.dumps(all_chat_message))

                else:
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
                                              "list_message": list_message,
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
            "c": event.get('c'),
            "p": event.get('p')
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
            'previous_rolls': event.get('previous_rolls'),
        }))

    async def get_bid(self, event):
        """Обрабатывает ставки пользователей"""
        data = event.get('bid')
        await self.send(text_data=json.dumps({
            "bid": data,
            "from_json": r.json().get('round_bets')
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
        message = {'init': {"state": state,
                            "t": str(t),
                            "previous_rolls": r.json().get('last_winners'),
                            }
                   }
        if state == 'rolling':
            round_result = r.get(ROUND_RESULT_FIELD_NAME)
            message['init']['winner'] = round_result
        await self.send(json.dumps(message))

    async def send_cases_info(self, event):
        """Отправляет по каналу сообщение о кейсах"""
        message = dict()
        message["cases"] = event.get("cases").get('cases')
        await self.send(json.dumps(message))

    async def send_cases_items(self, event):
        """Отправляет по каналу сообщение о кейсах"""
        message = dict()
        message["cases_items"] = event.get("cases_items")
        await self.send(json.dumps(message))

    async def send_user_item(self, event):
        """Отправляет по каналу сообщение о кейсах"""
        message = dict()
        message["user_items"] = event.get("user_items")
        await self.send(json.dumps(message))

    async def case_roll(self, event):
        """Отправляет результат выпадения кейса"""
        message = dict()
        message["case_roll_result"] = event.get("case_roll_result")
        await self.send(json.dumps(message))
