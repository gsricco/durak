from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response

from accaunts.models import CustomUser
from .models import Message, UserChatRoom
from .serializers import MessageGetSerializer, MessageCreateSerializer, RoomSerializer


class MessageViewSet(viewsets.ViewSet):
    """API для работы с сообщениями чата подержки"""
    def list(self, request):
        """Список всех сообщений авторизованного пользователя"""
        user = request.user
        queryset = Message.objects.filter(user_posted=user)
        serializer = MessageGetSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """Выборка всех сообщений по конкретному пользователю"""
        user = CustomUser.objects.all()
        user = get_object_or_404(user, username=pk)
        data = Message.objects.filter(user_posted=user.id)
        serializer = MessageGetSerializer(data, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Сохранение сообщения пользователя"""
        ### Или сделать с выборкой авториз пользователя, но как автоматом знать принимающую сторону
        # if not request.user.is_authenticated:            ## ПРоставить на методах???
        #     return Response(status=401)
        user = request.user
        file = request.data.get("file_message")
        serializer = MessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data["file_message"] = file
        serializer.validated_data["user_posted"] = user
        # Для ПАШИ - Если просто тестить отправку(не с сайта), то надо закоментить стр.31 и 36. А раскоментить надо стр38
        # serializer.validated_data["user_posted"] = CustomUser.objects.get(username='admin')
        serializer.save()
        return Response(status=200)

class RoomViewSet(viewsets.ViewSet):
    def retrieve(self,request,pk=None):
        room = get_object_or_404(UserChatRoom, room_id=pk)
        serializer = RoomSerializer(room)
        return Response(serializer.data)