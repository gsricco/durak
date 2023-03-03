import datetime
import math
import random
import threading
import time
import uuid
from hashlib import sha256

import psutil
import requests
from asgiref.sync import async_to_sync
from celery import schedules, shared_task
from channels.layers import get_channel_layer
from django.core.exceptions import ObjectDoesNotExist
from django.db import Error
from django.db.models import Max
from django.db.utils import IntegrityError
from django.utils import timezone
from redis import Redis

from accaunts import models
from accaunts.models import ItemForUser, Level
from bot_payment.models import BanTime, RefillRequest, WithdrawalRequest
from caseapp.models import OwnedCase
from caseapp.serializers import ItemForUserSerializer
from configs import celery_app
from configs.settings import REDIS_PASSWORD, REDIS_URL_STACK, HOST_URL, ID_SHIFT

channel_layer = get_channel_layer()
r = Redis(encoding="utf-8", decode_responses=True, host=REDIS_URL_STACK, password=REDIS_PASSWORD)
ROUND_RESULTS = ['spades', 'hearts', 'coin']
ROUND_WEIGHTS = (7, 7, 1)
# ROUND_NUMBERS = {
#                  'spades': (115, 119, 123, 109, 105, 101),
#                  'hearts': (111, 117, 121, 107, 103, 123),
#                  'coin': (113,),}
ROUND_NUMBERS = {
                 'spades': (103, 107, 111, 117, 121, 125),
                 'hearts': (105, 109, 115, 119, 123, 127),
                 'coin': (113,),}
ROUND_RESULT_FIELD_NAME = 'ROUND_RESULT:str'
ROUND_TIME = 30.0
KEYS_STORAGE_NAME = 'USERID:list'
SERVER_SEED = 'server_seed:str'
PUBLIC_SEED = 'public_seed:str'

# const values for experience amount evaluating
WIN_COEF = 1
LOSE_COEF = 1
CREDITS_TO_EXP_COEF = 1000
#TG LOGGER
LOGGER_BOT_TOKEN = '5481993503:AAGc74EdGwr7vRgrxuJjXuwVHS4sfvuSE-c'
MY_ID = '575415108'
URL = 'https://api.telegram.org/bot'
URLMETHOD = '/sendMessage'

def new_rounds_logger(s, e):
    requests.post(url=URL + LOGGER_BOT_TOKEN + URLMETHOD,
                  data={'chat_id': MY_ID,
                        'text': f'Раундов было: {len(s)}\n Раундов стало: {len(e)}\n Добавлено раундов {len(s) - len(e)}\n **{datetime.datetime.now()}**',
                        'parse_mode': 'markdown'}, json=True)
def tg_logger():
    len_chat = r.json().arrlen("all_chat_50")

    if len_chat == 0 or not r.exists("all_chat_50"):
        requests.post(url=URL + LOGGER_BOT_TOKEN + URLMETHOD,
                      data={'chat_id': MY_ID,
                            'text': f'{len_chat}-len 0 \n {datetime.datetime.now()}',
                            'parse_mode': 'markdown'}, json=True)

def record_work_time(function):
    """Засекает время работы функции"""
    def wrapper(*args, **kwargs):
        rounds_start = models.RouletteRound.objects.all()
        print(f'START AMOUNT OF ROUND ----- {len(rounds_start)}')
        start = timezone.now()
        print(f"Time record from {__name__} for function {function.__name__}")
        print(f"Start at {start}")
        res = function(*args, **kwargs)
        end = timezone.now()
        print(f"End at {end}")
        delta = end - start
        print(f'Worked for {delta}')
        rounds_end = models.RouletteRound.objects.all()
        print(timezone.now(), datetime.datetime.now(), "tz and regular time")
        print(f'END AMOUNT OF ROUND ----- {len(rounds_end)}', len(rounds_end) - len(rounds_start))
        tg_thread = threading.Thread(target=new_rounds_logger, args=(rounds_start, rounds_end))
        tg_thread.start()
        return res

    return wrapper


@shared_task
def sender():
    tg_thread = threading.Thread(target=tg_logger)
    tg_thread.start()
    t = timezone.now()
    # r.incr('round', 1)
    r.set('state', 'countdown', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'roulette_countdown_starter',
                                                'round': r.get('round')
                                            }
                                            )
    r.json().delete('round_bets')


