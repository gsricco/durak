from rest_framework import serializers
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser

from accaunts.models import CustomUser
from .models import Message, UserChatRoom



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'avatar')


class MessageGetSerializer(serializers.Serializer):
    user_posted = UserSerializer()
    # user_received = UserSerializer()
    message = serializers.CharField()
    file_message = serializers.FileField()
    date = serializers.DateTimeField()
    is_sell_item = serializers.BooleanField()


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
        ordering = [-1]
class RoomMessageSerializer(serializers.ModelSerializer):
    user_posted = UserSerializer()
    class Meta:
        model =  UserChatRoom
        fields = ('message')


# class RoomAdminMessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model =  AdminMessage
#         fields = ('user_posted','message')

class RoomSerializer(serializers.ModelSerializer):

    message = MessageGetSerializer(many=True)
    class Meta:
        model = UserChatRoom
        fields = ('room_id','message')

class NoReadSerializer(serializers.Serializer):
    not_read_counter = serializers.IntegerField()
    not_read_owner_counter = serializers.IntegerField()
class UserFromRoomSerializer(serializers.Serializer):
    username = serializers.CharField()
class OnlyRoomSerializer(serializers.Serializer):
    user = UserFromRoomSerializer()
    room_id = serializers.CharField()
    notread = NoReadSerializer()

