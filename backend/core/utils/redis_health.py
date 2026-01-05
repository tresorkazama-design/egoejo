"""
Utilitaires pour détecter et gérer les pannes Redis
"""
import logging
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

def check_redis_available():
    """
    Vérifie si Redis est disponible.
    
    Returns:
        bool: True si Redis est disponible, False sinon
    """
    try:
        cache.set('redis_health_check', 'ok', 1)
        cache.get('redis_health_check')
        return True
    except Exception as e:
        logger.error(f"Redis indisponible : {e}", exc_info=True)
        return False

def get_redis_status():
    """
    Retourne le statut Redis avec détails.
    
    Returns:
        dict: {
            'available': bool,
            'backend': str,
            'error': str | None
        }
    """
    try:
        cache.set('redis_health_check', 'ok', 1)
        cache.get('redis_health_check')
        return {
            'available': True,
            'backend': cache.__class__.__name__,
            'error': None
        }
    except Exception as e:
        logger.error(f"Redis indisponible : {e}", exc_info=True)
        return {
            'available': False,
            'backend': cache.__class__.__name__,
            'error': str(e)
        }

