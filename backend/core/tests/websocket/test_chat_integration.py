"""
Tests d'intégration complets pour le chat WebSocket.

Vérifie :
- Création message via API + réception via WebSocket
- Persistence des messages en base
- Broadcast à tous les membres connectés
- Mise à jour last_message_at
"""
import pytest
import asyncio
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from core.consumers import ChatConsumer
from core.models import ChatThread, ChatMembership, ChatMessage

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


@pytest.fixture
def api_client():
    """Client API pour tests synchrones"""
    return APIClient()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.critical
class TestChatIntegration:
    """Tests d'intégration complets chat (API + WebSocket)"""
    
    async def test_create_message_via_api_received_via_websocket(self, test_user, test_thread, api_client):
        """Vérifie qu'un message créé via API est reçu via WebSocket"""
        # Connecter l'utilisateur via WebSocket
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion WebSocket doit réussir"
        
        # Créer un message via API
        api_client.force_authenticate(user=test_user)
        response = api_client.post(
            '/api/chat/messages/',
            {
                'thread': test_thread.id,
                'content': 'Message de test via API'
            },
            format='json'
        )
        
        assert response.status_code == 201, f"Création message doit réussir, got {response.status_code}"
        
        # Attendre la réception du message via WebSocket (avec timeout)
        try:
            message = await asyncio.wait_for(communicator.receive_json_from(), timeout=2.0)
            assert message['type'] == 'chat_message', "Type doit être chat_message"
            assert message['payload']['content'] == 'Message de test via API', "Contenu doit correspondre"
            assert message['payload']['author']['id'] == test_user.id, "Auteur doit correspondre"
        except asyncio.TimeoutError:
            pytest.fail("Message WebSocket non reçu dans les 2 secondes")
        
        await communicator.disconnect()
    
    async def test_message_persisted_in_database(self, test_user, test_thread, api_client):
        """Vérifie qu'un message créé via API est persisté en base"""
        # Compter les messages avant
        initial_count = await database_sync_to_async(ChatMessage.objects.filter(thread=test_thread).count)()
        
        # Créer un message via API
        api_client.force_authenticate(user=test_user)
        response = api_client.post(
            '/api/chat/messages/',
            {
                'thread': test_thread.id,
                'content': 'Message persisté'
            },
            format='json'
        )
        
        assert response.status_code == 201, f"Création message doit réussir, got {response.status_code}"
        message_id = response.json()['id']
        
        # Vérifier que le message existe en base
        message = await database_sync_to_async(ChatMessage.objects.get)(pk=message_id)
        assert message.content == 'Message persisté', "Contenu doit être correct"
        assert message.author == test_user, "Auteur doit correspondre"
        assert message.thread == test_thread, "Thread doit correspondre"
        
        # Vérifier que le count a augmenté
        final_count = await database_sync_to_async(ChatMessage.objects.filter(thread=test_thread).count)()
        assert final_count == initial_count + 1, "Le nombre de messages doit avoir augmenté"
    
    async def test_message_broadcast_to_all_connected_members(self, test_user, test_user2, test_thread, api_client):
        """Vérifie qu'un message est broadcasté à tous les membres connectés"""
        # Ajouter test_user2 comme membre
        await database_sync_to_async(ChatMembership.objects.create)(
            thread=test_thread,
            user=test_user2,
            role=ChatMembership.ROLE_MEMBER
        )
        
        # Connecter les deux utilisateurs via WebSocket
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator1.scope['user'] = test_user
        connected1, _ = await communicator1.connect()
        assert connected1, "Connexion user1 doit réussir"
        
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator2.scope['user'] = test_user2
        connected2, _ = await communicator2.connect()
        assert connected2, "Connexion user2 doit réussir"
        
        # Créer un message via API (user1)
        api_client.force_authenticate(user=test_user)
        response = api_client.post(
            '/api/chat/messages/',
            {
                'thread': test_thread.id,
                'content': 'Message broadcasté'
            },
            format='json'
        )
        
        assert response.status_code == 201, f"Création message doit réussir, got {response.status_code}"
        
        # Les deux utilisateurs doivent recevoir le message
        try:
            message1 = await asyncio.wait_for(communicator1.receive_json_from(), timeout=2.0)
            message2 = await asyncio.wait_for(communicator2.receive_json_from(), timeout=2.0)
            
            assert message1['type'] == 'chat_message', "User1 doit recevoir chat_message"
            assert message2['type'] == 'chat_message', "User2 doit recevoir chat_message"
            assert message1['payload']['content'] == 'Message broadcasté', "Contenu user1 doit correspondre"
            assert message2['payload']['content'] == 'Message broadcasté', "Contenu user2 doit correspondre"
        except asyncio.TimeoutError:
            pytest.fail("Messages WebSocket non reçus dans les 2 secondes")
        
        await communicator1.disconnect()
        await communicator2.disconnect()
    
    async def test_last_message_at_updated(self, test_user, test_thread, api_client):
        """Vérifie que last_message_at est mis à jour lors de la création d'un message"""
        # Récupérer last_message_at initial
        initial_last_message_at = await database_sync_to_async(lambda: test_thread.last_message_at)()
        
        # Attendre un peu pour s'assurer que les timestamps sont différents
        await asyncio.sleep(0.1)
        
        # Créer un message via API
        api_client.force_authenticate(user=test_user)
        response = api_client.post(
            '/api/chat/messages/',
            {
                'thread': test_thread.id,
                'content': 'Message pour last_message_at'
            },
            format='json'
        )
        
        assert response.status_code == 201, f"Création message doit réussir, got {response.status_code}"
        
        # Rafraîchir le thread depuis la base
        await database_sync_to_async(test_thread.refresh_from_db)()
        updated_last_message_at = await database_sync_to_async(lambda: test_thread.last_message_at)()
        
        # Vérifier que last_message_at a été mis à jour
        assert updated_last_message_at is not None, "last_message_at doit être défini"
        if initial_last_message_at is not None:
            assert updated_last_message_at > initial_last_message_at, "last_message_at doit être mis à jour"
    
    async def test_message_not_received_if_not_connected(self, test_user, test_thread, api_client):
        """Vérifie qu'un message n'est pas reçu si l'utilisateur n'est pas connecté"""
        # Ne pas connecter l'utilisateur via WebSocket
        
        # Créer un message via API
        api_client.force_authenticate(user=test_user)
        response = api_client.post(
            '/api/chat/messages/',
            {
                'thread': test_thread.id,
                'content': 'Message sans connexion'
            },
            format='json'
        )
        
        assert response.status_code == 201, f"Création message doit réussir, got {response.status_code}"
        
        # Vérifier que le message est bien en base (mais pas reçu via WS car pas connecté)
        message_id = response.json()['id']
        message = await database_sync_to_async(ChatMessage.objects.get)(pk=message_id)
        assert message.content == 'Message sans connexion', "Message doit être en base"
        
        # Maintenant, connecter l'utilisateur et vérifier qu'il ne reçoit pas le message précédent
        # (les messages historiques ne sont pas envoyés automatiquement)
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Attendre un peu pour voir si un message arrive (il ne devrait pas)
        try:
            message = await asyncio.wait_for(communicator.receive_json_from(), timeout=0.5)
            pytest.fail("Aucun message ne devrait être reçu (messages historiques non envoyés)")
        except asyncio.TimeoutError:
            pass  # Comportement attendu : pas de message
        
        await communicator.disconnect()

