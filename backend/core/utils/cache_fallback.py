"""
Wrapper pour le cache avec gestion de fallback
"""
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)

def safe_cache_get(key, default=None):
    """
    Récupère une valeur du cache de manière sécurisée.
    
    Args:
        key: Clé du cache
        default: Valeur par défaut si non trouvé ou erreur
    
    Returns:
        Valeur du cache ou default
    """
    try:
        return cache.get(key, default)
    except Exception as e:
        logger.warning(
            f"Erreur lors de la récupération du cache ({key}) : {e}",
            exc_info=True
        )
        return default

def safe_cache_set(key, value, timeout=None):
    """
    Définit une valeur dans le cache de manière sécurisée.
    
    Args:
        key: Clé du cache
        value: Valeur à stocker
        timeout: Timeout en secondes
    
    Returns:
        bool: True si réussi, False si erreur
    """
    try:
        cache.set(key, value, timeout)
        return True
    except Exception as e:
        logger.warning(
            f"Erreur lors de la définition du cache ({key}) : {e}",
            exc_info=True
        )
        return False

def safe_cache_delete(key):
    """
    Supprime une valeur du cache de manière sécurisée.
    
    Args:
        key: Clé du cache
    
    Returns:
        bool: True si réussi, False si erreur
    """
    try:
        cache.delete(key)
        return True
    except Exception as e:
        logger.warning(
            f"Erreur lors de la suppression du cache ({key}) : {e}",
            exc_info=True
        )
        return False

