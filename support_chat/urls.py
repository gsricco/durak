from django.urls import path, include
from rest_framework import routers

from support_chat.views import MessageViewSet

app_name = 'support_chat'

router = routers.DefaultRouter()
router.register(r'message', MessageViewSet, basename='message_chat')


urlpatterns = [
    path('', include(router.urls)),

]