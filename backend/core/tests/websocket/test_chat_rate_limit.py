"""
Tests rate-limit pour ChatConsumer (P1/P2 - placeholder xfail).

Placeholder pour tests de rate-limit sur les messages WebSocket.
À implémenter si nécessaire.
"""
import pytest
from channels.testing import WebsocketCommunicator
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model

from core.consumers import ChatConsumer
from core.models import ChatThread, ChatMembership

User = get_user_model()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
@pytest.mark.xfail(reason="Rate-limit non implémenté - placeholder pour P1/P2")
class TestChatRateLimit:
    """Tests rate-limit pour ChatConsumer (placeholder)"""
    
    async def test_rate_limit_messages(self, db):
        """Vérifie que le rate-limit est appliqué sur les messages"""
        # TODO: Implémenter rate-limit
        # - Limiter le nombre de messages par seconde
        # - Rejeter les messages si limite dépassée
        pytest.skip("Rate-limit non implémenté")
    
    async def test_rate_limit_typing(self, db):
        """Vérifie que le rate-limit est appliqué sur les typing indicators"""
        # TODO: Implémenter rate-limit typing
        # - Limiter le nombre de typing indicators par seconde
        pytest.skip("Rate-limit typing non implémenté")

