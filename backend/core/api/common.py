"""
Fonctions utilitaires partagées entre les endpoints REST et websockets.
"""

import hashlib
import logging
import os
from typing import Any, Dict, Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings

from core.models import AuditLog, Poll


logger = logging.getLogger(__name__)


def broadcast_to_group(group_name: str, event_type: str, payload: Dict[str, Any]) -> None:
    """
    Envoie un message sur un groupe Channels s'il est disponible.
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.debug("Canal indisponible pour %s", group_name)
        return
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": event_type,
            "payload": payload,
        },
    )


def log_action(actor, action: str, target_type: str, target_id: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Persist l'action dans le journal d'audit sans casser la requête en cas d'échec.
    """
    try:
        AuditLog.objects.create(
            actor=actor if getattr(actor, "is_authenticated", False) else None,
            action=action,
            target_type=target_type,
            target_id=str(target_id or ""),
            metadata=metadata or {},
        )
    except Exception:  # noqa: BLE001
        logger.exception("Impossible d'enregistrer l'action %s (%s)", action, target_type)


def build_voter_hash(request, poll: Poll) -> str:
    """
    Génère un hash stable pour les bulletins afin d'assurer l'unicité par utilisateur.
    """
    base = f"user:{request.user.pk}"
    secret = settings.SECRET_KEY
    raw = f"{secret}:{poll.pk}:{base}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def extract_admin_token(request) -> Optional[str]:
    header = request.headers.get("Authorization", "")
    if header.startswith("Bearer "):
        return header.replace("Bearer ", "").strip()
    return None


import os
import logging

logger = logging.getLogger(__name__)

def require_admin_token(request):
    """
    Valide le token admin passé soit en query ?token=..., soit en header.
    Ne doit JAMAIS lever d'exception : renvoie None si invalide.
    """
    expected = os.environ.get("ADMIN_TOKEN")

    if not expected:
        logger.error("ADMIN_TOKEN is not configured in environment.")
        return None

    # Essayer plusieurs méthodes pour obtenir le token
    # 1. Query parameter
    token = request.GET.get("token")
    
    # 2. Header X-Admin-Token (via request.META pour compatibilité tests)
    if not token:
        token = request.META.get("HTTP_X_ADMIN_TOKEN") or request.headers.get("X-Admin-Token")
    
    # 3. Header Authorization Bearer (via request.META pour compatibilité tests)
    if not token:
        auth_header = request.META.get("HTTP_AUTHORIZATION") or request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "").strip()
        elif auth_header.startswith("bearer "):
            token = auth_header.replace("bearer ", "").strip()

    if not token:
        logger.warning("No admin token provided in request. META keys: %s", list(request.META.keys())[:10])
        return None

    if token != expected:
        logger.warning("Invalid admin token provided. Expected: %s, Got: %s", expected, token)
        return None

    return token

