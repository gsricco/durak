import datetime
import math
import uuid
from django.db import Error
import requests
from hashlib import sha256
from caseapp.serializers import ItemForUserSerializer
from configs import celery_app
from celery import shared_task, schedules
from redis import Redis
from asgiref.sync import async_to_sync
from accaunts import models
from caseapp.models import OwnedCase
from channels.layers import get_channel_layer
import random
from django.db.models import Max
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.utils import timezone
from accaunts.models import Level, ItemForUser
from bot_payment.models import RefillRequest, WithdrawalRequest
from configs.settings import REDIS_URL_STACK

channel_layer = get_channel_layer()
r = Redis(encoding="utf-8", decode_responses=True, host=REDIS_URL_STACK)
ROUND_RESULTS = ['spades', 'hearts', 'coin']
ROUND_WEIGHTS = (7, 7, 1)
ROUND_NUMBERS = {
                 'spades': (101, 105, 109, 117, 121, 125),
                 'hearts': (103, 107, 111, 115, 119, 123),
                 'coin': (113,),}
ROUND_RESULT_FIELD_NAME = 'ROUND_RESULT:str'
ROUND_TIME = 30.03
KEYS_STORAGE_NAME = 'USERID:list'
SERVER_SEED = 'server_seed:str'
PUBLIC_SEED = 'public_seed:str'

# const values for experience amount evaluating
WIN_COEF = 1
LOSE_COEF = 1
CREDITS_TO_EXP_COEF = 1000


def record_work_time(function):
    """Засекает время работы функции"""
    def wrapper(*args, **kwargs):
        start = timezone.now()
        print(f"Time record from {__name__} for function {function.__name__}")
        print(f"Start at {start}")
        res = function(*args, **kwargs)
        end = timezone.now()
        print(f"End at {end}")
        delta = end - start
        print(f'Worked for {delta}')
        return res

    return wrapper


@shared_task
def sender():
    t = datetime.datetime.now()
    r.incr('round', 1)
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
    t = datetime.datetime.now()
    r.set('state', 'rolling', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    # достаёт из БД результат раунда
    round_number = int(r.get('round'))
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


@shared_task
def go_back():
    t = datetime.datetime.now()
    r.set('state', 'go_back', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'go_back',
                                                'previous_rolls': r.json().get('last_winners')
                                            })


@shared_task
def stop():
    t = datetime.datetime.now()
    r.set('state', 'stop', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    winner = r.get(ROUND_RESULT_FIELD_NAME)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'stopper',
                                                'winner': winner
                                            })


# @shared_task()
async def save_as_nested(keys_storage_name: str, dict_key: (str | int), bet_info: dict) -> bool:
    """
    Записывает ставку пользователя в redis.json()

    Args:
        keys_storage_name (str): name of the list where dict_key will be stored;
        dict_key (str|int): ключ в словаре - user-id для записи/доступа;
        bet_info (dict): информация о конкретной ставке пользователя в текущем раунде;
    """
    current_round = r.get('round')
    bet_to_redis_json = bet_info
    bet_to_redis_json['amount'] = {bet_info['bidCard']: bet_info['bidCount']}
    to_save = {dict_key: bet_to_redis_json}
    vice_versa_dict = {'spades': 'hearts', 'hearts': 'spades'}
    if round_bets := r.json().objkeys('round_bets'):
        if str(dict_key) in round_bets:
            previous_bet = r.json().get('round_bets', dict_key)
            if bet_info['bidCard'] in previous_bet['amount']:
                print(f'{bet_info["userName"]} Incrementing amount of bid for {bet_info["bidCount"]} to card:{bet_info["bidCard"]}')
                r.json().numincrby('round_bets', f'{dict_key}.amount.{bet_info["bidCard"]}', bet_info['bidCount'])
            elif vice_versa_dict.get(bet_info['bidCard']) in previous_bet['amount']:
                return False
            else:
                print(f'{bet_info["userName"]} Add new bid with amount {bet_info["bidCount"]} to card:{bet_info["bidCard"]}')
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
        round_result (str): победная карта текущего раунда

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
    print(f'Кол-во кредитов к начислению : {credits}')
    return credits