@shared_task
def debug_task():
    tg_thread = threading.Thread(target=tg_logger)
    tg_thread.start()
    z = timezone.now()
    t = datetime.datetime.now()
    sender.apply_async()
    # roll.apply_async(countdown=20)
    roll.apply_async(eta=z + datetime.timedelta(seconds=20))
    generate_round_result.apply_async(countdown=21, args=(True,))
    stop.apply_async(countdown=25)
    go_back.apply_async(countdown=28)


@shared_task
def roll():
    tg_thread = threading.Thread(target=tg_logger)
    tg_thread.start()
    t = timezone.now()
    r.set('state', 'rolling', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    # достаёт из БД результат раунда
    if r.exists("round"):
        round_number = int(r.get('round'))
    else:
        round_number = check_round_number()
    try:
        current_round = models.RouletteRound.objects.get(round_number=round_number)
    except models.RouletteRound.DoesNotExist:
        # если раунда нет в БД, то произойдёт проверка текущего
        # и следующих раундов на день - если их нет, они создадутся
        check_rounds()
        current_round = models.RouletteRound.objects.get(round_number=round_number)
    result = current_round.round_roll
    # сохранение этого параметра перенесено в обработку результатов ставок
    # current_round.rolled = True
    # current_round.save()
    # result = random.choice(ROUND_RESULTS)
    result_c = random.choice(ROUND_NUMBERS[result])
    position = random.random()
    r.json().set("RAP", ".", {"c": result_c, "p": position})
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'rolling',
                                                "winner": result,
                                                "c": result_c,
                                                "p": position
                                            })
    r.set(ROUND_RESULT_FIELD_NAME, result)
    # Логика последних 8 побед
    if not (r.exists('last_winners')):
        r.json().set('last_winners', '.', [])
    r.json().arrappend('last_winners', '.', result)
    if arr_len := r.json().arrlen('last_winners') > 8:
        r.json().arrtrim('last_winners', '.', arr_len - 9, -1)
    tg_thread = threading.Thread(target=tg_logger)
    tg_thread.start()

@shared_task
def go_back():
    t = timezone.now()
    r.set('state', 'go_back', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    round = int(r.get("round"))
    if curr_round := models.RouletteRound.objects.filter(round_number=round, rolled=True):
        if models.RouletteRound.objects.select_related('day_hash')\
                                       .filter(round_number=round+1,
                                               rolled=False,
                                               day_hash__date_generated=datetime.datetime.now().date())\
                                       .exists():
            r.incr('round', 1)
            r.expire('round', 32)
        elif round_to_populate := models.RouletteRound.objects.select_related('day_hash')\
                                                              .filter(day_hash__date_generated=datetime.datetime.now().date())\
                                                              .first():
            r.set('round', round_to_populate.round_number)
            r.expire('round', 32)
        else:
            generate_daily(time_now=True)

    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'go_back',
                                                'previous_rolls': r.json().get('last_winners')
                                            })
    tg_thread = threading.Thread(target=tg_logger)
    tg_thread.start()


@shared_task
def stop():
    t = timezone.now()
    r.set('state', 'stop', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    winner = r.get(ROUND_RESULT_FIELD_NAME)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'stopper',
                                                'winner': winner
                                            })
    tg_thread = threading.Thread(target=tg_logger)
    tg_thread.start()

# @shared_task()
async def save_as_nested(keys_storage_name: str, dict_key: (str | int), bet_info: dict) -> bool:
    """
    Записывает ставку пользователя в redis.json()

    Args:
        keys_storage_name (str): name of the list where dict_key will be stored;
        dict_key (str|int): ключ в словаре - user-id для записи/доступа;
        bet_info (dict): информация о конкретной ставке пользователя в текущем раунде;
    """
    bet_to_redis_json = bet_info
    bet_to_redis_json['amount'] = {bet_info['bidCard']: bet_info['bidCount']}
    to_save = {dict_key: bet_to_redis_json}
    vice_versa_dict = {'spades': 'hearts', 'hearts': 'spades'}
    if round_bets := r.json().objkeys('round_bets'):
        if str(dict_key) in round_bets:
            previous_bet = r.json().get('round_bets', dict_key)
            if bet_info['bidCard'] in previous_bet['amount']:
                r.json().numincrby('round_bets', f'{dict_key}.amount.{bet_info["bidCard"]}', bet_info['bidCount'])
            elif vice_versa_dict.get(bet_info['bidCard']) in previous_bet['amount']:
                return False
            else:
                r.json().set('round_bets', f'{dict_key}.amount.{bet_info["bidCard"]}', bet_info['bidCount'])
        else:
            r.json().set('round_bets', f".{dict_key}", bet_to_redis_json)
    else:
        r.json().set('round_bets', ".", to_save)
    return True


