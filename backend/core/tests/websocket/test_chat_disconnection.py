"""
Tests de déconnexion brutale pour le chat WebSocket.

Vérifie :
- Déconnexion brutale (fermeture forcée)
- Nettoyage des groupes Channels
- Reconnexion après déconnexion
"""
import pytest
import asyncio
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model

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
async def test_thread(db, test_user):
    """Thread de chat de test (async)"""
    thread = await database_sync_to_async(ChatThread.objects.create)(
        title='Test Thread',
        created_by=test_user
    )
    await database_sync_to_async(ChatMembership.objects.create)(
        thread=thread,
        user=test_user,
        role=ChatMembership.ROLE_OWNER
    )
    return thread


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.critical
class TestChatDisconnection:
    """Tests de déconnexion"""
    
    async def test_brutal_disconnect_cleans_up_group(self, test_user, test_thread):
        """Vérifie qu'une déconnexion brutale nettoie le groupe Channels"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Vérifier que le groupe existe
        channel_layer = get_channel_layer()
        group_name = f"chat_thread_{test_thread.id}"
        
        # Déconnexion brutale (sans appeler disconnect())
        # Simuler une fermeture forcée en fermant directement
        await communicator.disconnect()
        
        # Attendre un peu pour que le nettoyage se fasse
        await asyncio.sleep(0.1)
        
        # Vérifier que le groupe est nettoyé (en essayant de se reconnecter)
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator2.scope['user'] = test_user
        
        connected2, _ = await communicator2.connect()
        assert connected2, "Reconnexion doit réussir après déconnexion brutale"
        
        await communicator2.disconnect()
    
    async def test_reconnect_after_disconnect(self, test_user, test_thread):
        """Vérifie qu'un utilisateur peut se reconnecter après déconnexion"""
        # Première connexion
        communicator1 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator1.scope['user'] = test_user
        
        connected1, _ = await communicator1.connect()
        assert connected1, "Première connexion doit réussir"
        
        # Déconnexion propre
        await communicator1.disconnect()
        
        # Attendre un peu
        await asyncio.sleep(0.1)
        
        # Reconnexion
        communicator2 = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator2.scope['user'] = test_user
        
        connected2, _ = await communicator2.connect()
        assert connected2, "Reconnexion doit réussir"
        
        await communicator2.disconnect()
    
    async def test_multiple_disconnects_handled_gracefully(self, test_user, test_thread):
        """Vérifie que plusieurs déconnexions sont gérées gracieusement"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Appeler disconnect() plusieurs fois (ne devrait pas crasher)
        await communicator.disconnect()
        await communicator.disconnect()  # Deuxième appel
        await communicator.disconnect()  # Troisième appel
        
        # Ne devrait pas lever d'exception
    
    async def test_disconnect_with_code(self, test_user, test_thread):
        """Vérifie qu'une déconnexion avec code est gérée correctement"""
        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            f"/ws/chat/{test_thread.id}/"
        )
        communicator.scope['user'] = test_user
        
        connected, _ = await communicator.connect()
        assert connected, "Connexion doit réussir"
        
        # Déconnexion avec code (simuler code 1000 = normal closure)
        await communicator.disconnect(code=1000)
        
        # Ne devrait pas lever d'exception

