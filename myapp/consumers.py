import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from myapp.models import ChatMessage


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
            print(f"{user.username} connected.")

            messages = await database_sync_to_async(
                lambda: list(ChatMessage.objects.select_related('user').order_by('timestamp')[:20])
            )()

            for msg in messages:
                await self.send(text_data=json.dumps({
                    'message': f"{msg.user.username} : {msg.message}"
                }))

    async def disconnect(self, close_code):
        # disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"{self.scope['user'].username} disconnected.")

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "")
        user = self.scope["user"]

        if message.strip() == "":
            return

        await self.save_message(user, message)

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

    @database_sync_to_async
    def save_message(self, user, message):
        return ChatMessage.objects.create(user=user, message=message)
