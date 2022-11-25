from rest_framework import routers
from django.urls import path, include

from support_chat.views import MessageViewSet, RoomViewSet


router = routers.DefaultRouter()

# чат поддержки
router.register(r'message', MessageViewSet, basename='support_chat')
router.register(r'message_v2', RoomViewSet, basename='support_chat_v2')


urlpatterns = [
    path('api/v1/', include(router.urls)),
]