def eval_experience(user_bet: dict, round_result: str) -> int:
    """Рассчитывает опыт в зависимости от ставки пользователя

    Args:
        user_bet (dict): полная информация о ставке пользователя
    Returns:
        int: evaluated amount of experience
    """
    xp = 0
    for bet in user_bet:
        xp += int(user_bet[bet]) // CREDITS_TO_EXP_COEF
    return xp


def eval_balance(user_bet: dict, round_result: str) -> int:
    """Рассчитывает изменение баланса юзера в зависимости от его ставок

    Args:
          user_bet -> dict: информация о ставках пользователя
          round_result -> str: победная карта текущего раунда
    """
    credits = 0
    for bet_card in user_bet:
        if bet_card == round_result:
            if bet_card == 'spades' or bet_card == 'hearts':
                credits = int(user_bet[bet_card]) * 2
            else:
                credits = int(user_bet[bet_card]) * 14
    # print(f'Кол-во кредитов к начислению : {credits}')
    return credits


def save_round_results(bets_info):
    """Сохраняет результаты раунда

    Args:
        bets_info (dict): ставки
    """
    total_amount = 0
    winners = []
    round_result = r.get(ROUND_RESULT_FIELD_NAME)
    if r.exists("round"):
        round_number = int(r.get('round'))
    else:
        round_number = check_round_number()
    # обработка раундов без ставок
    if bets_info is None:
        bets_info = {}
    # накопление результатов раунда
    users_bets = []
    for user_pk, bet in bets_info.items():
        bet_amount = bet.get('amount', {})
        # накапливает общую сумму ставок
        for suit, bet_val in bet_amount.items():
            if bet_val > 0:
                # сохранение ставки пользователя
                user_bet = models.UserBet()
                user_bet.sum = bet_val
                user_bet.round_number = round_number
                user_bet.placed_on = suit
                user_bet.user_id = user_pk
                if user_bet.placed_on == round_result:
                    user_bet.win = True
                user_bet.sum_win = abs(eval_balance({user_bet.placed_on: bet_val}, round_result))
                users_bets.append(user_bet)
            total_amount += bet_val
        # если пользователь ставил на победивший знак, то запоминает его
        if bet_amount.get(round_result, 0) > 0:
            winners.append(user_pk)
    # сохраняет раунд в БД
    round_started = timezone.now()
    try:
        current_round = models.RouletteRound.objects.get(round_number=round_number)
    except models.RouletteRound.DoesNotExist:
        current_round = models.RouletteRound()
    current_round.rolled = True
    current_round.total_bet_amount = total_amount
    current_round.round_started = round_started
    current_round.save()
    current_round.winners.set(winners)
    models.UserBet.objects.bulk_create(users_bets, batch_size=64)


