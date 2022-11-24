import json
from channels.generic.websocket import AsyncWebsocketConsumer
from . import tasks
# from configs.celery import debug_task


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'go'
        self.room_group_name = "chat_%s" % self.room_name
        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
        )
        # a = debug_task.apply_async()
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        if text_data_json.get('online') == "online":
            online = self.channel_layer.receive_count
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "get_online",
                                       "get_online": online
                                       }
            )
        elif text_data_json.get('bet'):
            # expected to have bet like {"bet": {"credits": 1000, "placed": "black"}}
            user = self.scope.get('user')
            if user and user.isauthenticated():
                user_pk = user.pk
                bet = text_data_json.get('bet')
                self.save_bet(bet, user_pk)
        else:
            message = text_data_json["message"]
            user = text_data_json["user"]
            avatar = text_data_json["avatar"]
            rubin = text_data_json.get("rubin")
            # online = self.channel_layer.receive_count
            await self.channel_layer.group_send(
                self.room_group_name, {"type": "chat_message",
                                       "message": message,
                                       "user": user,
                                       "avatar": avatar,
                                       "rubin": rubin,
                                       }
            )
        # self.send(text_data=json.dumps({'message': message}))
    async def get_online(self, event):
        print(event['get_online'])
        online = event['get_online']
        await self.send(text_data=json.dumps({
            "get_online": online
        }))
    async def chat_message(self, event):
        user = event.get('user')
        message = event.get("message")
        avatar = event.get("avatar")
        rubin = event.get("rubin")
        # online = event.get("online")
        await self.send(text_data=json.dumps({"message": message,
                                              "user": user,
                                              "avatar": avatar,
                                              "rubin": rubin,
                                              # "online": online
                                              }))
# начинает отсчёт
    async def korney_task(self, event):
        await self.send(text_data=json.dumps({
            "roulette": 20,
        }))
# начинает крутиться рулетка
    async def rolling(self, event):
        await self.send(text_data=json.dumps({
            "roll": 'rolling'
        }))

    async def stopper(self, event):
        await self.send(text_data=json.dumps({
            "stop": "stopping"
        }))       

    async def save_bet(self, bet, user_pk):
        storage_name = tasks.KEYS_STORAGE_NAME
        tasks.save_as_nested.apply_async(args=(storage_name, user_pk, bet))