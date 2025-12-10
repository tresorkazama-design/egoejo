"""
Configuration Django pour EGOEJO
"""
# Import Celery app pour qu'il soit chargé au démarrage Django (optionnel)
try:
    from .celery import app as celery_app
    __all__ = ('celery_app',)
except ImportError:
    # Celery non installé, continuer sans
    celery_app = None
    __all__ = ()