def save_round_results(bets_info):
    """Сохраняет результаты раунда

    Args:
        bets_info (dict): ставки
    """
    total_amount = 0
    winners = []
    round_result = r.get(ROUND_RESULT_FIELD_NAME)
    round_number = int(r.get('round'))
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
    except ObjectDoesNotExist:
        current_round = models.RouletteRound()
    current_round.rolled = True
    current_round.total_bet_amount = total_amount
    current_round.winners.set(winners)
    current_round.round_started = round_started
    current_round.save()
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

    print(f"Extracted keys: {bets_keys}", type(bets_keys))
    if not bets_keys:
        print('There were no bets for this round')
        return 1

    users = models.CustomUser.objects.filter(pk__in=list(map(lambda x: int(x), bets_keys)))
    print(f"Users with a bet: f{users}")

    # Get round results
    round_result = r.get(round_result_field_name)
    print(f"Current round result: {round_result}")

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
        user.detailuser.balance += eval_balance(user_bets['amount'], round_result)
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
                    'current_balance': user.detailuser.balance
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
                print(f"Rewards was given: {users_rewards}")

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
    print(f"Experience updated for {updated} users")
    if users_rewards:
        granted = OwnedCase.objects.bulk_create(users_rewards)
        print(f"Rewards granted:{granted}")

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
def generate_daily(day_hash_pk=None, update_rounds=True):
    """Генерирует хеши для получения результатов раундов и сами раунды"""
    # генерация хеша
    if day_hash_pk is None:
        try:
            try:
                # находит существующий хеш на день
                day_hash = models.DayHash.objects.get(date_generated=timezone.now().date())
            except ObjectDoesNotExist:
                # если хеша на день нет, создаёт новый
                day_hash = models.DayHash()
                day_hash.private_key = generate_private_key()
                day_hash.public_key = generate_public_key()
                day_hash.private_key_hashed = sha256(day_hash.private_key.encode()).hexdigest()
                day_hash.save()
        except IntegrityError:
            # если новый хеш создался во время выполнения функции в другом потоке, то достаёт его
            day_hash = models.DayHash.objects.get(date_generated=timezone.now().date())
    else:
        day_hash = models.DayHash.objects.get(pk=day_hash_pk)

    # генерация результатов раундов
    # определение количества раундов для генерации
    seconds_per_day = 24*60*60
    # при делении получается нецелое число - количество раундов округляется вверх
    rounds_per_day = math.ceil(seconds_per_day / ROUND_TIME)
    # print(rounds_per_day,'rounds per day')
    current_round = int(r.get('round'))
    # print(current_round,'current round')

    # получение следующих за текущим раундов для их обновления
    existing_rounds = models.RouletteRound.objects.filter(round_number__gte=current_round)
    existing_rounds_dict = {round.round_number: round for round in existing_rounds}
    # обновление старых и создание новых раундов
    roulette_rounds = []
    for round_number in range(current_round, current_round + rounds_per_day + 1):
        if round_number in existing_rounds_dict:
            if not update_rounds:
                continue
            round = existing_rounds_dict[round_number]
        else:
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
    # сохранение обновлённых раундов в БД
    if update_rounds:
        models.RouletteRound.objects.bulk_update(existing_rounds, ['round_roll', 'day_hash'])
    # сохранение новых раундов в БД
    models.RouletteRound.objects.bulk_create(roulette_rounds)
    # удаление дубликатов раундов
    models.RouletteRound.objects.filter(round_number__gte=current_round).exclude(day_hash=day_hash).delete()
    # считает количество выпавших на сегодня результатов рулетки
    # print('Generated rounds for this day:')
    # for result in ROUND_RESULTS:
    #     amount = models.RouletteRound.objects.filter(round_number__gte=current_round, round_roll=result).count()
    #     print(f"{result} = {amount}")


def setup_check_request_status(host_url, operation, id_shift, request_pk, user_pk, delay):
    """Запускает проверку статуса на сервере ботов через delay секунд"""
    check_request_status.apply_async(
        args=(host_url, operation, id_shift, request_pk, user_pk),
        countdown=delay
    )

