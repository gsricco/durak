from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from accaunts.models import CustomUser
from .models import Message
from .serializers import MessageGetSerializer, MessageCreateSerializer


class MessageViewSet(viewsets.ViewSet):
    """API для работы с сообщениями чата подержки"""
    def list(self, request):
        """Список всех сообщений авторизованного пользователя"""
        user = request.user
        queryset = Message.objects.filter(Q(user_posted=user) | Q(user_received=user))
        serializer = MessageGetSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Выборка всех сообщений по конкретному пользователю"""
        user = CustomUser.objects.all()
        user = get_object_or_404(user, username=pk)
        data = Message.objects.filter(Q(user_posted=user.id) | Q(user_received=user.id))
        serializer = MessageGetSerializer(data, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Сохранение сообщения пользователя"""
        ### Или сделать с выборкой авториз пользователя, но как автоматом знать принимающую сторону
        file = request.data.get('file_message')
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['file_message'] = file
        serializer.save()
        return Response(status=200)
