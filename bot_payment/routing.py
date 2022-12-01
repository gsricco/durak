from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/refill_payment/(?P<user>\w+)/$", consumers.RefillConsumer.as_asgi()),
]
