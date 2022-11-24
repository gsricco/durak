import os
import asyncio
from celery import Celery, shared_task
from channels.layers import get_channel_layer
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
app = Celery('configs')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(30.03, debug_task.s(), name='add every 10')


# @shared_task(bind=True)
# def sender(self):
#     print(self)
#     async_to_sync(channel_layer.group_send)('chat_go',
#                                             {
#                                                 'type': 'korney_task',
#                                                 'do': 'do_something'
#                                             }
#                                             )
#     print('konec')
#     return {"my_name": "Korney"}


# # @app.task
# @shared_task
# def debug_task():
#     sender.apply_async()
#     stop.apply_async(countdown=20)
#     generate_round_result.apply_async(countdown=20)


# @shared_task(bind=True)
# def stop(self):
#     print(self)
#     async_to_sync(channel_layer.group_send)('chat_go',
#                                             {
#                                                 'type':'stopper',

#                                             })


# # round results generation logic
# import random
# from redis import Redis
# # from ws_chat.tasks import process_bets

# r = Redis()

# ROUND_RESULTS = ('black', 'red', 'bonus')
# ROUND_RESULT_FIELD_NAME = 'round_result'
# KEYS_STORAGE_NAME = 'users_bets'


# @shared_task()
# def generate_round_result() -> int:
#     """Generates round result and stores it in redis
#     Returns:
#         int: return code
#     """
#     result = random.choice(ROUND_RESULTS)
#     r.set(ROUND_RESULT_FIELD_NAME, result)
#     print(r.get(ROUND_RESULT_FIELD_NAME))
    
#     return 0
