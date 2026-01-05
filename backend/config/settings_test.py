"""
Configuration Django pour les tests E2E full-stack
Base de données de test isolée, SAKA activé
"""
from .settings import *

# Base de données de test isolée
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base de données en mémoire pour les tests
        # Alternative : utiliser un fichier temporaire
        # 'NAME': BASE_DIR / 'db_test_e2e.sqlite3',
    }
}

# Activer SAKA pour les tests
ENABLE_SAKA = True
SAKA_COMPOST_ENABLED = True
SAKA_SILO_REDIS_ENABLED = True

# Configuration du compostage pour les tests
SAKA_COMPOST_INACTIVITY_DAYS = 90
SAKA_COMPOST_RATE = 0.1  # 10%
SAKA_COMPOST_MIN_BALANCE = 50
SAKA_COMPOST_MIN_AMOUNT = 10

# Configuration de la redistribution
SAKA_SILO_REDIS_RATE = 0.05  # 5%
SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY = 1

# Désactiver le cache pour les tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Désactiver les migrations pour accélérer les tests
# (utiliser migrate --run-syncdb si nécessaire)
# MIGRATION_MODULES = {
#     'core': None,
# }

# Logging pour les tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

# CORS pour les tests E2E
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Secret key pour les tests (ne pas utiliser en production)
SECRET_KEY = 'test-secret-key-for-e2e-fullstack-testing-min-50-chars-required-egoejo'

# Désactiver les vérifications de sécurité pour les tests
DEBUG = True
ALLOWED_HOSTS = ['*']

