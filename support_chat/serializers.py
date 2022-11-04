
from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

from accaunts.models import CustomUser
from .models import Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'avatar')


class MessageGetSerializer(serializers.Serializer):
    user_posted = UserSerializer()
    user_received = UserSerializer()
    message = serializers.CharField()
    file_message = serializers.FileField()
    date = serializers.DateTimeField()


# class MessageFileCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         parser_classes = (FileUploadParser,)
#         fields = ('file_message',)

class MessageCreateSerializer(serializers.ModelSerializer):
    # file_message = MessageFileCreateSerializer(default=None)
    class Meta:
        model = Message
        fields = ('message', 'file_message')
