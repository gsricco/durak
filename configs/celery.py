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


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(30.03, debug_task.s(), name='add every 10')


def sender():
    print('HI Korney ANd OLEG', '*' * 50)
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
    sender()
