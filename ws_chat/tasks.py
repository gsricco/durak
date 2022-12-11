import datetime
from configs import celery_app
from celery import shared_task
from redis import Redis
from asgiref.sync import async_to_sync
from accaunts import models
from caseapp.models import OwnedCase
from channels.layers import get_channel_layer
import random
from accaunts.models import Level

channel_layer = get_channel_layer()
r = Redis()
# ROUND_RESULTS = ('coin',)
ROUND_RESULTS = (
                 ('spades', 101), ('hearts', 103),
                 ('spades', 105), ('hearts', 107),
                 ('spades', 109), ('hearts', 111),
                 ('coin', 113),
                 ('spades', 117), ('hearts', 115),
                 ('spades', 121), ('hearts', 119),
                 ('spades', 125), ('hearts', 123),)
# ROUND_RESULTS = ('spades', 'hearts', 'coin')
ROUND_RESULT_FIELD_NAME = 'ROUND_RESULT:str'
KEYS_STORAGE_NAME = 'USERID:list'

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
    result = random.choice(ROUND_RESULTS)
    position = random.random()
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'rolling',
                                                "winner": result[0],
                                                "c": result[1],
                                                "p": position
                                            })
    r.set(ROUND_RESULT_FIELD_NAME, result[0])
    # Логика последних 8 побед
    if not (r.exists('last_winners')):
        r.json().set('last_winners', '.', [])
    r.json().arrappend('last_winners', '.', result[0])
    if arr_len := r.json().arrlen('last_winners') > 8:
        r.json().arrtrim('last_winners', '.', arr_len-8, -1)

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
                new_level = level +1
                if level == max_level:
                    new_level = 'max'
                message = {
                    "type": "send_new_level",
                    "lvlup": {
                        "new_lvl": new_level,   "type": "send_new_level",
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

    max_exp = user.level.experience_range.upper
    min_exp = user.level.experience_range.lower
    delta_exp = max_exp - min_exp
    exp = user.experience
    percent_exp_line = (exp - min_exp) / (delta_exp / 100)
    if percent_exp_line >= 100:
        percent_exp_line -= 100
    if percent_exp_line == max_exp:
        percent_exp_line = 100
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


celery_app.add_periodic_task(30.03, debug_task.s(), name='debug_task every 30.03')
