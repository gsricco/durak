from django.urls import path, include
from rest_framework import routers

from support_chat.views import MessageViewSet


router_get = routers.DefaultRouter()
router_get.register(r'message', MessageViewSet, basename='message')


urlpatterns = [
    path('', include(router_get.urls)),

]