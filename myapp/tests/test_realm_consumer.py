import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from websocketrealms.asgi import application
from myapp.models import ChatMessage
from asgiref.sync import sync_to_async

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_realm_consumer_connect_send_recieve():
    user = await sync_to_async(User.objects.create_user)(
        username='tester', password='pass123'
    )

    communicator = WebsocketCommunicator(application, "/ws/realm/")
    communicator.scope['user'] = user

    connected, _ = await communicator.connect()
    assert connected

    await communicator.send_json_to({"message": "Hello from test"})

    response = await communicator.receive_json_from()
    assert response["message"] == "tester: Hello from test"

    exists = await sync_to_async(ChatMessage.objects.filter(
        user=user, message="Hello from test").exists)()
    assert exists
    await communicator.disconnect()
