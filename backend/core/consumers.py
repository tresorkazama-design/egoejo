from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import ChatThread, Poll


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.thread_id = int(self.scope['url_route']['kwargs']['thread_id'])
        self.group_name = f"chat_thread_{self.thread_id}"
        user = self.scope['user']

        if user.is_anonymous:
            await self.close(code=4401)
            return

        is_member = await self._is_member(user.pk)
        if not is_member:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type == 'typing':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_typing',
                    'payload': {
                        'user_id': self.scope['user'].pk,
                        'is_typing': bool(content.get('is_typing')),
                    },
                },
            )

    async def chat_message(self, event):
        await self.send_json({'type': 'chat_message', 'payload': event['payload']})

    async def chat_typing(self, event):
        await self.send_json({'type': 'chat_typing', 'payload': event['payload']})

    @database_sync_to_async
    def _is_member(self, user_id: int) -> bool:
        return ChatThread.objects.filter(pk=self.thread_id, participants__pk=user_id).exists()


class PollConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.poll_id = int(self.scope['url_route']['kwargs']['poll_id'])
        self.group_name = f"poll_{self.poll_id}"

        exists = await self._poll_exists()
        if not exists:
            await self.close(code=4404)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def poll_update(self, event):
        await self.send_json({'type': 'poll_update', 'payload': event['payload']})

    @database_sync_to_async
    def _poll_exists(self) -> bool:
        return Poll.objects.filter(pk=self.poll_id).exists()
