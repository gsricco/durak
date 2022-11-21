import json
from asgiref.sync import sync_to_async, async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer
from accaunts.models import CustomUser
from support_chat.models import Message, UserChatRoom
from support_chat.serializers import RoomSerializer


class ChatConsumer(AsyncWebsocketConsumer):

    @sync_to_async
    def create_or_get_support_chat_room(self, message):  # получает или создает чат рум
        if message.get('user'):
            chat_room, created = UserChatRoom.objects.get_or_create(room_id=message.get('user'))
            return chat_room

    @sync_to_async
    def save_user_message(self, room, message):  # сохраняет сообщение в бд
        if message.get('user'):
            user = CustomUser.objects.get(username=message.get('user')).pk
            user_mess = Message(user_posted_id=user, message=message.get('message'))
            user_mess.save()
            room.message.add(user_mess, bulk=False)
            return user_mess

    @sync_to_async()
    def send_json(self, channel, room_name):
        try:
            room_data = UserChatRoom.objects.get(room_id=room_name)
            serializer = RoomSerializer(room_data)
            channel_layer = get_channel_layer()
            for i in serializer.data.get('message')[::-1]:
                async_to_sync(channel_layer.send)(channel, {"type": "chat_message",
                                                            "chat_type": "support",
                                                            "message": i['message'],
                                                            "user": i['user_posted'],
                                                            })
        except:
            pass
    async def connect(self):
        user = self.scope['user']
        self.room_name = 'go'  # self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        await self.send_online(0)
        await self.send_json(self.channel_name, user)

    async def send_online(self, num):
        online = self.channel_layer.receive_count + num
        await self.channel_layer.group_send(self.room_group_name, {"type": "get_online", "get_online": online})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.send_online(-1)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        if text_data_json.get('chat_type') == 'support':
            room = await self.create_or_get_support_chat_room(text_data_json)
            await self.save_user_message(room, text_data_json)
            await self.channel_layer.send(
                self.channel_name, {"type": "chat_message",
                                       "chat_type": "support",
                                       "message": text_data_json["message"],
                                       "user": text_data_json["user"], })

        elif text_data_json.get('chat_type') == 'all_chat':
            message = text_data_json["message"]
            user = text_data_json["user"]
            avatar = text_data_json["avatar"]
            rubin = text_data_json.get("rubin")
            chat_type = text_data_json.get('chat_type')
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message",
                                       "chat_type": chat_type,
                                       "message": message,
                                       "user": user,
                                       "avatar": avatar,
                                       "rubin": rubin,
                                       }
            )

    async def get_online(self, event):
        # print(event['get_online'])
        online = event['get_online']
        await self.send(text_data=json.dumps({
            "get_online": online
        }))

    async def chat_message(self, event):
        # print(event, 'Это event')
        chat_type = event.get('chat_type')
        # print(chat_type)
        user = event.get('user')
        message = event.get("message")
        avatar = event.get("avatar")
        rubin = event.get("rubin")
        # online = event.get("online")
        await self.send(text_data=json.dumps({"message": message,
                                              "chat_type": chat_type,
                                              "user": user,
                                              "avatar": avatar,
                                              "rubin": rubin,
                                              # "online": online
                                              }))
