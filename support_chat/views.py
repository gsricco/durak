from django.db.models import Q
from rest_framework import viewsets
from rest_framework.response import Response

from .models import Message
from .serializers import MessageGetSerializer, MessageCreateSerializer


class MessageViewSet(viewsets.ViewSet):
    """API для работы с сообщениями чата подержки"""
    def list(self, request):
        """Список всех сообщений авторизованного юзера"""
        user = request.user
        queryset = Message.objects.filter(Q(user_posted=user) | Q(user_received=user))
        print(request.user)
        serializer = MessageGetSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk='admin'):
        """Выборка по всех сообщений по конкретному юзеру"""
        data = Message.objects.filter(Q(user_posted=pk) | Q(user_received=pk))
        serializer = MessageGetSerializer(data)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Сохранение сообщения авторизованного юзера"""
        # Сделать привязку к авторизованному юзеру или к админу.
        # Как в админке реализовать отправку сообщения от админа???
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=200)

