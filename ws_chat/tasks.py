from configs import celery_app
from celery import shared_task
from redis import Redis
from asgiref.sync import async_to_sync
from accaunts import models
from channels.layers import get_channel_layer
import random

channel_layer = get_channel_layer()
r = Redis()

ROUND_RESULTS = ('black', 'red', 'bonus')
ROUND_RESULT_FIELD_NAME = 'ROUND_RESULT:str'
KEYS_STORAGE_NAME = 'USERID:list'

# const values for experience amount evaluating
WIN_COEF = 1
LOSE_COEF = 1
CREDITS_TO_EXP_COEF = 1000 


@shared_task(bind=True)
def sender(self):
    print(self)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type': 'korney_task',
                                                'do': 'do_something'
                                            }
                                            )
    print('konec')
    return {"my_name": "Korney"}


# @app.task
@shared_task
def debug_task():
    sender.apply_async()
    stop.apply_async(countdown=20)
    generate_round_result.apply_async(countdown=20, args=(True,))


@shared_task(bind=True)
def stop(self):
    print(self)
    async_to_sync(channel_layer.group_send)('chat_go',
                                            {
                                                'type':'stopper',

                                            })


@shared_task()
def save_as_nested(keys_storage_name: str, dict_key: (str|int), dictionary: dict) -> None:
    """
    Creates a nested structure imitation in redis.

    Args:
        keys_storage_name (str): name of the list where dict_key will be stored;
        dict_key (str|int): name of the key to acces dict;
        dictionary (dict): dict to store.
    """
    with r.pipeline() as pipe:
        pipe.rpush(keys_storage_name, dict_key)
        pipe.hmset(dict_key, dictionary)
        pipe.execute()
    print(f"Hi from save_as_nested. {r.hgetall(dict_key)}")


def eval_experience(credits: int, bet: str, round_result: str) -> int:
    """Evaluates experience amount for bet.

    Args:
        credits (int): amount of credits placed on the bet
        bet (str): bet placed
        round_result (str): a round result - the winning bet

    Returns:
        int: evaluated amount of experience
    """
    experience = credits // CREDITS_TO_EXP_COEF
    experience *= WIN_COEF if bet == round_result else LOSE_COEF

    return experience


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
    # Get bets keys from redis. Bets keys are expected to be users pks
    bets_keys = r.lpop(keys_storage_name, r.llen(keys_storage_name))
    print(f"Extracted keys: f{bets_keys}")
    if bets_keys == None:
        print('There were no bets for this round')
        return 1
    
    user_ids = [key.decode("utf-8") for key in bets_keys]

    # Get bets from redis
    # bets = {key: dict(r.hgetall(key)) for key in bets_keys_str}
    # print(f"Extracted bets: f{bets}")

    # Get users that placed a bet

    # make async in future
    users = models.CustomUser.objects.filter(pk__in=user_ids)
    print(f"Users with a bet: f{users}")

    # Get round results
    round_result = r.get(round_result_field_name).decode("utf-8")
    print(f"Current round result: {round_result}")

    # Add experience to users
    for user in users:
        bet_key = user.pk
        credits_amount_byte = r.hget(bet_key, "credits")
        credits_amount = int(credits_amount_byte) if credits_amount_byte else 0
        placed_bet_byte = r.hget(bet_key, "placed")
        placed_bet = placed_bet_byte.decode("utf-8") if placed_bet_byte else None

        experience = eval_experience(credits_amount, placed_bet, round_result)

        user.experience += experience
        print(f"Bet by {user.pk} amount {credits_amount} on {placed_bet} results {experience} exp")
    
    # make async in future
    models.CustomUser.objects.bulk_update(users, ['experience'])
    print("Experience updated")

    return 0


@shared_task()
def generate_round_result(process_after_generating: bool=False) -> int:
    """Generates round result and stores it in redis

    Args:
        process_after_generating (bool): defines whether to process round results after its generating or not

    Returns:
        int: return code
    """
    result = random.choice(ROUND_RESULTS)
    r.set(ROUND_RESULT_FIELD_NAME, result)
    print(r.get(ROUND_RESULT_FIELD_NAME))

    if process_after_generating:
        process_bets.apply_async(args=(KEYS_STORAGE_NAME, ROUND_RESULT_FIELD_NAME,))
    
    return 0


celery_app.add_periodic_task(30.03, debug_task.s(), name='debug_task every 30.03')