@shared_task
def check_request_status(host_url, operation, id_shift, request_pk, user_pk):
    """Проверяет статус заявки на сервере ботов"""
    # удаляет из redis запись о заявке
    # r.delete(f"user_{operation}:{user_pk}")
    # r.delete(f"user_{operation}:{user_pk}:start")
    # создаёт url для получения статуса заявки
    url_get_status = f"{host_url}{operation}/get?id={request_pk + id_shift}"
    timeout = 2
    # попытка соединения с сервером ботов
    try:
        resp = requests.get(url_get_status, timeout=timeout)
        req_txt = resp.text
        info = resp.json()
    except (requests.ConnectionError, requests.Timeout):
        # планирование следующей попытки обновления статуса заявки
        setup_check_request_status(host_url, operation, id_shift, request_pk, 2*60)
        return
    # проверяет статус заявки
    if info.get('done'):
        if operation == 'refill':
            model = RefillRequest
        elif operation == 'withdraw':
            model = WithdrawalRequest
        else:
            print(f'Unknown request operation: {operation}')
            return
        # достаёт заявку из бд
        try:
            user_request = model.objects.get(pk=request_pk)
        except model.DoesNotExist as err:
            print(f'Request {request_pk} does not exist')
            return
        except Error:
            setup_check_request_status(host_url, operation, id_shift, request_pk, 2*60)
            return
        # проверяет, не была ли заявка закрыта ранее
        if user_request.status != 'open' or r.getex(f'close_{request_pk}:{operation}:bool', ex=10*60):
            print(f'Request {request_pk} already closed')
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
        try:
            if operation == 'refill':
                user_request.amount = info.get('refiil')
                if user_request.amount > 0:
                    detail_user = models.DetailUser.objects.get(user=user_request.user)
                    detail_user.balance += user_request.amount
                    detail_user.save()
            elif operation == 'withdraw':
                user_request.amount = info.get('withdraw')
                detail_user = models.DetailUser.objects.get(user=user_request.user)
                frozen_balance_remain = detail_user.frozen_balance - user_request.amount
                new_balance = max(0, detail_user.balance + frozen_balance_remain)
                detail_user.balance = new_balance
                detail_user.frozen_balance = 0
                detail_user.save()
            else:
                print(f'Unknown request operation: {operation}')
                return
            user_request.save()
        except Error as err:
            setup_check_request_status(host_url, operation, id_shift, request_pk, 2*60)
            return
        # банит пользователя, если его забанил сервер
        if info.get('ban'):
            try:
                ban = models.Ban.objects.get(user=user_request.user)
                ban.ban_site = True
                ban.save()
            except Error as err:
                print("Database error. Can't load a ban.")
                return


def check_round_number():
    """Проверяет, есть ли в redis счётчик числа раундов"""
    if r.get('round') is None:
        last_round = models.RouletteRound.objects.filter(rolled=True).aggregate(Max('round_number'))
        last_round_number = last_round.get('round_number__max')
        if last_round_number is None:
            last_round_number = 1
        r.set('round', last_round_number)


def check_rounds():
    """Проверяет, есть ли в БД раунды и создаёт их, если раундов нет"""
    try:
        day_hash = models.DayHash.objects.get(date_generated=timezone.now().date())
        # дополнит бд недостающими раундами, если их нет
        generate_daily(day_hash_pk=day_hash.pk)
    except ObjectDoesNotExist:
        generate_daily()


def initialize_rounds():
    """Проверяет, есть ли в redis номер текущего раунда, а в БД - сами раунды"""
    check_round_number()
    check_rounds()


initialize_rounds()
celery_app.add_periodic_task(ROUND_TIME, debug_task.s(), name=f'debug_task every 30.03')
celery_app.add_periodic_task(schedule=schedules.crontab(minute=0, hour=0), sig=generate_daily.s(), name='Генерация хеша каждый день')


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
                'current_balance': user.detailuser.balance
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
                'current_balance': user.detailuser.balance
            }
        }
        async_to_sync(channel_layer.group_send)(f'{user.id}_room', message)


def send_balance_delay(user_pk):
    send_balance.apply_async(args=(user_pk,), countdown=5)


def send_items_delay(user_pk):
    send_items.apply_async(args=(user_pk,), countdown=5)
