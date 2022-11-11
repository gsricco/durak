import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'go'
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        user = text_data_json["user"]
        avatar = text_data_json["avatar"]
        rubin = text_data_json.get("rubin")
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat_message",
                                   "message": message,
                                   "user": user,
                                   "avatar": avatar,
                                   "rubin": rubin
                                   }
        )
        # self.send(text_data=json.dumps({'message': message}))

    async def chat_message(self, event):
        user = event['user']
        message = event["message"]
        avatar = event["avatar"]
        rubin = event.get("rubin")
        await self.send(text_data=json.dumps({"message": message,
                                              "user": user,
                                              "avatar": avatar,
                                              "rubin": rubin
                                              }))
