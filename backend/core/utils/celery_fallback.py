"""
Fallback pour Celery si Redis est indisponible
"""
import logging
from django.conf import settings
from core.utils.redis_health import check_redis_available

logger = logging.getLogger(__name__)

def execute_task_sync(task_func, *args, **kwargs):
    """
    Exécute une tâche de manière synchrone si Celery n'est pas disponible.
    
    Args:
        task_func: Fonction de tâche Celery
        *args: Arguments positionnels
        **kwargs: Arguments nommés
    
    Returns:
        Résultat de la tâche (celery.AsyncResult ou résultat direct)
    """
    if check_redis_available():
        # Redis disponible, utiliser Celery normalement
        try:
            return task_func.delay(*args, **kwargs)
        except Exception as e:
            logger.warning(
                f"Erreur lors de l'envoi de la tâche Celery {task_func.__name__} : {e}. "
                f"Tentative d'exécution synchrone...",
                exc_info=True
            )
            # Fallback : exécuter de manière synchrone
            return task_func(*args, **kwargs)
    else:
        # Redis indisponible, exécuter de manière synchrone
        logger.warning(
            f"Redis indisponible - Exécution synchrone de la tâche {task_func.__name__}"
        )
        return task_func(*args, **kwargs)

