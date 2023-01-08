from django.urls import re_path

from .consumers import ChatConsumer

websocket_urlpatterns = [
    # re_path(r"ws/chat/", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/chat/(?P<user>\w+)/$", ChatConsumer.as_asgi()),
]
