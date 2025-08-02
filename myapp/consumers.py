from channels.generic.websocket import AsyncWebsocketConsumer
import json


class RealmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "chat_global"
        user = self.scope["user"]

        if user.is_anonymous:
            await self.close()
        else:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            print(f" {user.username} connected.")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"🔌 {self.scope['user'].username} disconnected.")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope["user"]

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': f"{user.username}: {message}",
            }
        )
        print(f" {user.username} said: {message}")

    async def chat_message(self, event):
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': message
        }))
