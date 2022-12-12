import datetime
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
from django.core.exceptions import ObjectDoesNotExist

channel_layer = get_channel_layer()
r = Redis()
# ROUND_RESULTS = ('coin',)
ROUND_RESULTS = ('spades', 'hearts', 'coin')
ROUND_RESULT_FIELD_NAME = 'ROUND_RESULT:str'
KEYS_STORAGE_NAME = 'USERID:list'
SERVER_SEED = 'server_seed:str'
PUBLIC_SEED = 'public_seed:str'

# const values for experience amount evaluating
WIN_COEF = 1
LOSE_COEF = 1
CREDITS_TO_EXP_COEF = 1000


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
    sender.apply_async()
    roll.apply_async(countdown=20)
    generate_round_result.apply_async(countdown=24, args=(True,))
    stop.apply_async(countdown=25)
    go_back.apply_async(countdown=28)


@shared_task
def roll():
    t = datetime.datetime.now()
    r.set('state', 'rolling', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    result = roll_fair(ROUND_RESULTS, weights=(7, 7, 1))
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'rolling',
                                                "winner": result,
                                            })
    r.set(ROUND_RESULT_FIELD_NAME, result)

@shared_task
def go_back():
    t = datetime.datetime.now()
    r.set('state', 'go_back', ex=30)
    r.set(f'start:time', str(int(t.timestamp() * 1000)), ex=30)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'go_back',
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


def eval_experience(user_bet: dict, round_result:str) -> int:
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
                message = {
                    "type": "send_new_level",
                    "lvlup": {
                        "new_lvl": user.level.level + 1,
                        "levels": user.level.level ,
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
    print('отправился опыт')
    max_exp = user.level.experience_range.upper
    min_exp = user.level.experience_range.lower
    delta_exp = max_exp - min_exp
    exp = user.experience
    percent_exp_line = (exp - min_exp) / (delta_exp / 100)
    if percent_exp_line >= 100:
        percent_exp_line -= 100
    message = {
        "type": "send_new_level",
        "expr": {
            "min_exp": min_exp,
            "max_exp": max_exp,
            "expr":exp,
            "percent":percent_exp_line,
        },
    }
    async_to_sync(channel_layer.send)(channel_name, message)


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


def roll_fair(round_results: list, weights: tuple=None) -> str:
    """Генерирует результат раунда через хеш (как на csgoempire.com)

    Args:
        round_results (list): массив с возможными результатами раунда (результат - str)
        weights (tuple, optional): вес соответствующего результата. Defaults to None.

    Returns:
        str: результат раунда
    """
    # генерация весов по умолчание, если они не были переданы
    if weights is None:
        weights = (1 for _ in range(len(round_results)))
    # получаем server_seed из redis
    server_seed_byte = r.get(SERVER_SEED)
    server_seed = ''
    if server_seed_byte is None:
        server_seed = generate_private_key()
    else:
        server_seed = server_seed_byte.decode("utf-8")
    # получаем public_seed из redis
    public_seed_byte = r.get(PUBLIC_SEED)
    public_seed = ''
    if public_seed_byte is None:
        public_seed = generate_public_key()
    else:
        public_seed = public_seed_byte.decode("utf-8")
    # получаем номер раунда из redis
    round_number_byte = r.get('round')
    round_number = 1
    if not round_number_byte is None:
        round_number = int(round_number_byte)
    # генерация хеша раунда
    unhashed_round = f"{server_seed}-{public_seed}-{round_number:06d}"
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
    """Generates round result and stores it in redis

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
def generate_daily_hash():
    """Генерирует хеши для получения результатов раундов"""
    day_hash = models.DayHash()
    day_hash.private_key = generate_private_key()
    day_hash.public_key = generate_public_key()
    day_hash.save()
    r.set(SERVER_SEED, day_hash.private_key)
    r.set(PUBLIC_SEED, day_hash.public_key)


# считывает из БД ключи для генерации результатов раунда, если их нет в редис
r.delete(SERVER_SEED)
if r.get(SERVER_SEED) is None or r.get(PUBLIC_SEED) is None:
    try:
        day_hash = models.DayHash.objects.get(date_generated=datetime.date.today())
        r.set(SERVER_SEED, day_hash.private_key)
        r.set(PUBLIC_SEED, day_hash.public_key)
    except ObjectDoesNotExist:
        # создаёт в БД ключи для текущего дня
        generate_daily_hash()
        

celery_app.add_periodic_task(30.03, debug_task.s(), name='debug_task every 30.03')
celery_app.add_periodic_task(schedule=schedules.crontab(minute=1, hour=0), sig=generate_daily_hash.s(), name='Генерация хеша каждый день')
