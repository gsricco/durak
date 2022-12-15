import datetime
import math
import uuid
from hashlib import sha256
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
from accaunts.models import Level

channel_layer = get_channel_layer()
r = Redis()
# ROUND_RESULTS = (
#                  ('spades', 101), ('hearts', 103),
#                  ('spades', 105), ('hearts', 107),
#                  ('spades', 109), ('hearts', 111),
#                  ('coin', 113),
#                  ('spades', 117), ('hearts', 115),
#                  ('spades', 121), ('hearts', 119),
#                  ('spades', 125), ('hearts', 123),)
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
        start = datetime.datetime.now()
        print(f"Time record from {__name__} for function {function.__name__}")
        print(f"Start at {start}")
        res = function(*args, **kwargs)
        end = datetime.datetime.now()
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
                                                'round': r.get('round').decode('utf-8')
                                            }
                                            )
    r.json().delete('round_bets')


@shared_task
def debug_task():
    t = datetime.datetime.now()
    sender.apply_async()
    # roll.apply_async(countdown=19.5)
    roll.apply_async(eta=t + datetime.timedelta(seconds=20))
    generate_round_result.apply_async(countdown=24, args=(True,))
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
    except ObjectDoesNotExist:
        # если раунда нет в БД, то произойдёт проверка текущего
        # и следующих раундов на день - если их нет, они создадутся
        check_rounds()
        current_round = models.RouletteRound.objects.get(round_number=round_number)
    result = current_round.round_roll
    current_round.rolled = True
    current_round.save()
    # result = random.choice(ROUND_RESULTS)
    result_c = random.choice(ROUND_NUMBERS[result])
    position = random.random()
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
    winner = r.get(ROUND_RESULT_FIELD_NAME).decode("utf-8")
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'stopper',
                                                'winner': winner
                                            })


# @shared_task()
async def save_as_nested(keys_storage_name: str, dict_key: (str | int), bet_info: dict) -> None:
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
    if round_bets := r.json().objkeys('round_bets'):
        if str(dict_key) in round_bets:
            previous_bet = r.json().get('round_bets', dict_key)
            if bet_info['bidCard'] in previous_bet['amount']:
                print(f'{bet_info["userName"]} Incrementing amount of bid for {bet_info["bidCount"]} to card:{bet_info["bidCard"]}')
                r.json().numincrby('round_bets', f'{dict_key}.amount.{bet_info["bidCard"]}', bet_info['bidCount'])
            else:
                print(f'{bet_info["userName"]} Add new bid with amount {bet_info["bidCount"]} to card:{bet_info["bidCard"]}')
                r.json().set('round_bets', f'{dict_key}.amount.{bet_info["bidCard"]}', bet_info['bidCount'])
        else:
            r.json().set('round_bets', f".{dict_key}", bet_to_redis_json)
    else:
        r.json().set('round_bets', ".", to_save)


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
            if bet_card == ('spades' or 'hearts'):
                credits += int(user_bet[bet_card])
            else:
                credits += int(user_bet[bet_card]) * 13
        # Возможно списание средств надо оставить на момент самой ставки
        # и убрать отсюда
        else:
            credits += - int(user_bet[bet_card])
    print(f'Кол-во кредитов к начислению : {credits}')
    return credits


