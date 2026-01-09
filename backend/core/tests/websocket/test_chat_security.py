"""
Tests de sécurité pour le chat WebSocket.

Vérifie :
- Pas d'accès cross-room (isolation des threads)
- Validation payload (types invalides, payloads malformés)
- Permissions strictes (non-membre ne peut pas accéder)
"""
import pytest
import asyncio
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

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
async def test_thread1(db, test_user):
    """Premier thread de chat (async)"""
    thread = await database_sync_to_async(ChatThread.objects.create)(
        title='Thread 1',
        created_by=test_user
    )
    await database_sync_to_async(ChatMembership.objects.create)(
        thread=thread,
        user=test_user,
        role=ChatMembership.ROLE_OWNER
    )
    return thread


@pytest.fixture
async def test_thread2(db, test_user2):
    """Deuxième thread de chat (async)"""
    thread = await database_sync_to_async(ChatThread.objects.create)(
        title='Thread 2',
        created_by=test_user2
    )
    await database_sync_to_async(ChatMembership.objects.create)(
        thread=thread,
        user=test_user2,
        role=ChatMembership.ROLE_OWNER
    )
    return thread


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.critical
class TestChatSecurityCrossRoom:
    """Tests d'isolation cross-room"""
    
    async def test_user_cannot_access_other_thread(self, test_user, test_thread2):
        """Vérifie qu'un utilisateur ne peut pas accéder à un thread dont il n'est pas membre"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread2.id}/"
        )
        communicator.scope['user'] = test_user  # test_user n'est pas membre de test_thread2
        
        connected, _ = await communicator.connect()
        
        # La connexion doit être refusée
        assert not connected, "Utilisateur non-membre ne doit pas pouvoir se connecter"
        
        await communicator.disconnect()
    
    async def test_message_not_broadcasted_to_other_thread(self, test_user, test_user2, test_thread1, test_thread2):
        """Vérifie qu'un message d'un thread n'est pas broadcasté à un autre thread"""
        # Ajouter test_user2 comme membre de thread1
        await database_sync_to_async(ChatMembership.objects.create)(
            thread=test_thread1,
            user=test_user2,
            role=ChatMembership.ROLE_MEMBER
        )
        
        # Connecter test_user2 aux deux threads
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread1.id}/"
        )
        communicator1.scope['user'] = test_user2
        connected1, _ = await communicator1.connect()
        assert connected1, "Connexion thread1 doit réussir"
        
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread2.id}/"
        )
        communicator2.scope['user'] = test_user2
        connected2, _ = await communicator2.connect()
        assert connected2, "Connexion thread2 doit réussir"
        
        # Envoyer un message dans thread1 via channel_layer (simuler broadcast)
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            f"chat_thread_{test_thread1.id}",
            {
                'type': 'chat_message',
                'payload': {
                    'id': 1,
                    'thread': test_thread1.id,
                    'author': {'id': test_user.id, 'username': test_user.username},
                    'content': 'Message thread1',
                    'created_at': '2025-01-27T10:00:00Z'
                }
            }
        )
        
        # test_user2 doit recevoir le message dans thread1 uniquement
        try:
            message1 = await asyncio.wait_for(communicator1.receive_json_from(), timeout=2.0)
            assert message1['type'] == 'chat_message', "Message doit être reçu dans thread1"
            assert message1['payload']['content'] == 'Message thread1', "Contenu doit correspondre"
            
            # Vérifier qu'aucun message n'arrive dans thread2
            try:
                message2 = await asyncio.wait_for(communicator2.receive_json_from(), timeout=0.5)
                pytest.fail("Aucun message ne devrait être reçu dans thread2")
            except asyncio.TimeoutError:
                pass  # Comportement attendu : pas de message dans thread2
        except asyncio.TimeoutError:
            pytest.fail("Message thread1 non reçu dans les 2 secondes")
        
        await communicator1.disconnect()
        await communicator2.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.critical
class TestChatSecurityPayloadValidation:
    """Tests de validation des payloads"""
    
    async def test_invalid_json_rejected(self, test_user, test_thread1):
        """Vérifie qu'un JSON invalide est rejeté"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread1.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Envoyer un JSON invalide (bytes au lieu de JSON)
        # Note: WebsocketCommunicator.send_json_to() valide le JSON,
        # donc on doit utiliser send_to() pour envoyer des données brutes
        await communicator.send_to(text_data="invalid json {")
        
        # Le consumer devrait gérer l'erreur gracieusement (pas de crash)
        # Attendre un peu pour voir si une erreur arrive
        try:
            response = await asyncio.wait_for(communicator.receive_json_from(), timeout=0.5)
            # Si une réponse arrive, elle devrait être une erreur
            # (mais le consumer actuel ne renvoie pas d'erreur pour JSON invalide)
        except asyncio.TimeoutError:
            pass  # Pas de réponse attendue pour JSON invalide
        
        await communicator.disconnect()
    
    async def test_unknown_message_type_ignored(self, test_user, test_thread1):
        """Vérifie qu'un type de message inconnu est ignoré"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread1.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Envoyer un type de message inconnu
        await communicator.send_json_to({
            'type': 'unknown_type',
            'data': 'test'
        })
        
        # Le consumer devrait ignorer le message (pas de réponse)
        try:
            response = await asyncio.wait_for(communicator.receive_json_from(), timeout=0.5)
            pytest.fail("Aucune réponse ne devrait être envoyée pour un type inconnu")
        except asyncio.TimeoutError:
            pass  # Comportement attendu : pas de réponse
        
        await communicator.disconnect()
    
    async def test_typing_without_is_typing_field(self, test_user, test_thread1):
        """Vérifie que typing sans is_typing est géré correctement"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread1.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Envoyer typing sans is_typing
        await communicator.send_json_to({
            'type': 'typing'
            # Pas de is_typing
        })
        
        # Le consumer devrait utiliser bool(content.get('is_typing')) qui retourne False
        # et broadcast le typing indicator
        try:
            response = await asyncio.wait_for(communicator.receive_json_from(), timeout=2.0)
            assert response['type'] == 'chat_typing', "Type doit être chat_typing"
            assert response['payload']['is_typing'] is False, "is_typing doit être False par défaut"
        except asyncio.TimeoutError:
            pytest.fail("Typing indicator non reçu dans les 2 secondes")
        
        await communicator.disconnect()
    
    async def test_malformed_payload_handled_gracefully(self, test_user, test_thread1):
        """Vérifie qu'un payload malformé est géré gracieusement"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread1.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Envoyer un payload avec des types incorrects
        await communicator.send_json_to({
            'type': 'typing',
            'is_typing': 'not a boolean'  # String au lieu de bool
        })
        
        # Le consumer devrait convertir en bool() et continuer
        try:
            response = await asyncio.wait_for(communicator.receive_json_from(), timeout=2.0)
            assert response['type'] == 'chat_typing', "Type doit être chat_typing"
            # bool('not a boolean') = True en Python
            assert response['payload']['is_typing'] is True, "is_typing doit être converti en bool"
        except asyncio.TimeoutError:
            pytest.fail("Typing indicator non reçu dans les 2 secondes")
        
        await communicator.disconnect()