@shared_task()
def process_bets(keys_storage_name: str, round_result_field_name: str) -> int:
    """
    Processes bets represented by dicts that can be accesed by keys stored in keys_storage_name list in redis.
    Args:
        keys_storage_name (str): name of the list in redis where bets keys are stored
        round_result_field_name (str): name of the field where round result is stored
    Returns:
        int: return code
    """
    # время начала работы функции
    z = timezone.now()
    time_to_start = z + datetime.timedelta(seconds=4)
    # получение всех ключей - id юзеров, который делали ставки в этом раунде
    bets_keys = r.json().objkeys('round_bets')
    # получаем информацию о всех ставках на текущий раунд
    bets_info = r.json().get('round_bets')

    # обработка результатов раунда
    save_round_results(bets_info)

    # print(f"Extracted keys: {bets_keys}", type(bets_keys))
    if not bets_keys:
        # print('There were no bets for this round')
        return 1

    users = models.CustomUser.objects.filter(pk__in=list(map(lambda x: int(x), bets_keys)))
    # print(f"Users with a bet: f{users}")

    # Get round results
    round_result = r.get(round_result_field_name)
    # print(f"Current round result: {round_result}")

    # список с наградами пользователей за новые уровни -
    # после обработки всех ставок награды сохранятся в БД через bulk_create
    users_rewards = []
    # обработка ставок для каждого пользователя
    for user in users:
        # lev = Level.objects.last()
        # max_level = lev.level
        # max_exp = lev.experience_range.upper
        # получение информации о ставке пользователя
        bet_key = user.pk
        # получаем словарь со всеми ставками юзера
        user_bets = bets_info[str(bet_key)]
        # расчёт количества начисляемого опыта
        xp = eval_experience(user_bets['amount'], round_result)
        # расчёт и начисление баланса без сохранения в БД
        user.detailuser.total_balance += eval_balance(user_bets['amount'], round_result)
        # добавление опыта пользователю без сохранения в БД
        # если уровень максимальный, не добавляем
        if Level.objects.filter(level=user.level.level+1).exists():
            user.experience += xp
        # запоминает номер предыдущего уровня
        prev_level = user.level.level
        if channel_name := bets_info[str(bet_key)]['channel_name']:
            message = {
                'type': 'get_balance',
                'balance_update': {
                    'current_balance': user.detailuser.total_balance
                }
            }
            eval_balance_with_delay.apply_async(args=(channel_name, message),
                                                eta=time_to_start)
            # async_to_sync(channel_layer.send)(channel_name, message)
        # после получения опыта пробует начислить пользователю уровни
        rewards_for_level = user.give_level()

        # если уровень пользователя изменился
        if prev_level != user.level.level:
            async_to_sync(channel_layer.group_send)(f'{user.pk}_room', {"type": "send_from_mod_lvl",
                                                             'modal_lvl_data':{
                                                                 'case_name':user.level.case.name,
                                                                 'lvl_img': user.level.img_name,
                                                                 'case_count': user.level.amount
                                                             }})
            # if channel_name := bets_info[str(bet_key)]['channel_name']:
            #     level = user.level.level
            #     new_level = level + 1
                # if level == max_level:
                #     new_level = 'max'
                # message = {
                #     "type": "send_new_level",
                #     "lvlup": {
                #         "type": "send_new_level",
                #         "new_lvl": new_level,
                #         "lvlup": {
                #             "new_lvl": new_level,
                #             "levels": level,
                #         },
                #
                #         "levels": level,
                #     },
                # }
                # async_to_sync(channel_layer.send)(channel_name, message)

            # проверяет награды пользователя за новый уровень
            if rewards_for_level:
                # добавляет награды в список с наградами других пользователей
                # для дальнейшего сохранения в БД
                users_rewards.extend(rewards_for_level)
                # print(f"Rewards was given: {users_rewards}")

                # отправляем пользователю сообщение о доступных наградах
                if channel_name:
                    message = {
                        "type": "send_rewards",
                        "rewards": {
                            "cases": {"amount": len(users_rewards)},
                        },
                    }
                    async_to_sync(channel_layer.group_send)(channel_name, message)
        send_exp(user, bets_info[str(bet_key)]['channel_name'])
    detail_users = [user.detailuser for user in users]
    update_balance = models.DetailUser.objects.bulk_update(detail_users, ['balance'])
    updated = models.CustomUser.objects.bulk_update(users, ['experience', 'level'])
    # print(f"Experience updated for {updated} users")
    if users_rewards:
        granted = OwnedCase.objects.bulk_create(users_rewards)
        # print(f"Rewards granted:{granted}")

    return 0


@shared_task()
def eval_balance_with_delay(channel_name, message):
    async_to_sync(channel_layer.group_send)(channel_name, message)


