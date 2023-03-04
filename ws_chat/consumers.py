import asyncio
import base64
import datetime
import json
import os
import threading
from random import choices

import redis
from asgiref.sync import async_to_sync, sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accaunts.models import (AvatarProfile, Ban, CustomUser, DetailUser,
                             FreeBalanceHistory, ItemForUser, Level, UserBet,
                             UserBonus)
from caseapp.models import Case, Item, ItemForCase, OwnedCase
from caseapp.serializers import (CaseAndCaseItemSerializer,
                                 ItemForUserSerializer,
                                 OwnedCaseTimeSerializer)
from configs.settings import BASE_DIR, REDIS_PASSWORD, REDIS_URL_STACK
from content_manager.models import BadSlang
from pay.views import rub_to_pay, virtual_money_to_rub
from support_chat.models import Message, UserChatRoom
from support_chat.serializers import OnlyRoomSerializer, RoomSerializer

from . import tasks
# хранит победную карту текущего раунда
from .tasks import ROUND_RESULT_FIELD_NAME
from .utils import check_youtube_subscribers, vk_subscribe

# подключаемся к редису
r = redis.Redis(encoding="utf-8", decode_responses=True, host=REDIS_URL_STACK, password=REDIS_PASSWORD)


class ChatConsumer(AsyncWebsocketConsumer):

    @sync_to_async
    def get_not_read(self, room):
        room.notread.save()
        return room.notread.not_read_owner_counter

    @sync_to_async
    def create_or_get_support_chat_room(self, user_pk):
        chat_room, created = UserChatRoom.objects.get_or_create(user_id=user_pk, room_id=user_pk)
        return chat_room

    async def save_user_message_all_chat(self, all_chat_message):
        """Сохраняет последние 1-50 сообщений из общего чата в Редис"""
        if not r.exists("all_chat_50"):
            r.json().set("all_chat_50", ".", [])
        r.json().arrappend("all_chat_50", ".", all_chat_message)
        if (arr_len := r.json().arrlen("all_chat_50")) > 50:
            r.json().arrtrim("all_chat_50", ".", arr_len - 50, -1)
        # r.expire("all_chat_50", datetime.timedelta(hours=48))

    @sync_to_async()
    def base64_to_image(self, file):
        """Преобразование байт строки в файл и сохранение его"""
        content_type = file.split(';')[0].split('/')[0]
        if content_type == 'data:image':
            file_type = file.split(';')[0].split('/')[1]
            string_file = file.split(';')[1][7:]
            save_date = datetime.datetime.now()
            byte_file = string_file.encode(encoding='ascii')
            new_file = base64.decodebytes(byte_file)
            user = self.scope['user']
            save_name = f'media/support_chat/{user.pk}/{save_date}.{file_type}'
            if os.path.isdir(f'{BASE_DIR}/media/support_chat'):
                if os.path.isdir(f'{BASE_DIR}/media/support_chat/{user.pk}'):
                    with open(save_name, 'wb') as f:
                        f.write(new_file)
                else:
                    os.mkdir(f'media/support_chat/{user.pk}')
                    with open(save_name, 'wb') as f:
                        f.write(new_file)
            else:
                os.mkdir('media/support_chat')
                os.mkdir(f'media/support_chat/{user.pk}')
                with open(save_name, 'wb') as f:
                    f.write(new_file)
            return save_name
        else:
            return ''

    @sync_to_async
    def save_user_message(self, room, user_id, message, file_path='', is_sell_item=False):
        """Сохраняет сообщения из чата поддержки в БД"""
        user_mess = Message(user_posted_id=user_id, message=message,
                            file_message=file_path[6:], is_sell_item=is_sell_item)
        user_mess.save()
        room.message.add(user_mess, bulk=False)
        room.save()
        room.notread.save()
        async_to_sync(self.get_all_room)()
        return user_mess

    @sync_to_async()
    def get_all_room(self):
        """Отправляет комнаты в админ чат при коннекте или при появлении нового сообщения"""
        if UserChatRoom.objects.all().exists():
            rooms = UserChatRoom.objects.all()
            serializer = OnlyRoomSerializer(rooms, many=True)
            async_to_sync(self.channel_layer.group_send)('admin_group',
                                                         {'type': 'get_rooms',
                                                          'room_data': serializer.data
                                                          })

    async def set_online(self, is_auth: bool, incr: bool = True):
        """Отправка онлайна при коннекте и дисконнекте пользователя"""
        if is_auth:
            if incr:
                r.sadd("online", self.scope["user"].id)
                # r.expire("online", 86400)
            else:
                r.srem("online", self.scope["user"].id)
        online = r.scard("online")
        if staff := self.scope["user"].is_staff:
            await self.channel_layer.group_send('admin_group', {
                "type": "get_online",
                "get_online": online,
                "staff": staff
            })
        # else:
        if r.exists("fake_online"):
            online = r.get("fake_online")
        await self.channel_layer.group_send(self.room_group_name, {
            "type": "get_online",
            "get_online": online
        })

    async def init_users_chat(self, channel):
        """Отправляет историю сообщений(до 50шт) общего чата, выгружая её из Редиса"""
        message_with_list = r.json().get("all_chat_50")
        await self.channel_layer.send(channel, {"type": "chat_message",
                                                "chat_type": "all_chat_list",
                                                "message": "list",
                                                "list": message_with_list,
                                                })

    @sync_to_async()
    def init_support_chat(self, room_name):
        """Отправка истории сообщений в чат поддержки"""
        if UserChatRoom.objects.filter(room_id=room_name).exists():
            room_data = UserChatRoom.objects.get(room_id=room_name)  # получаем комнату
            serializer = RoomSerializer(room_data)  # сериализуем ее
            async_to_sync(self.channel_layer.send)(self.channel_name, {"type": "support_chat_message",
                                                                       "chat_type": "support",
                                                                       "list_message": serializer.data.get('message')})

    @sync_to_async
    def check_last_visit(self, user_id):
        if user_id:
            messages = Message.objects.filter(chat_room__user_id=user_id,
                                              date__gte=timezone.now() - datetime.timedelta(days=2)) \
                .only('date')
            if messages:
                return True
        return False

    @sync_to_async()
    def check_total_transactions(self, user):
        """Проверяет кол-во транзакций пользователя - если меньше 3000_000 то не даёт писать в чат"""
        all_user_bets = UserBet.objects.filter(user=user).aggregate(total_bets=Sum('sum')).get('total_bets')
        if all_user_bets:
            if all_user_bets >= 3000000:
                return False
        return True

    @sync_to_async()
    def get_ban_chat_user(self, user):
        """Проверка бана пользователя в общем чате"""
        if Ban.objects.get(user=user).ban_chat:
            return True
        else:
            return False

    @sync_to_async()
    def add_user_to_chat_ban(self, user_id):
        """Устанавливает юзеру бан общего чата"""
        user_to_ban = Ban.objects.get(user_id=user_id)
        user_to_ban.ban_chat = True
        user_to_ban.save()

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
                    'max_lvl': True,
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
        message = dict()
        message['lvlup'] = event.get('lvlup')
        message['expr'] = event.get('expr')
        message['lvl_info'] = event.get('lvl_info')
        await self.send(text_data=json.dumps(message))

    @sync_to_async()
    def get_cases_info(self, user):
        """Функция отправки информации о кейсах"""
        # поулчаем все выданные и не открытые кейсы
        owned_cases_for_user = OwnedCase.objects.filter(owner=user.pk)
        not_owned_case = owned_cases_for_user.filter(date_opened=None)
        # получаем все имена кейсов из бд и делаем из них дикт
        all_case_name = Case.objects.all()
        case_count_for_name = {}
        for case_name in all_case_name:
            # case_item_series = ItemForCaseSerializer(case_name.itemforcase_set.all(), many=True)
            case_count_for_name[case_name.name] = {
                'count': 0,
                'open_lvl': case_name.user_lvl_for_open,
                # 'case_info': case_item_series.data
            }

        # подсчитываем сколько каких кейсов есть у юзера
        for case in not_owned_case:
            case_count_for_name[str(case.case)]['count'] += 1
        last_open_owned_case = owned_cases_for_user.exclude(date_opened=None).order_by("-date_opened").first()
        case_time = {'date_opened': '', 'seconds_since_prev_open': 3600, 'can_be_opened': True}
        if owned_cases_for_user.exclude(date_opened=None).order_by("-date_opened").exists():
            serializer = OwnedCaseTimeSerializer(last_open_owned_case)
            case_time = serializer.data
        message = {'cases': {'open_time': case_time, 'user_cases': case_count_for_name}}
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": "send_cases_info",
                "cases": message
            }
        )

    @sync_to_async()
    def get_items_for_cases(self):
        cases_items = Case.objects.all()
        serializer = CaseAndCaseItemSerializer(cases_items, many=True)
        message = dict()
        for case in serializer.data:
            message[case['name']] = {
                'image': case['image'],
                'items': case['itemforcase_set'],
            }
        async_to_sync(self.channel_layer.group_send)(
            self.unique_room_name, {
                "type": "send_cases_items",
                "cases_items": message,
            }
        )

    @sync_to_async()
    def get_user_items(self, user):
        """Шлёт кейсы пользователям"""
        user_items = ItemForUser.objects.filter(user=user, is_used=False)
        serializer = ItemForUserSerializer(user_items, many=True)
        message = {
            'type': 'send_user_item',
            'user_items': serializer.data
        }
        async_to_sync(self.channel_layer.group_send)(self.unique_room_name, message)

    @sync_to_async()
    def open_case(self, case, user):
        """Открывает кейсы"""
        if case_id := Case.objects.filter(name=case).first():
            if owned_case := OwnedCase.objects.filter(owner=user.pk) \
                    .filter(date_opened=None).filter(case=case_id).last():
                last_user_case = OwnedCase.objects.filter(owner_id=user.pk) \
                    .exclude(date_opened=None) \
                    .order_by("-date_opened") \
                    .first()
                if last_user_case is not None:
                    delta_time = datetime.datetime.now(datetime.timezone.utc) - last_user_case.date_opened
                case = owned_case.case
                case_items = ItemForCase.objects.filter(case=case)
                weights = [float(item['chance']) for item in case_items.values('chance')]
                chosen_item_in_case = choices(case_items, weights=weights, k=1)[0]
                chosen_item = Item.objects.get(pk=chosen_item_in_case.item.pk)
                owned_case.item = chosen_item
                # сохраняет время открытия кейса
                owned_case.date_opened = datetime.datetime.now()
                # owned_case.date_opened = datetime.datetime.now() - datetime.timedelta(seconds=3585)
                owned_case.save()
                async_to_sync(self.channel_layer.group_send)(self.unique_room_name, {
                    'type': 'case_roll',
                    'case_roll_result': chosen_item.name
                })
                # проверка является ли выпавший предмет деньгами
                # если да пополняет баланс, если нет добавляет предмет в инвентарь
                if chosen_item.is_money:
                    ItemForUser.objects.create(user=user, user_item=chosen_item, is_money=True, is_used=True)
                    user.detailuser.balance += chosen_item.selling_price
                    user.detailuser.save()
                    tasks.send_balance_delay(user.pk)
                else:
                    ItemForUser.objects.create(user=user, user_item=chosen_item)
                    tasks.send_items_delay(user.pk)

    @sync_to_async
    def sell_item(self, data, user):
        if Item.objects.filter(name=data.get('name')).exists():
            item = Item.objects.get(name=data.get('name'))
            if user_item := ItemForUser.objects.filter(user_item=item, user=user, is_used=False).first():
                user_item.is_used = True
                user_item.save()
                user.detailuser.balance += item.selling_price
                user.detailuser.save()
                message = {
                    'type': 'get_balance',
                    'balance_update': {
                        'current_balance': user.detailuser.balance
                    }
                }
                async_to_sync(self.get_user_items)(user)
                if user.is_staff:
                    async_to_sync(self.channel_layer.group_send)(f'admin_group', message)
                else:
                    async_to_sync(self.channel_layer.group_send)(f'{user.id}_room', message)

    @sync_to_async
    def forward_item(self, data):
        user = self.scope['user']
        if user.is_authenticated:
            if item := Item.objects.filter(name=data.get('item_name')).first():
                if user_item := ItemForUser.objects.filter(user_item=item, user=user, is_used=False).first():
                    user_item.is_used = True
                    user_item.is_forwarded = True
                    user_item.save()
                    async_to_sync(self.get_user_items)(user)
                    durak_username = data.get('durak_username')
                    item_name = data.get('item_name')
                    svg_name = data.get('item_image')
                    message = {
                        'type': 'support_chat_message',
                        'chat_type': 'support',
                        'user': user.username,
                        'message': f'{durak_username};{item_name};{svg_name}',
                        'is_sell_item': True
                    }

                    room = async_to_sync(self.create_or_get_support_chat_room)(user.pk)
                    async_to_sync(self.save_user_message)(room, user.id, f'{durak_username};{item_name};{svg_name}',
                                                          is_sell_item=True)
                    async_to_sync(self.channel_layer.group_send)(f'{user.id}_room', message)
                    async_to_sync(self.channel_layer.group_send)('admin_group', message)

    @sync_to_async
    def read_all_message_from_room(self, user_pk, room_id):
        room = async_to_sync(self.create_or_get_support_chat_room)(int(room_id))
        if room_id != user_pk:
            room.message.filter(is_read=False).filter(user_posted=room_id).update(is_read=True)
        else:
            room.message.filter(is_read=False).exclude(user_posted=room_id).update(is_read=True)
        room.notread.save()

    async def connect(self):
        """Подключение пользователя"""
        recieve_user = str(self.scope["url_route"]["kwargs"][
                               "user"])  # сюда с фронта передаём имя комнаты для выгрузки сообщения в админ чат
        user = self.scope['user']  # TODO получаем имя пользователя который подключился с фронта
        #user_id = str(self.scope["user"].id)
        if is_auth := user.is_authenticated:
            if self.scope['user'].is_staff:
                await self.channel_layer.group_add('admin_group', self.channel_name)
                await self.channel_layer.group_add(f'{user.id}_room', self.channel_name)
            else:
                await self.channel_layer.group_add(f'{user.id}_room',
                                                   self.channel_name)  # TODO добавляем в группу юзеров
        self.room_name = 'go'  # задаем статический румнейм для общего чата
        self.room_group_name = f"chat_{self.room_name}"  # формируем рум груп нейм
        self.unique_room_name = f"{user.id}_room"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)  # добавляем в группу юзеров
        await self.accept()
        # await self.get_free_balance(user)
        await self.channel_layer.send(self.channel_name, {
            "type": 'roulette_countdown_state',
        })
        await self.set_online(is_auth)
        if is_auth:
            await self.change_balance(user)
        if recieve_user == 'go':  # Проверка подключение из админки или нет. 'go' - это не админка
            # выгружает свою историю чата поддержки
            await self.init_support_chat(user.pk)
            await self.init_users_chat(self.channel_name)
        else:
            await self.get_all_room()
        await self.channel_layer.send(self.channel_name, {
            "type": "send_lvl_and_exp"
        })

    async def disconnect(self, code):
        """Отключение пользователя"""
        await self.channel_layer.group_discard(f'{str(self.scope["user"].id)}_room', self.channel_name)
        await self.channel_layer.group_discard('admin_group', self.channel_name)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)  # убирает юзера из группы
        await self.set_online(self.scope["user"].is_authenticated, False)

    async def receive(self, text_data=None, bytes_data=None):
        """Принятие сообщения"""
        text_data_json = json.loads(text_data)
        user = self.scope['user']
        if user.is_authenticated:
            if user.is_staff:
                if message_to_delete := text_data_json.get('delete_message'):
                    new_list_all_chat_50 = await self.all_chat_delete_message(message_to_delete)
                    await self.channel_layer.group_send(self.room_group_name, {
                        "type": "chat_message",
                        "chat_type": "all_chat_list",
                        "message": "list",
                        "list": new_list_all_chat_50
                    }
                                                        )
                elif user_id_to_ban := text_data_json.get("ban_user_all_chat"):
                    await self.add_user_to_chat_ban(user_id_to_ban)
            if text_data_json.get('vk_youtube_api') == 1:
                if text_data_json.get('subscribe') == "vk":
                    t1 = threading.Thread(target=vk_subscribe, args=(user,))
                    t1.start()
                elif text_data_json.get('subscribe') == "y":
                    if youtube_id := text_data_json.get('payload'):
                        thread_for_youtube = threading.Thread(target=check_youtube_subscribers, args=(youtube_id, user))
                        thread_for_youtube.start()
                        # await check_youtube_subscribers(youtube_id)
            elif text_data_json.get('init_faq'):
                await self.read_all_message_from_room(user.pk, user.pk)
                await self.channel_layer.group_send(f'{user.pk}_room', {
                    "type": "not_read",
                    'not_read': None
                })
            elif text_data_json.get('last_visit'):
                is_approved = await self.check_last_visit(text_data_json.get('last_visit'))
                if is_approved:
                    message = {"type": "send_approving_for_support_chat", "last_visit": 1}
                else:
                    message = {"type": "send_approving_for_support_chat", "last_visit": 0}
                await self.channel_layer.group_send(self.unique_room_name, message)
            elif text_data_json.get('get_avatar'):
                await self.get_avatar(text_data_json)
            elif text_data_json.get('set_avatar'):
                await self.set_avatar_new_username(text_data_json)
            # обмен предмета пользователя на валюту дурак-ролл
            elif text_data_json.get('sell_user_item'):
                await self.sell_item(text_data_json.get('sell_user_item'), user)
            # обмен предмета пользователя на валюту в дурак-онлайн
            elif text_data_json.get('forward_user_item'):
                await self.forward_item(text_data_json.get('forward_user_item'))
            elif text_data_json.get('get_cases_items'):
                await self.get_items_for_cases()
            # получение предметов в инвентарь
            # elif text_data_json.get('item'):
                await self.get_user_items(user)
            # кнопка открытия кейса
            elif text_data_json.get('open_case'):
                this_case = text_data_json.get('open_case')
                await self.open_case(this_case, user)
                # await self.get_user_items()
                await self.get_cases_info(user)
            # информация о кейсах
            elif text_data_json.get('cases'):
                await self.get_cases_info(user)
            elif text_data_json.get('bet') is not None:
                if user:
                    user_pk = user.pk
                    bet = text_data_json.get('bet')
                    bet_is_valid = await self.save_bet(bet, user_pk)
                    amount = None
                    if bet_is_valid:
                        amount = bet.get('bidCount')
                    await self.change_balance(user, amount)
                    await self.channel_layer.group_send(
                        self.room_group_name, {
                            "type": "get_bid",
                            "bid": text_data_json,
                        }
                    )
            # получение запроса на зачисление бонусных средств
            elif text_data_json.get("get_free_balance") == 'g':
                await self.send_free_balance(user)
            elif text_data_json.get('free_balance') == 'get':
                await self.get_free_balance(user)
            elif rub := text_data_json.get("rub"):
                if rub == "to_credits":
                    await self.send_rubs_from_credits(text_data_json.get("to_credits"))
                else:
                    await self.send_credits_from_rubs(text_data_json["rub"])
            #Первичное получение и обработка сообщений
            elif text_data_json.get('chat_type') == 'support':
                if len(text_data_json.get("message")) <= 500:
                    file_path = ''
                    if filed := text_data_json.get('file'):
                        file_path = await self.base64_to_image(filed)
                    room = await self.create_or_get_support_chat_room(user.pk)
                    await self.save_user_message(room, user.id, text_data_json["message"], file_path)
                    if not user.is_staff:
                        await self.send_support_chat_message(self.channel_name,
                                                             text_data_json["message"],
                                                             user.username, file_path)  # из супорт чата на сайте себе
                    await self.channel_layer.group_send('admin_group', {"type": "support_chat_message",
                                                                        "chat_type": "support",
                                                                        "message": text_data_json["message"],
                                                                        "user": user.username,
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
                    await self.read_all_message_from_room(user.pk, receive_user)
                    await self.get_all_room()
                    await self.init_support_chat(receive_user)
                else:
                    receive = text_data_json.get('receive')
                    room = await self.create_or_get_support_chat_room(receive)
                    await self.save_user_message(room, user.id,
                                                 text_data_json["message"], file_path)  # сохранении сообщение админа в бд
                    not_read = await self.get_not_read(room)
                    await self.send_support_chat_message(self.channel_name, text_data_json["message"],
                                                         user.username,
                                                         file_path)  # отправка сообщения самому себе в админку
                    await self.channel_layer.group_send(f'{receive}_room', {"type": "support_chat_message",
                                                                            "chat_type": "support",
                                                                            "message": text_data_json["message"],
                                                                            "file_path": f'/{file_path}',
                                                                            "user": user.username, })  # отправка сообщения пользователю в рум
                    await self.channel_layer.group_send(f'{receive}_room', {"type": "not_read",
                                                                            'not_read': not_read,
                                                                            })
            elif text_data_json.get('chat_type') == 'all_chat':
                """Общий чат на всех страницах. Получаем сообщение и рассылаем его всем.
                Проводим проверку на длину сообщения не более 250 символов.
                Проводим проверку на бан пользователя."""
                all_chat_message = {"type": "chat_message",
                                    "chat_type": text_data_json.get('chat_type'),
                                    "message": text_data_json["message"],
                                    "user": text_data_json["user"],
                                    "avatar": text_data_json["avatar"],
                                    "rubin": text_data_json.get("rubin"),
                                    "t": text_data_json.get("t"),
                                    "id": text_data_json.get("id")
                                    }
                if await self.check_total_transactions(user):
                    return await self.channel_layer.group_send(self.unique_room_name, {'type':'all_chat_error'})
                if len(all_chat_message["message"]) <= 250:
                    if await self.get_ban_chat_user(user):
                        await self.channel_layer.group_send(self.unique_room_name, all_chat_message)
                    elif not await self.check_bad_slang(text_data_json["message"].lower()):
                        await self.channel_layer.group_send(self.unique_room_name, all_chat_message)
                    else:
                        await self.channel_layer.group_send(self.room_group_name, all_chat_message)
                        await self.save_user_message_all_chat(all_chat_message)

    async def get_online(self, event):
        """Получение онлайна для нового юзера"""
        message = {'get_online': event.get('get_online')}
        if s := event.get('staff'):
            message['staff'] = s
        await self.send(text_data=json.dumps(message))

    async def get_rooms(self, event):
        await self.send(text_data=json.dumps({
            "room_name": event.get('room_name'),
            "room_data": event.get('room_data')
        }))

    async def chat_message(self, event):
        """Общий чат - обмен сообщениями"""
        await self.send(text_data=json.dumps(
            {
                "chat_type": event.get('chat_type'),
                "user": event.get('user'),
                "message": event.get("message"),
                "avatar": event.get("avatar"),
                "rubin": event.get("rubin"),
                "list": event.get('list'),
                "t": event.get('t'),
                "id": event.get("id"),
            }
        ))

    async def support_chat_message(self, event):
        await self.send(text_data=json.dumps(
            {
                "message": event.get("message"),
                "list_message": event.get('list_message'),
                "chat_type": event.get('chat_type'),
                "user": event.get('user'),
                "file_path": event.get('file_path'),
                'is_sell_item': event.get('is_sell_item')
            }
        ))

    async def roulette_countdown_starter(self, event):
        """Начинает отсчёт рулетки"""
        await self.send(text_data=json.dumps({
            "roulette": 20,
        }))

    # начинает крутиться рулетка
    async def rolling(self, event):
        """Начинает прокрутку рулетки"""
        await self.send(text_data=json.dumps({
            "roll": 'rolling',
            "winner": event.get('winner'),
            "c": event.get('c'),
            "p": event.get('p')
        }))

    async def stopper(self, event):
        """Сигнализирует об остановке прокрутки рулетки"""
        await self.send(text_data=json.dumps({
            "stop": "stopping",
            "w": event.get('winner'),
        }))

    async def go_back(self, event):
        """Откатывает рулетку на первоначальное состояние"""
        await self.send(text_data=json.dumps({
            'back': 'go-back',
            'previous_rolls': event.get('previous_rolls'),
        }))

    async def get_bid(self, event):
        """Обрабатывает ставки пользователей"""
        await self.send(text_data=json.dumps({
            "bid": event.get('bid'),
            "round_bets": r.json().get('round_bets')
        }))

    async def get_balance(self, event):
        """Отправляет изменения баланса пользователя"""
        message = event.get('balance_update')
        await self.send(text_data=json.dumps(message))

    @sync_to_async
    def change_balance(self, user, amount_to_subtract=None):
        user_to_change = CustomUser.objects.get(id=user.id)
        if amount_to_subtract:
            user_to_change.detailuser.total_balance -= amount_to_subtract
            user_to_change.detailuser.save()
        async_to_sync(self.channel_layer.group_send)(self.unique_room_name, {
            'type': 'get_balance',
            'balance_update': {
                'current_balance': user_to_change.detailuser.total_balance
            }
        })

    async def save_bet(self, bet, user_pk):
        storage_name = tasks.KEYS_STORAGE_NAME
        bet["channel_name"] = self.unique_room_name
        is_valid = await tasks.save_as_nested(storage_name, user_pk, bet)
        return is_valid

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
        """Отправляет новому клиенту состояния рулетки"""
        state = r.get('state')
        t = r.get('start:time')
        bets = r.json().get('round_bets')
        message = {'init': {
            "state": state,
            "t": str(t),
            "previous_rolls": r.json().get('last_winners'),
            "bets": bets
        }
        }
        if state == 'rolling' or state == 'stop':
            if r.exists("RAP"):
                rap = r.json().get("RAP")
                message["init"].update(rap)
            round_result = r.get(ROUND_RESULT_FIELD_NAME)
            message['init']['w'] = round_result

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

    async def get_avatar(self, data):
        """Отправляет новую аватарку(или аватарку соц-сети) пользователю"""
        if data.get('get_avatar') == 'all':
            if avatar_id := data.get('c'):
                updated_avatar = await self.generate_avatar(avatar_id)
            else:
                updated_avatar = await self.generate_avatar()
            message = {'b_avatar': updated_avatar.avatar_img.url,
                       'c': updated_avatar.id}
        else:
            updated_avatar = self.scope['user'].avatar
            message = {'u_avatar': updated_avatar.url}
        await self.send(json.dumps(message))

    @sync_to_async
    def generate_avatar(self, prev_avatar_id=None):
        """Генерирует последовательно базовые аватарки"""
        if prev_avatar_id and AvatarProfile.objects.filter(id__gt=prev_avatar_id).exists():
            ava = AvatarProfile.objects.filter(id__gt=prev_avatar_id).first()
        else:
            ava = AvatarProfile.objects.first()
        return ava

    @sync_to_async
    def check_username(self, username):
        return CustomUser.objects.filter(username=username).exists()

    @sync_to_async
    def set_username(self, new_name):
        self.scope['user'].username = new_name
        self.scope['user'].save()

    @sync_to_async
    def set_new_basic_avatar(self, avatar_id=None, basic=True):
        if avatar_id:
            self.scope['user'].avatar_default_id = avatar_id
        self.scope['user'].use_avatar = basic
        self.scope['user'].save()

    async def set_avatar_new_username(self, data):
        if data.get('user') != data.get('new_username'):
            check_username = await self.check_username(data.get('new_username'))
            if check_username:
                message = {'error': 'Попробуйте другое имя...'}
                await self.send(json.dumps(message))
                return
            else:
                await self.set_username(data.get('new_username'))
        if data.get('basic', True):
            if ava_id := data.get('avatarId'):
                await self.set_new_basic_avatar(ava_id)
            else:
                await self.set_new_basic_avatar()
        else:
            await self.set_new_basic_avatar(basic=False)
        message = {'new_username': data.get('new_username'),
                   'set_avatar': data.get('set_avatar')}
        await self.send(json.dumps(message))

    @staticmethod
    async def all_chat_delete_message(message_to_delete):
        """Находит и удаляет указанное сообщение в общем чате из Redis"""
        message_index = None
        new_list_all_chat_50 = r.json().get("all_chat_50")
        for i, message in enumerate(new_list_all_chat_50):
            id_t = message.get('t')
            if str(id_t) == message_to_delete:
                message_index = i
                break
        if message_index:
            r.json().arrpop("all_chat_50", ".", message_index)
        return r.json().get("all_chat_50")

    async def not_read(self, event):
        message = {'not_read_count': event.get('not_read')}
        await self.send(json.dumps(message))

    async def send_from_mod_lvl(self, event):
        message = {'modal_lvl_data': event.get('modal_lvl_data')}
        await self.send(json.dumps(message))

    async def send_approving_for_support_chat(self, event):
        await self.send(json.dumps({"last_visit": event.get("last_visit")}))

    async def send_free_balance(self, user):
        if user.id:
            detail_user = await DetailUser.objects.aget(user_id=user.id)
            await self.send(json.dumps({"free_balance": detail_user.free_balance}))

    @sync_to_async
    def check_bonuses(self, user):
        bonuses = UserBonus.objects.filter(detail_user_id=user.id, is_active=False, is_from_referal_activated=None)
        if bonuses:
            bonuses.update(is_active=True, is_from_referal_activated=True)
            return True
        return False

    @sync_to_async
    def calculate_free(self, detail_user):
        free_balance_history = FreeBalanceHistory.objects.filter(detail_user=detail_user, is_active=True)
        total_bonus_free = free_balance_history.aggregate(total_bonus=Sum('bonus_sum')).get('total_bonus')
        free_balance_history.update(is_active=False)

    @sync_to_async
    def get_total_balance(self, user):
        balance = user.detailuser.total_balance
        return balance

    async def get_free_balance(self, user):
        if user.id:
            detail_user = await DetailUser.objects.aget(user_id=user.id)
            bonuses_activated = await self.check_bonuses(user)
            if bonuses_activated and detail_user.free_balance > 0:
                detail_user.balance += detail_user.free_balance
                await self.calculate_free(detail_user)
                detail_user.free_balance = 0
                await sync_to_async(detail_user.save)()
            await self.send(json.dumps({"free_balance": detail_user.free_balance}))
            # total_balance = await self.get_total_balance(user)
            message = {'current_balance': detail_user.total_balance}
            await self.send(json.dumps(message))

    async def send_credits_from_rubs(self, rub):
        """Переводит рубли в кредиты и возвращает пользователю"""
        try:
            sum_rub = int(rub)
        except (TypeError, ValueError) as err:
            sum_rub = 0
        sum_credits = await sync_to_async(rub_to_pay)(sum_rub)
        await self.send(json.dumps({
            "credits": sum_credits
        }))

    async def send_rubs_from_credits(self, sum_credits):
        """Переводит кредиты в рубли"""
        try:
            int_credits = int(sum_credits)
        except (TypeError, ValueError):
            int_credits = 0
        rubs = await sync_to_async(virtual_money_to_rub)(int_credits)
        await self.send(json.dumps({
            "creds_to_rubs": rubs
        }))

    async def check_bad_slang(self, message: str) -> bool:
        """Проверяет сообщение на наличие запрещённых слов"""
        if not r.exists("bad_slang"):
            await self.init_bad_slang()
        bad_words_set = r.smembers("bad_slang")
        for word in bad_words_set:
            if word in message:
                return False
        return True

    @sync_to_async
    def init_bad_slang(self):
        if words := BadSlang.objects.all().only("name").values_list("name", flat=True):
            all_words = words
            r.sadd("bad_slang", *set(all_words))

    async def subscriber(self, event):
        event.pop('type')
        await self.send(json.dumps(event))

    async def all_chat_error(self, event):
        message = {'error': 'erroro 3М'}
        await self.send(json.dumps(message))
