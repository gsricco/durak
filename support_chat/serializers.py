from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser

from .models import Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')


class MessageGetSerializer(serializers.Serializer):
    user_posted = UserSerializer()
    user_received = UserSerializer()
    message = serializers.CharField()
    file_message = serializers.FileField()
    date = serializers.DateTimeField()


class MessageFileCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        parser_classes = (MultiPartParser, FormParser)
        fields = ('file_message',)


class MessageCreateSerializer(serializers.ModelSerializer):
    file_message = MessageFileCreateSerializer()
    class Meta:
        model = Message
        fields = ('user_posted', 'user_received', 'message', 'file_message')
