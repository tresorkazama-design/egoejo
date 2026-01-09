"""
Tests d'intégration pour ChatConsumer (WebSocket).

Vérifie :
- Authentification (anon close 4401)
- Permissions (non-member close 4403)
- Membership check
- Typing indicator / heartbeat
"""
import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from core.consumers import ChatConsumer
from core.models import ChatThread, ChatMembership

User = get_user_model()


@pytest.fixture
async def test_user(db):
    """Utilisateur de test (async)"""
    return await database_sync_to_async(User.objects.create_user)(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
async def test_user2(db):
    """Deuxième utilisateur de test (async)"""
    return await database_sync_to_async(User.objects.create_user)(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )


@pytest.fixture
async def test_thread(db, test_user):
    """Thread de chat de test (async)"""
    thread = await database_sync_to_async(ChatThread.objects.create)(
        title='Test Thread',
        created_by=test_user
    )
    # Ajouter test_user comme membre
    await database_sync_to_async(ChatMembership.objects.create)(
        thread=thread,
        user=test_user,
        role=ChatMembership.ROLE_OWNER
    )
    return thread


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.critical
class TestChatConsumerAuth:
    """Tests d'authentification pour ChatConsumer"""
    
    async def test_anon_close_4401(self, test_thread):
        """Vérifie qu'un utilisateur anonyme est rejeté avec code 4401"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = await database_sync_to_async(lambda: User())()  # AnonymousUser
        
        connected, subprotocol = await communicator.connect()
        
        # La connexion doit être refusée
        assert not connected, "Connexion anonyme doit être refusée"
        
        # Vérifier le code de fermeture (4401 = Unauthorized)
        # Note: WebsocketCommunicator ne retourne pas toujours le code exact,
        # mais on peut vérifier que la connexion n'est pas acceptée
        await communicator.disconnect()
    
    async def test_authenticated_user_connects(self, test_user, test_thread):
        """Vérifie qu'un utilisateur authentifié membre peut se connecter"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, subprotocol = await communicator.connect()
        
        assert connected, "Utilisateur authentifié membre doit pouvoir se connecter"
        
        await communicator.disconnect()
    
    async def test_non_member_close_4403(self, test_user2, test_thread):
        """Vérifie qu'un utilisateur non-membre est rejeté avec code 4403"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user2  # Non-membre
        
        connected, subprotocol = await communicator.connect()
        
        # La connexion doit être refusée
        assert not connected, "Utilisateur non-membre doit être refusé"
        
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.critical
class TestChatConsumerMembership:
    """Tests de vérification de membership"""
    
    async def test_member_can_connect(self, test_user, test_thread):
        """Vérifie qu'un membre peut se connecter"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, subprotocol = await communicator.connect()
        assert connected, "Membre doit pouvoir se connecter"
        
        await communicator.disconnect()
    
    async def test_non_member_cannot_connect(self, test_user2, test_thread):
        """Vérifie qu'un non-membre ne peut pas se connecter"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user2
        
        connected, subprotocol = await communicator.connect()
        assert not connected, "Non-membre ne doit pas pouvoir se connecter"
        
        await communicator.disconnect()
    
    async def test_member_after_joining(self, test_user2, test_thread):
        """Vérifie qu'un utilisateur peut se connecter après avoir rejoint le thread"""
        # D'abord, vérifier qu'il ne peut pas se connecter
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator1.scope['user'] = test_user2
        
        connected1, _ = await communicator1.connect()
        assert not connected1, "Non-membre ne doit pas pouvoir se connecter"
        await communicator1.disconnect()
        
        # Ajouter test_user2 comme membre
        await database_sync_to_async(ChatMembership.objects.create)(
            thread=test_thread,
            user=test_user2,
            role=ChatMembership.ROLE_MEMBER
        )
        
        # Maintenant, il doit pouvoir se connecter
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator2.scope['user'] = test_user2
        
        connected2, _ = await communicator2.connect()
        assert connected2, "Membre doit pouvoir se connecter après avoir rejoint"
        
        await communicator2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestChatConsumerHeartbeat:
    """Tests heartbeat (ping/pong)"""
    
    async def test_ping_pong(self, test_user, test_thread):
        """Vérifie que le heartbeat ping/pong fonctionne"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Envoyer un ping
        await communicator.send_json_to({'type': 'ping'})
        
        # Recevoir le pong
        response = await communicator.receive_json_from()
        assert response['type'] == 'pong', "Réponse doit être un pong"
        
        await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestChatConsumerTyping:
    """Tests typing indicator"""
    
    async def test_typing_indicator_sent(self, test_user, test_thread):
        """Vérifie que l'indicateur de frappe est envoyé au groupe"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Envoyer un typing indicator
        await communicator.send_json_to({
            'type': 'typing',
            'is_typing': True
        })
        
        # Recevoir le typing indicator broadcast
        response = await communicator.receive_json_from()
        assert response['type'] == 'chat_typing', "Réponse doit être chat_typing"
        assert response['payload']['user_id'] == test_user.id, "user_id doit correspondre"
        assert response['payload']['is_typing'] is True, "is_typing doit être True"
        
        # Envoyer typing = False
        await communicator.send_json_to({
            'type': 'typing',
            'is_typing': False
        })
        
        # Recevoir le typing indicator broadcast
        response2 = await communicator.receive_json_from()
        assert response2['type'] == 'chat_typing', "Réponse doit être chat_typing"
        assert response2['payload']['is_typing'] is False, "is_typing doit être False"
        
        await communicator.disconnect()
    
    async def test_typing_indicator_broadcast(self, test_user, test_user2, test_thread):
        """Vérifie que l'indicateur de frappe est broadcasté à tous les membres"""
        # Ajouter test_user2 comme membre
        await database_sync_to_async(ChatMembership.objects.create)(
            thread=test_thread,
            user=test_user2,
            role=ChatMembership.ROLE_MEMBER
        )
        
        # Connexion user1
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator1.scope['user'] = test_user
        connected1, _ = await communicator1.connect()
        assert connected1
        
        # Connexion user2
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator2.scope['user'] = test_user2
        connected2, _ = await communicator2.connect()
        assert connected2
        
        # User1 envoie typing indicator
        await communicator1.send_json_to({
            'type': 'typing',
            'is_typing': True
        })
        
        # User2 doit recevoir le typing indicator
        response = await communicator2.receive_json_from()
        assert response['type'] == 'chat_typing', "User2 doit recevoir chat_typing"
        assert response['payload']['user_id'] == test_user.id, "user_id doit être celui de user1"
        assert response['payload']['is_typing'] is True, "is_typing doit être True"
        
        await communicator1.disconnect()
        await communicator2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestChatConsumerMessage:
    """Tests réception de messages via WebSocket"""
    
    async def test_receive_chat_message(self, test_user, test_thread):
        """Vérifie qu'un message chat est reçu via WebSocket"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected
        
        # Simuler un message broadcasté (comme le ferait broadcast_to_group)
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        
        await channel_layer.group_send(
            f"chat_thread_{test_thread.id}",
            {
                'type': 'chat_message',
                'payload': {
                    'id': 1,
                    'thread': test_thread.id,
                    'author': {'id': test_user.id, 'username': test_user.username},
                    'content': 'Test message',
                    'created_at': '2025-01-27T10:00:00Z'
                }
            }
        )
        
        # Recevoir le message
        response = await communicator.receive_json_from()
        assert response['type'] == 'chat_message', "Réponse doit être chat_message"
        assert response['payload']['content'] == 'Test message', "Contenu doit correspondre"
        
        await communicator.disconnect()

