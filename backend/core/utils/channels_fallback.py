"""
Wrapper pour Channels avec gestion de fallback
"""
import logging
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

def safe_group_send(group_name, message):
    """
    Envoie un message à un groupe de manière sécurisée avec fallback.
    
    Args:
        group_name: Nom du groupe
        message: Message à envoyer
    
    Returns:
        bool: True si envoyé, False si erreur
    """
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(group_name, message)
        return True
    except Exception as e:
        logger.error(
            f"Erreur lors de l'envoi de message au groupe {group_name} : {e}",
            exc_info=True
        )
        return False

