import os
from celery import Celery
from channels.layers import get_channel_layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configs.settings')
app = Celery('configs')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
channel_layer = get_channel_layer()


# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#    sender.add_periodic_task(30.03, tasks.debug_task.s(), name='add every 30')


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

# @shared_task
# def sender():
#     async_to_sync(channel_layer.group_send)('chat_go',
#                                             {
#                                                 'type': 'korney_task',
#                                                 'do': 'do_something'
#                                             }
#                                             )
#     print('konec')
#     return {"my_name": "Korney"}
#
# @shared_task
# def debug_task():
#     sender.apply_async()
#     roll.apply_async(countdown=20)
#     stop.apply_async(countdown=25)
#     go_back.apply_async(countdown=28)
#
# @shared_task
# def roll():
#     async_to_sync(channel_layer.group_send)('chat_go',
#                                             {
#                                                 'type': 'rolling',
#                                             })
# @shared_task
# def stop():
#     # print(self.__dict__)
#     async_to_sync(channel_layer.group_send)('chat_go',
#                                             {
#                                                 'type': 'stopper',
#
#                                             })
# @shared_task
# def go_back():
#     async_to_sync(channel_layer.group_send)('chat_go',
#                                             {
#                                                 'type': 'go_back',
#                                             })


# @shared_task
# def debug_task():
#     redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)
#     json_data = {'message': 'Hello to all connected clients', 'date': '2019-02-02', 'title': 'welcome'}
#     redis_client.publish('roulette', json.dumps(json_data))
