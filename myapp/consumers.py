from channels.generic.websocket import AsyncWebsocketConsumer
import json


class RealmConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = "global"
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("receiveed from client",text_data)
        data = json.loads(text_data)
        message = data['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        print("Sending to client:", event['message'])
        message = event['message']

        await self.send(text_data=json.dumps({
            'message': f"Aetheria says: {message}"
        }))
