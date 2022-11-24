from configs.celery import app
from redis import Redis
from accaunts import models
from django.db.models.query import QuerySet
from asgiref.sync import sync_to_async

r = Redis()


@app.task()
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


WIN_COEF = 1
LOSE_COEF = 1
CREDITS_TO_EXP_COEF = 1000 

def eval_experience(credits: int, bet: str, round_result: str) -> int:
    """Evaluetes experience amount for bet.

    Args:
        credits (int): amount of credits placed on the bet
        bet (str): bet placed
        round_result (str): a round result - the winning bet
    """
    experience = credits // CREDITS_TO_EXP_COEF
    experience *= WIN_COEF if bet == round_result else LOSE_COEF

    return experience


def add_experience_field(bets: dict, round_result: str, exp_field_name: str='experience') -> None:
    """Adds experience field to bets dict.

    Args:
        bets (dict): dict with bets
        round_result (str): a result of a round
        exp_field_name (str)='experience': name of an experience field
    """
    for bet in bets:
        credits = bet.get('credits')
        placed_bet = bet.get('placed')
        bet[exp_field_name] = eval_experience(credits, placed_bet, round_result)


@app.task()
def process_round_results(bets: dict, users: QuerySet, round_result: str) -> None:
    """Processes round results for users that placed a bet

    Args:
        bets (dict): bets stored here and can be accessed by user's pk as a key
        users (QuerySet): users that placed a bet
        round_result (_type_): a result of a roulette round
    """

    add_experience_field(bets, round_result)

    # add experience to user (later here can be added other logic: credits operations and so one)
    for user in users:
        bet = bets.get(user.pk)
        if bet:
            user.experience += bet.get('experience')
    
    models.CustomUser.objects.bulk_update(users, ['experience'])


ROUND_RESULT_FIELD_NAME = 'round_result'

@app.task()
def process_bets(keys_storage_name: str) -> None:
    """
    Processes bets represented by dicts that can be accesed by keys stored in keys_storage_name list in redis.
    Args:
        keys_storage_name (str): name of the list in redis where bets keys are stored
    """
    # Get bets keys from redis. Bets keys are expected to be users pks
    bets_keys = r.lpop(keys_storage_name, r.llen(keys_storage_name))
    print(f"Extracted keys: f{bets_keys}")

    # Get bets from redis
    bets_keys_str = [str(key) for key in bets_keys]
    bets = {key: r.hgetall(key) for key in bets_keys_str}
    print(f"Extracted bets: f{bets}")

    # Get users that placed a bet
    users = sync_to_async(models.CustomUser.objects.filter)(pk__in=bets_keys_str)
    print(f"Users with a bet: f{users}")

    # Get round results
    round_result = r.get(ROUND_RESULT_FIELD_NAME)

    # Add experience to users
    process_round_results.apply_async(bets, users, round_result)    