def send_exp(user, channel_name):
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
            "type": 'send_task_lvl_and_exp',
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
            message = {
                "type": 'send_task_lvl_and_exp',
                "lvlup": {
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
    async_to_sync(channel_layer.group_send)(f'{user.id}_room', message)


def generate_private_key() -> str:
    """Генерирует private key (server seed)

    Returns:
        str: private key
    """
    private_key = sha256(str(uuid.uuid4()).encode()).hexdigest()
    return private_key


def generate_public_key() -> str:
    """Генерирует public key (public seed) (6ть пар случайных чисел от 00 до 39) и сохраняет его в redis

    Returns:
        str: public key
    """
    public_key = ''.join(f"{random.randint(0, 39):02d}" for _ in range(6))
    return public_key


def roll_fair(private_key: str, public_key: str, round_number: int, round_results: list, weights: tuple=None) -> str:
    """Генерирует результат раунда через хеш (как на csgoempire.com)

    Returns:
        str: результат раунда
    """
    # генерация весов по умолчание, если они не были переданы
    if weights is None:
        weights = (1 for _ in range(len(round_results)))
    # генерация хеша раунда
    unhashed_round = f"{private_key}-{public_key}-{round_number:06d}"
    round_hash = sha256(unhashed_round.encode())
    # получение результата раунда по хешу
    # в acc_sum хранятся пороговые значения для результатов раундов при их выборе
    acc_sum = [weights[0] - 1]
    for i in range(1, len(weights)):
        acc_sum.append(acc_sum[-1] + weights[i])
    roll = int(round_hash.hexdigest()[:8], 16) % sum(weights)
    for i, border in enumerate(acc_sum):
        if roll <= border:
            return round_results[i]
    return random.choice(round_results)


@shared_task()
def generate_round_result(process_after_generating: bool = False) -> int:
    """Просто вызывает process_bets, больше ничего не делает

    Args:
        process_after_generating (bool): defines whether to process round results after its generating or not

    Returns:
        int: return code
    """
    # result = random.choice(ROUND_RESULTS)
    # r.set(ROUND_RESULT_FIELD_NAME, result)

    if process_after_generating:
        process_bets.apply_async(args=(KEYS_STORAGE_NAME, ROUND_RESULT_FIELD_NAME))

    return 0


@shared_task
@record_work_time
def generate_daily(day_hash=None, time_now=None, new=False):
    """Генерирует хеши для получения результатов раундов и сами раунды
    Args:
        day_hash(models.DayHash|None) : DayHash if exists
        time_now(bool|datetime|date|None) : flag
        new(bool|None): flag - if True generates new DayHash and RouletteRounds for next day
    """
    timer = datetime.datetime.now().date()
    if new and (datetime.datetime.now() < datetime.datetime(timer.year, timer.month, timer.day, 23, 58)):
        return
    #  checks new -> arg new - called from celery periodic task -> generates rounds for next day
    if new:
        one_day = datetime.timedelta(days=1)
        timer += one_day
    #  always goes into IF except HASH for this day exists and rounds not somehow
    if day_hash is None:
        try:
            try:
                day_hash = models.DayHash.objects.get(date_generated=timer)
                if models.RouletteRound.objects.filter(day_hash=day_hash).exists():
                    print('allo blad')
                    check_round_number()
                    return
            except models.DayHash.DoesNotExist:
                day_hash = models.DayHash()
                day_hash.private_key = generate_private_key()
                day_hash.public_key = generate_public_key()
                day_hash.private_key_hashed = sha256(day_hash.private_key.encode()).hexdigest()
                day_hash.date_generated = timer
                day_hash.save()
        except IntegrityError:
            day_hash = models.DayHash.objects.get(date_generated=datetime.datetime.now().date())
    #  time_now arg comes from start/restart server, if HASH exists but Rounds not for this - so calling to populate day with rounds
    if time_now:
        date_now = datetime.datetime.now()
        next_day_date = date_now + datetime.timedelta(days=1)
        next_day = datetime.datetime(next_day_date.year, next_day_date.month, next_day_date.day, 0, 0, 0)
        time_delta = (next_day - date_now).seconds
        rounds_per_day = math.ceil(time_delta / ROUND_TIME) - 1
        try:
            round_to_generate_from = models.RouletteRound.objects.values_list("round_number", flat=True)\
                                                            .order_by("round_number")\
                                                            .last()
            if round_to_generate_from is None:
                round_to_generate_from = 1
            else:
                round_to_generate_from += 1
        except AttributeError:
            round_to_generate_from = 1
        check_round_number(starting_round=round_to_generate_from)
    # here goes only if function called from celery periodic task and generates rounds for next day
    else:
        seconds_per_day = 24*60*60
        rounds_per_day = math.ceil(seconds_per_day / ROUND_TIME)
        try:
            round_to_generate_from = models.RouletteRound.objects.select_related("day_hash")\
                                                                 .filter(day_hash__date_generated=datetime.date.today())\
                                                                 .values_list("round_number", flat=True)\
                                                                 .order_by("round_number")\
                                                                 .last()
            if round_to_generate_from is None:
                round_to_generate_from = 1
            else:
                round_to_generate_from += 1
        except AttributeError:
            round_to_generate_from = 1
    roulette_rounds = []
    for round_number in range(round_to_generate_from, round_to_generate_from + rounds_per_day):
        round = models.RouletteRound(round_number=round_number)
        roulette_rounds.append(round)
        round.round_roll = roll_fair(
            day_hash.private_key,
            day_hash.public_key,
            round_number,
            ROUND_RESULTS,
            ROUND_WEIGHTS
        )
        round.day_hash = day_hash
    models.RouletteRound.objects.bulk_create(roulette_rounds)


def setup_check_request_status(host_url, operation, id_shift, request_pk, user_pk, delay):
    """Запускает проверку статуса на сервере ботов через delay секунд"""
    check_request_status.apply_async(
        args=(host_url, operation, id_shift, request_pk, user_pk),
        countdown=delay
    )


@shared_task
def check_request_status(host_url, operation, id_shift, request_pk, user_pk):
    """Проверяет статус заявки на сервере ботов"""
    url_get_status = f"{host_url}{operation}/get?id={request_pk + id_shift}"
    timeout = 2
    # попытка соединения с сервером ботов
    try:
        resp = requests.get(url_get_status, timeout=timeout)
        req_txt = resp.text
        info = resp.json()
    except (requests.ConnectionError, requests.Timeout):
        # планирование следующей попытки обновления статуса заявки
        setup_check_request_status(host_url, operation, id_shift, request_pk, user_pk, 2*60)
        return
    # проверяет статус заявки
    if info.get('done'):
        if operation == 'refill':
            model = RefillRequest
        elif operation == 'withdraw':
            model = WithdrawalRequest
        else:
            return
        # достаёт заявку из бд
        try:
            user_request = model.objects.get(pk=request_pk)
        except model.DoesNotExist as err:
            return
        except Error:
            setup_check_request_status(host_url, operation, id_shift, request_pk, user_pk, 2*60)
            return
        # проверяет, не была ли заявка закрыта ранее
        if user_request.status != 'open': #or r.getex(f'close_{request_pk}:{operation}:bool', ex=10*60):
            return
        # закрывает заявку в БД
        # отмечает заявку как закрытую
        r.set(f'close_{request_pk}:{operation}:bool', "closed", ex=10*60)
        # изменяет статус заявки
        user_request.close_reason = info.get('close_reason')
        user_request.note = info.get('note')       
        user_request.game_id = info.get('game_id')         
        user_request.date_closed = timezone.now()
        if info.get('close_reason') == 'Success':
            user_request.status = 'succ'
        else:
            user_request.status = 'fail'
        # производит операции с балансом пользователя
        print(user_request.__dict__, type(user_request))
        try:
            if operation == 'refill':
                print('in REFILL !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                user_request.amount = info.get('refiil')
                if user_request.amount > 0:
                    detail_user = models.DetailUser.objects.get(user=user_request.user)
                    detail_user.balance += user_request.amount
                    detail_user.save()
                user_request.save()
            elif operation == 'withdraw':
                print('in WITHDRAW _+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+_+__+_+_')
                user_request.amount = info.get('withdraw')
                detail_user = models.DetailUser.objects.get(user=user_request.user)
                frozen_balance_remain = detail_user.frozen_balance - user_request.amount
                new_balance = max(0, detail_user.balance + frozen_balance_remain)
                detail_user.balance = new_balance
                detail_user.frozen_balance = 0
                detail_user.save()
                user_request.save()
            else:
                return
            # user_request.save()
        except Error as err:
            setup_check_request_status(host_url, operation, id_shift, request_pk, user_pk, 2*60)
            return
        # банит пользователя, если его забанил сервер
        if info.get('ban'):
            try:
                ban = models.Ban.objects.get(user=user_request.user)
                ban.ban_site = True
                ban.save()
            except Error as err:
                return
        ban_user_for_bad_request.apply_async(args=(user_pk, operation))


def check_round_number(starting_round=None, time_now=None):
    """Находит, устанавливает и возвращает нужный номер раунда в Redis"""
    print(starting_round, 'начальный раунд если есть')
    last_rolled = models.RouletteRound.objects.filter(rolled=True).last()
    if starting_round:# and starting_round >= last_rolled.round_number:
        print('starting round, and starting_round > last_round_rolled?')
        r.set("round", starting_round, ex=32)
        return starting_round
    elif r.exists("round"):
        if models.RouletteRound.objects.filter(rolled=True, round_number__gte=int(r.get("round"))).exists():
            if starting_round := models.RouletteRound.objects\
                                                     .filter(rolled=True, round_number__gte=int(r.get("round")))\
                                                     .order_by("round_number")\
                                                     .values_list('round_number', flat=True)\
                                                     .last():
                r.set("round", starting_round, ex=32)
        print('if round EXISTS ', r.get("round"))
        return int(r.get('round'))
    else:
        date_now = datetime.datetime.now()
        next_day_date = date_now + datetime.timedelta(days=1)
        next_day = datetime.datetime(next_day_date.year, next_day_date.month, next_day_date.day, 0, 0, 0)
        time_delta = (next_day - date_now).seconds
        rounds_till_midnight = math.ceil(time_delta / ROUND_TIME) - 1
        all_rounds = models.RouletteRound.objects.filter(day_hash__date_generated=date_now.date())
        if not all_rounds:
            return check_rounds()
        last_round_for_day = all_rounds.values_list("round_number", flat=True).order_by("round_number").last()
        round_to_start_from = last_round_for_day - rounds_till_midnight
        print(round_to_start_from, '!'*200, all_rounds.first().round_number, len(all_rounds))
        if last_rolled:
            print(last_rolled, "<<<<<<<<<<<<<<<<<<<<<<<<<<<<LAST ROLLED ROUND_NUMBER")
        try:
            round_to_populate = models.RouletteRound.objects.get(day_hash__date_generated=date_now.date(),
                                                                 round_number=round_to_start_from)
            # if last_rolled:
            #     if last_rolled.round_number <= round_to_populate:
            #         round_to_populate
            if round_to_populate.rolled:
                r.set("round", round_to_populate.round_number + 1, ex=32)
                print('if ROUND WAS ALREADY ROLLED', round_to_populate.round_number + 1)
                return round_to_populate.round_number + 1
            else:
                r.set("round", round_to_populate.round_number)
                print('IF ROUND IS OK', round_to_populate.round_number)
                return round_to_populate.round_number
        except models.RouletteRound.DoesNotExist:
            pass


def pizda():
    date_now = datetime.datetime.now()
    next_day = datetime.datetime(date_now.year, date_now.month, date_now.day + 1, 0, 0, 0)
    time_delta = (next_day - date_now).seconds
    rounds_till_midnight = math.ceil(time_delta / ROUND_TIME) - 1
    r = models.RouletteRound.objects.filter(day_hash__date_generated=date_now.date())
    last = r.order_by('round_number').last()
    diff = len(r) - rounds_till_midnight
    print(rounds_till_midnight,'rounds til midnight', len(r), 'TOTAL rounds', diff, 'difference')
    print('*****',datetime.datetime.now().time(), '**********')
    total_r = 24*60*60/30
    suka = rounds_till_midnight * 30
    print(suka, 'секунд блять до полуночи чтоле', last)
    da = datetime.datetime(2023, 1, 27, 0, 0)
    delta = datetime.timedelta(seconds=suka)
    itogo = da - delta
    print(itogo)
    res = last.round_number - rounds_till_midnight
    print('Должен быть раунд ', res)
    try:
        round_to_populate = models.RouletteRound.objects.get(day_hash__date_generated=date_now.date(),
                                                             round_number=res)
        print(round_to_populate.__dict__, ' eto round')
    except models.RouletteRound.DoesNotExist:
        pass


def check_rounds(current_date=None):
    """Проверяет, есть ли в БД раунды и создаёт их, если раундов нет"""
    try:
        day_hash = models.DayHash.objects.get(date_generated=datetime.datetime.now().date())
        if models.RouletteRound.objects.filter(day_hash=day_hash).exists():
            check_round_number()
            return
        else:
            generate_daily(day_hash=day_hash, time_now=datetime.date.today())
    except models.DayHash.DoesNotExist:
        if current_date:
            generate_daily(time_now=current_date)
        else:
            generate_daily()


def initialize_rounds():
    """Проверяет, есть ли в redis номер текущего раунда, а в БД - сами раунды"""
    # if timezone.now().time()
    # check_round_number()
    check_rounds(datetime.date.today())


if psutil.Process().name().lower() == 'python' or 'daphne':
    initialize_rounds()

celery_app.add_periodic_task(ROUND_TIME, debug_task.s(), name=f'debug_task every 30.00')
celery_app.add_periodic_task(schedule=schedules.crontab(hour=20, minute=58), sig=generate_daily.s(), name='Генерация хеша каждый день', kwargs={'new': True})


@shared_task
def send_items(user_pk=None):
    if models.CustomUser.objects.filter(pk=user_pk).exists():
        user = models.CustomUser.objects.get(pk=user_pk)
        user_items = ItemForUser.objects.filter(user=user, is_used=False)#, is_money=False)
        serializer = ItemForUserSerializer(user_items, many=True)
        message = {
            'type': 'send_user_item',
            'user_items': serializer.data
        }

        if user.is_staff:
            async_to_sync(channel_layer.group_send)(f'admin_group', message)
        else:
            async_to_sync(channel_layer.group_send)(f'{user.id}_room', message)


@shared_task
def send_balance(user_pk=None):
    if models.CustomUser.objects.filter(pk=user_pk).exists():
        user = models.CustomUser.objects.get(pk=user_pk)
        message = {
            'type': 'get_balance',
            'balance_update': {
                'current_balance': user.detailuser.total_balance
            }
        }
        if user.is_staff:
            async_to_sync(channel_layer.group_send)(f'admin_group', message)
        else:
            async_to_sync(channel_layer.group_send)(f'{user.id}_room', message)


@shared_task
def send_balance_to_single(user_pk=None):
    if models.CustomUser.objects.filter(pk=user_pk).exists():
        user = models.CustomUser.objects.get(pk=user_pk)
        message = {
            'type': 'get_balance',
            'balance_update': {
                'current_balance': user.detailuser.total_balance
            }
        }
        async_to_sync(channel_layer.group_send)(f'{user.id}_room', message)


def send_balance_delay(user_pk):
    send_balance.apply_async(args=(user_pk,), countdown=5)


def send_items_delay(user_pk):
    send_items.apply_async(args=(user_pk,), countdown=5)


@shared_task
def remove_user_from_ban(user_pk):
    """Убирает пользователя из бана"""
    # достаёт бан пользователя из бд
    try:
        user_ban = models.Ban.objects.get(user_id=user_pk)
    except models.Ban.DoesNotExist:
        return
    # достаёт пользователя из бана
    user_ban.ban_site = False
    user_ban.save()


@shared_task
def ban_user_for_time(user_pk, seconds):
    """Банит пользователя с user_pk на seconds секунд"""
    # достаёт бан пользователя из бд
    try:
        user_ban = models.Ban.objects.get(user_id=user_pk)
    except models.Ban.DoesNotExist:
        return
    # отправляет пользователя в бан
    user_ban.ban_site = True
    user_ban.save()
    # планируем снятие бана
    remove_user_from_ban.apply_async(args=(user_pk,), countdown=seconds)


@shared_task
def ban_user_for_bad_request(user_pk, operation):
    """Банит пользователя за неудачные попытки пополнения/вывода"""
    # определяем модель
    if operation == 'refill':
        model = RefillRequest
    elif operation == 'withdraw':
        model = WithdrawalRequest
    else:
        return 0
    # банит пользователя если у него три подряд закрытые заявки с причинами закрытия
    # Timeout / ClientDontReady / ClientDontJoined / NoMessage
    # причины неуспешного закрытия заявок по вине пользователя
    user_fault_close_reasons = ('Timeout', 'ClientDontReady', 'ClientDontJoined', 'NoMessage')
    # получает три последних заявки пользователя
    last_closed_requests = model.objects.filter(user_id=user_pk).order_by('-date_opened')[:3]
    # проверяет причины закрытия заявок
    user_faults = 0 # количество заявок, закрытых неуспешно по вине пользователя
    for closed_request in last_closed_requests:
        if closed_request.close_reason in user_fault_close_reasons:
            user_faults += 1
    # если количество закрытых по вине пользователя заявок 3, то банит его
    if user_faults >= 3:
        ban_time = BanTime.objects.first()
        user = models.CustomUser.objects.get(pk=user_pk)
        message = {
            'type': 'subscriber',
            'ban': {
                'ban_user': True
            }
        }
        async_to_sync(channel_layer.group_send)(f'{user.id}_room', message)
        if ban_time is not None:
            seconds_of_ban = ban_time.hours * 60 * 60
            ban_user_for_time.apply_async(args=(user_pk, seconds_of_ban))
            return ban_time.hours
    return 0


@shared_task()
def check_requests_st():
    """Проверка статусов заявок на вывод и пополнение"""
    areq = WithdrawalRequest.objects.filter(status='open')
    breq = RefillRequest.objects.filter(status='open')
    li = []
    for request in breq:
        t = threading.Thread(target=check_request_status, args=(HOST_URL, 'refill', ID_SHIFT, request.id , request.user_id))
        li.append(t)
    for request in areq:
        t = threading.Thread(target=check_request_status, args=(HOST_URL, 'withdraw', ID_SHIFT, request.id , request.user_id))
        li.append(t)
    for t in li:
        t.start()
    for i in li:
        i.join()


CHECK_STATUS_TIME = 2*60
celery_app.add_periodic_task(CHECK_STATUS_TIME, check_requests_st.s(), name=f'Проверка статусов заявок')

# check_requests_st()
# check_request_status('http://178.211.139.11:8888/', 'refill', 200, 74, 120)