def save_round_results(bets_keys, bets_info):
    """Сохраняет результаты раунда

    Args:
        bets_keys (dict): ключи ставок
        bets_info (dict): ставки
    """
    total_amount = 0
    winners = []
    round_result = r.get(ROUND_RESULT_FIELD_NAME).decode("utf-8")

    for user_pk, bet in bets_info.items():
        # накапливает общую сумму ставок
        total_amount += bet.get('bidCount', 0)
        # если пользователь ставил на победивший знак, то запоминает его
        if round_result in bet.get('amount', {}):
            winners.append(user_pk)

    # сохраняет раунд в БД
    round_number = r.get('round')
    round_started = datetime.datetime.fromtimestamp(int(r.get('start:time')) / 1000)
    # TODO: save round results to DB


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
    # получение всех ключей - id юзеров, который делали ставки в этом раунде
    bets_keys = r.json().objkeys('round_bets')
    # получаем информацию о всех ставках на текущий раунд
    bets_info = r.json().get('round_bets')

    print(f"Extracted keys: {bets_keys}", type(bets_keys))
    if not bets_keys:
        print('There were no bets for this round')
        return 1
    # make async in future
    users = models.CustomUser.objects.filter(pk__in=list(map(lambda x: int(x), bets_keys)))
    print(f"Users with a bet: f{users}")

    # Get round results
    round_result = r.get(round_result_field_name).decode("utf-8")
    print(f"Current round result: {round_result}")

    # список с наградами пользователей за новые уровни -
    # после обработки всех ставок награды сохранятся в БД через bulk_create
    users_rewards = []
    # обработка ставок для каждого пользователя
    for user in users:
        lev = Level.objects.last()
        max_level = lev.level
        max_exp = lev.experience_range.upper
        # получение информации о ставке пользователя
        bet_key = user.pk
        # получаем словарь со всеми ставками юзера
        user_bets = bets_info[str(bet_key)]
        # расчёт количества начисляемого опыта
        xp = eval_experience(user_bets['amount'], round_result)
        # расчёт и начисление баланса без сохранения в БД
        user.detailuser.balance += eval_balance(user_bets['amount'], round_result)
        # добавление опыта пользователю без сохранения в БД
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
            async_to_sync(channel_layer.send)(channel_name, message)
        # после получения опыта пробует начислить пользователю уровни
        rewards_for_level = user.give_level()

        # если уровень пользователя изменился
        if prev_level != user.level.level:
            if channel_name := bets_info[str(bet_key)]['channel_name']:
                level = user.level.level
                new_level = level + 1
                if level == max_level:
                    new_level = 'max'
                message = {
                    "type": "send_new_level",
                    "lvlup": {
                        "type": "send_new_level",
                        "new_lvl": new_level,
                        "lvlup": {
                            "new_lvl": new_level,
                            "levels": level,
                        },

                        "levels": level,
                    },
                }
                async_to_sync(channel_layer.send)(channel_name, message)

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
                    async_to_sync(channel_layer.send)(channel_name, message)
        send_exp(user, bets_info[str(bet_key)]['channel_name'])
    detail_users = [user.detailuser for user in users]
    update_balance = models.DetailUser.objects.bulk_update(detail_users, ['balance'])
    updated = models.CustomUser.objects.bulk_update(users, ['experience', 'level'])
    print(f"Experience updated for {updated} users")
    if users_rewards:
        granted = OwnedCase.objects.bulk_create(users_rewards)
        print(f"Rewards granted:{granted}")

    return 0


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
    async_to_sync(channel_layer.group_send)(f'{user.username}_room', message)


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
        process_bets.apply_async(args=(KEYS_STORAGE_NAME, ROUND_RESULT_FIELD_NAME,))

    return 0


@shared_task
@record_work_time
def generate_daily(day_hash_pk=None, update_rounds=True):
    """Генерирует хеши для получения результатов раундов и сами раунды"""
    # генерация хеша
    if day_hash_pk is None:
        try:
            day_hash = models.DayHash.objects.get(date_generated=datetime.date.today())
        except ObjectDoesNotExist:
            day_hash = models.DayHash()
            day_hash.private_key = generate_private_key()
            day_hash.public_key = generate_public_key()
            day_hash.save()
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
    # считает количество выпавших на сегодня результатов рулетки
    # print('Generated rounds for this day:')
    # for result in ROUND_RESULTS:
    #     amount = models.RouletteRound.objects.filter(round_number__gte=current_round, round_roll=result).count()
    #     print(f"{result} = {amount}")


def check_round_number():
    """проверяет, есть ли в redis счётчик числа раундов"""
    if r.get('round') is None:
        last_round = models.RouletteRound.objects.filter(rolled=True).aggregate(Max('round_number'))
        last_round_number = last_round.get('round_number__max')
        if last_round_number is None:
            last_round_number = 1
        r.set('round', last_round_number)


def check_rounds():
    """проверяет, есть ли в БД раунды и создаёт их, если раундов нет"""
    try:
        day_hash = models.DayHash.objects.get(date_generated=datetime.date.today())
        # дополнит бд недостающими раундами, если их нет
        generate_daily(
            day_hash_pk=day_hash.pk,
            update_rounds=False
        )
    except ObjectDoesNotExist:
        generate_daily()


def initialize_rounds():
    """Проверяет, есть ли в redis номер текущего раунда, а в БД - сами раунды"""
    check_round_number()
    check_rounds()


initialize_rounds()

celery_app.add_periodic_task(ROUND_TIME, debug_task.s(), name=f'debug_task every 30.03')
celery_app.add_periodic_task(schedule=schedules.crontab(minute=1, hour=0), sig=generate_daily.s(), name='Генерация хеша каждый день')
