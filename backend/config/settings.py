import os
from pathlib import Path
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================
# SECRET KEY
# ======================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY must be set")
if len(SECRET_KEY) < 50:
    import warnings
    warnings.warn("SECRET_KEY should be at least 50 characters long for production use")

# ======================
# DEBUG & ALLOWED_HOSTS
# ======================
_debug_env = os.environ.get('DEBUG', '0')
DEBUG = str(_debug_env).lower() in ('1', 'true', 'yes', 'on')

_raw_allowed = os.environ.get('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip() for h in _raw_allowed.split(',') if h.strip()]

# Ajouter automatiquement le domaine Railway si disponible
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)

# Extraire le domaine depuis RAILWAY_STATIC_URL si disponible
_railway_static = os.environ.get('RAILWAY_STATIC_URL', '')
if _railway_static:
    try:
        from urllib.parse import urlparse
        parsed = urlparse(_railway_static)
        if parsed.hostname and parsed.hostname not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(parsed.hostname)
    except Exception:
        pass

# En production sur Railway, extraire le domaine depuis les variables Railway
if not DEBUG and not any('railway' in h for h in ALLOWED_HOSTS):
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PROJECT_ID'):
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        if railway_domain:
            if railway_domain not in ALLOWED_HOSTS:
                ALLOWED_HOSTS.append(railway_domain)
        elif not ALLOWED_HOSTS:
            raise RuntimeError(
                "ALLOWED_HOSTS must be set in production. "
                "Set RAILWAY_PUBLIC_DOMAIN or ALLOWED_HOSTS environment variable."
            )

# ======================
# APPS & MIDDLEWARE
# ======================
INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'csp',  # Content Security Policy
    'drf_spectacular',  # OpenAPI/Swagger documentation
    'rest_framework_simplejwt.token_blacklist',
    'core',
    'finance',  # Système financier unifié (V1.6 + V2.0 dormant)
    'investment',  # Investissement (V2.0 dormant)
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.security.middleware.SecurityHeadersMiddleware',  # Headers de sécurité renforcés
    'core.security.middleware.DataProtectionMiddleware',  # Protection des données sensibles
    'csp.middleware.CSPMiddleware',  # Content Security Policy
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ]
    },
}]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# ======================
# CHANNELS
# ======================
REDIS_URL = os.environ.get('REDIS_URL')
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }

# ======================
# CACHING
# ======================
# Utiliser Redis pour le cache si disponible, sinon cache en mémoire
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL.replace('/0', '/1'),  # Utiliser la DB 1 pour le cache (DB 0 pour Channels)
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'egoejo',
            'TIMEOUT': 300,  # 5 minutes par défaut
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

# ======================
# DATABASES
# ======================
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    db_config['OPTIONS'] = {
        'connect_timeout': 10,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
    }
    DATABASES = {
        'default': db_config
    }
elif os.environ.get('DB_NAME'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'db'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ======================
# PASSWORDS
# ======================
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 10},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ======================
# SECURITY - RENFORCÉE
# ======================
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Headers de sécurité supplémentaires
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

# Protection des cookies
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Protection CSRF
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Timeout de session (30 minutes)
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True  # Renouveler le cookie à chaque requête

# ======================
# STATIC & MEDIA
# ======================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Configuration des médias (upload utilisateurs)
# Utiliser R2/S3 en production, système de fichiers local en développement
USE_S3_STORAGE = os.environ.get('USE_S3_STORAGE', 'False').lower() == 'true'

if USE_S3_STORAGE:
    # Configuration Cloudflare R2 (compatible S3) ou AWS S3
    # Variables d'environnement requises :
    # - R2_ACCESS_KEY_ID ou AWS_ACCESS_KEY_ID
    # - R2_SECRET_ACCESS_KEY ou AWS_SECRET_ACCESS_KEY
    # - R2_BUCKET_NAME ou AWS_STORAGE_BUCKET_NAME
    # - R2_ENDPOINT_URL (pour R2 uniquement, ex: https://xxx.r2.cloudflarestorage.com)
    # - R2_CUSTOM_DOMAIN (optionnel, pour CDN)
    
    INSTALLED_APPS.append('storages')
    
    AWS_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID') or os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY') or os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME') or os.environ.get('AWS_STORAGE_BUCKET_NAME')
    
    # Configuration spécifique R2 (Cloudflare)
    R2_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL')
    if R2_ENDPOINT_URL:
        AWS_S3_ENDPOINT_URL = R2_ENDPOINT_URL
        AWS_S3_CUSTOM_DOMAIN = os.environ.get('R2_CUSTOM_DOMAIN')
        AWS_S3_REGION_NAME = 'auto'  # R2 utilise 'auto'
    else:
        # Configuration AWS S3 standard
        AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    
    # Paramètres de stockage
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',  # 24 heures
    }
    AWS_DEFAULT_ACL = os.environ.get('AWS_DEFAULT_ACL', 'public-read')  # 'public-read' ou 'private'
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    
    # Utiliser R2/S3 pour les médias
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # URL des médias
    if AWS_S3_CUSTOM_DOMAIN:
        MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
    else:
        MEDIA_URL = f'{AWS_S3_ENDPOINT_URL or f"https://{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"}/'
    
    MEDIA_ROOT = ''  # Non utilisé avec S3
else:
    # Stockage local (développement uniquement)
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'

# ======================
# CORS & CSRF
# ======================
CORS_ALLOWED_ORIGINS = [
    u.strip()
    for u in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    if u.strip()
]
CSRF_TRUSTED_ORIGINS = [
    u.strip()
    for u in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if u.strip()
]

# Si CORS_ALLOWED_ORIGINS est vide en développement, autoriser localhost par défaut
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://localhost:5174',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:5174',
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

# En production, ajouter automatiquement le frontend Vercel si disponible
if not DEBUG:
    _vercel_url = os.environ.get('VERCEL_URL') or os.environ.get('FRONTEND_URL')
    if _vercel_url:
        if not _vercel_url.startswith('http'):
            _vercel_url = f'https://{_vercel_url}'
        if _vercel_url not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(_vercel_url)
        if _vercel_url not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(_vercel_url)

# ======================
# REST FRAMEWORK / JWT
# ======================
_auth_classes = (
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework.authentication.BasicAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
)

if os.environ.get('DISABLE_THROTTLE_FOR_TESTS') == '1':
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': _auth_classes,
        'DEFAULT_THROTTLE_CLASSES': [],
        'DEFAULT_THROTTLE_RATES': {},
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(os.environ.get('API_PAGE_SIZE', '20')),
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': _auth_classes,
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
            # 'core.api.rate_limiting.IPRateThrottle',  # Décommenter si nécessaire
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': os.environ.get('THROTTLE_ANON', '10/minute'),
            'user': os.environ.get('THROTTLE_USER', '100/minute'),
            'ip': os.environ.get('THROTTLE_IP', '100/hour'),  # Limite par IP
        },
        'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': int(os.environ.get('API_PAGE_SIZE', '20')),
    }

# ======================
# OPENAPI / SWAGGER (drf-spectacular)
# ======================
SPECTACULAR_SETTINGS = {
    'TITLE': 'EGOEJO API',
    'DESCRIPTION': 'API pour le collectif EGOEJO - Relier des citoyens à des projets sociaux à fort impact',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SCHEMA_PATH_PREFIX': '/api/',
    'COMPONENT_SPLIT_REQUEST': True,
    'COMPONENT_NO_READ_ONLY_REQUIRED': True,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(
        minutes=int(os.environ.get('ACCESS_TOKEN_MINUTES', '60'))
    ),
    'REFRESH_TOKEN_LIFETIME': timedelta(
        days=int(os.environ.get('REFRESH_TOKEN_DAYS', '7'))
    ),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# ======================
# LOGGING
# ======================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'filters': {
        'mask_sensitive': {
            '()': 'core.security.logging.SecureFormatter',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.environ.get('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.environ.get('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': os.environ.get('DB_LOG_LEVEL', 'WARNING'),
            'propagate': False,
        },
        'channels': {
            'handlers': ['console'],
            'level': os.environ.get('CHANNELS_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}

# ======================
# EMAIL
# ======================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', '1') == '1'

# ADMINS : Liste des administrateurs qui recevront les alertes critiques
# Format : [('Nom', 'email@example.com'), ...]
# Peut être configuré via variable d'environnement ADMINS (JSON)
ADMINS = []
if os.environ.get('ADMINS'):
    import json
    try:
        ADMINS = json.loads(os.environ.get('ADMINS'))
        # S'assurer que ADMINS est une liste de tuples
        if ADMINS and isinstance(ADMINS[0], list):
            ADMINS = [tuple(admin) for admin in ADMINS]
    except (json.JSONDecodeError, ValueError):
        # Fallback : format simple "Nom,email@example.com;Nom2,email2@example.com"
        admin_str = os.environ.get('ADMINS', '')
        if admin_str:
            for admin_pair in admin_str.split(';'):
                if ',' in admin_pair:
                    name, email = admin_pair.split(',', 1)
                    ADMINS.append((name.strip(), email.strip()))

# ALERTES EMAIL CRITIQUES
# ======================
ALERT_EMAIL_ENABLED = os.environ.get('ALERT_EMAIL_ENABLED', 'True').lower() == 'true'
ALERT_EMAIL_SUBJECT_PREFIX = os.environ.get('ALERT_EMAIL_SUBJECT_PREFIX', '[URGENT] EGOEJO')

# ALERTES WEBHOOK (Optionnel)
# ======================
ALERT_WEBHOOK_ENABLED = os.environ.get('ALERT_WEBHOOK_ENABLED', 'False').lower() == 'true'
ALERT_WEBHOOK_URL = os.environ.get('ALERT_WEBHOOK_URL', '')
ALERT_WEBHOOK_TYPE = os.environ.get('ALERT_WEBHOOK_TYPE', 'generic').lower()  # 'generic' ou 'slack'
ALERT_WEBHOOK_TIMEOUT_SECONDS = int(os.environ.get('ALERT_WEBHOOK_TIMEOUT_SECONDS', '5'))

# ====================================================================
# SÉCURITÉ DEV / PROD
# ====================================================================
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get(
        'SECURE_HSTS_INCLUDE_SUBDOMAINS', '1'
    ) == '1'
    SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', '1') == '1'

# ==============================================
# EGOEJO FEATURE FLAGS (Le Cerveau Hybride)
# ==============================================
# Si False : Mode V1.6 (Dons uniquement, interface simplifiée)
# Si True  : Mode V2.0 (Investissement, KYC, Actions, Signatures)
ENABLE_INVESTMENT_FEATURES = os.environ.get('ENABLE_INVESTMENT_FEATURES', 'False').lower() == 'true'

# Modèle Économique (5% + 3%)
EGOEJO_COMMISSION_RATE = float(os.environ.get('EGOEJO_COMMISSION_RATE', '0.05'))  # 5%
STRIPE_FEE_ESTIMATE = float(os.environ.get('STRIPE_FEE_ESTIMATE', '0.03'))  # 3%

# Frais Stripe détaillés (pour calcul proportionnel)
STRIPE_FIXED_FEE = float(os.environ.get('STRIPE_FIXED_FEE', '0.25'))  # 0.25€ fixe
STRIPE_PERCENT_FEE = float(os.environ.get('STRIPE_PERCENT_FEE', '0.015'))  # 1.5% (0.015)

# Sécurité Fondateur
# CORRECTION 3 : Nom unique et explicite pour éviter magic strings
FOUNDER_GROUP_NAME = os.environ.get('FOUNDER_GROUP_NAME', 'Founders_V1_Protection')

# ==============================================
# PROTOCOLE SAKA 🌾 (V2.1 - Le Cerveau Yin)
# ==============================================
# SAKA : Monnaie interne d'engagement (Yin) - Strictement séparée de l'Euro (Yang)
# Règles fondamentales :
# - SAKA ne s'achète pas, il se récolte (Proof of Care)
# - SAKA ne sert pas à consommer, mais à influencer (gouvernance)
# - SAKA inactif retourne au Silo commun (compostage)
# - SAKA (Yin) et Euro (Yang) sont strictement séparés

# Mode test E2E (pour activer les endpoints test-only)
E2E_TEST_MODE = os.environ.get('E2E_TEST_MODE', 'False').lower() in ('1', 'true', 'yes', 'on')

# Activation globale du protocole SAKA
ENABLE_SAKA = os.environ.get('ENABLE_SAKA', 'False').lower() == 'true'  # Active la récolte + exposition global-assets

# Feature flags par fonctionnalité
SAKA_VOTE_ENABLED = os.environ.get('SAKA_VOTE_ENABLED', 'False').lower() == 'true'  # Phase 2 : Vote quadratique fertilisé
SAKA_PROJECT_BOOST_ENABLED = os.environ.get('SAKA_PROJECT_BOOST_ENABLED', 'False').lower() == 'true'  # Phase 2 : Sorgho-boosting
# ==============================================
# SAKA PROTOCOL - PHASE 3 : COMPOSTAGE & SILO COMMUN
# ==============================================
SAKA_COMPOST_ENABLED = os.environ.get('SAKA_COMPOST_ENABLED', 'False').lower() == 'true'  # Phase 3 : Compostage
SAKA_COMPOST_INACTIVITY_DAYS = int(os.environ.get('SAKA_COMPOST_INACTIVITY_DAYS', '90'))  # Durée d'inactivité avant compost (jours)
SAKA_COMPOST_RATE = float(os.environ.get('SAKA_COMPOST_RATE', '0.10'))  # % de balance à composter (10%)
SAKA_COMPOST_MIN_BALANCE = int(os.environ.get('SAKA_COMPOST_MIN_BALANCE', '50'))  # Ne composter que si balance >= 50 SAKA
SAKA_COMPOST_MIN_AMOUNT = int(os.environ.get('SAKA_COMPOST_MIN_AMOUNT', '10'))  # Composter au moins 10 SAKA quand on déclenche

# PROTECTION HOSTILE : Validation des settings SAKA critiques en production
if not DEBUG:
    # En production, le compostage DOIT être activé si SAKA est activé
    if ENABLE_SAKA and not SAKA_COMPOST_ENABLED:
        raise ImproperlyConfigured(
            "SAKA_COMPOST_ENABLED doit être True en production si ENABLE_SAKA=True. "
            "Le compostage est obligatoire pour respecter la philosophie anti-accumulation EGOEJO."
        )
    
    # En production, la redistribution DOIT être activée si SAKA est activé
    if ENABLE_SAKA and not SAKA_SILO_REDIS_ENABLED:
        raise ImproperlyConfigured(
            "SAKA_SILO_REDIS_ENABLED doit être True en production si ENABLE_SAKA=True. "
            "La redistribution est obligatoire pour respecter la philosophie de circulation obligatoire EGOEJO."
        )

# Configuration Vote Quadratique Fertilisé (Phase 2)
SAKA_VOTE_MAX_MULTIPLIER = float(os.environ.get('SAKA_VOTE_MAX_MULTIPLIER', '2.0'))  # Max x2 de poids
SAKA_VOTE_SCALE = int(os.environ.get('SAKA_VOTE_SCALE', '200'))  # 200 SAKA => +100% de poids
SAKA_VOTE_COST_PER_INTENSITY = int(os.environ.get('SAKA_VOTE_COST_PER_INTENSITY', '5'))  # Coût SAKA par unité d'intensité

# Configuration Sorgho-Boosting (Phase 2)
SAKA_PROJECT_BOOST_COST = int(os.environ.get('SAKA_PROJECT_BOOST_COST', '10'))  # Coût SAKA pour nourrir un projet

# ==============================================
# SAKA PROTOCOL - REDISTRIBUTION DU SILO (V1)
# ==============================================
# Redistribution Silo SAKA (V1)
SAKA_SILO_REDIS_ENABLED = os.environ.get('SAKA_SILO_REDIS_ENABLED', 'False').lower() == 'true'  # Active la redistribution automatique
SAKA_SILO_REDIS_RATE = float(os.environ.get('SAKA_SILO_REDIS_RATE', '0.05'))  # 5% du Silo redistribué par cycle
SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY = int(os.environ.get('SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY', '1'))  # Min total_harvested pour être éligible

# ==============================================
# VALIDATION FAIL-FAST : Settings SAKA critiques
# ==============================================
# Validation au démarrage Django - Toute valeur invalide lève ImproperlyConfigured

# Validation SAKA_COMPOST_RATE : 0 < rate <= 1
if SAKA_COMPOST_RATE <= 0:
    raise ImproperlyConfigured(
        f"SAKA_COMPOST_RATE doit être strictement supérieur à 0. "
        f"Valeur actuelle : {SAKA_COMPOST_RATE}"
    )
if SAKA_COMPOST_RATE > 1.0:
    raise ImproperlyConfigured(
        f"SAKA_COMPOST_RATE doit être strictement supérieur à 0 et inférieur ou égal à 1. "
        f"Valeur actuelle : {SAKA_COMPOST_RATE}"
    )

# Validation SAKA_COMPOST_INACTIVITY_DAYS : 1 <= days <= 365
if SAKA_COMPOST_INACTIVITY_DAYS < 1 or SAKA_COMPOST_INACTIVITY_DAYS > 365:
    raise ImproperlyConfigured(
        f"SAKA_COMPOST_INACTIVITY_DAYS doit être entre 1 et 365. "
        f"Valeur actuelle : {SAKA_COMPOST_INACTIVITY_DAYS}"
    )

# Validation SAKA_SILO_REDIS_RATE : 0 < rate <= 1
if SAKA_SILO_REDIS_RATE <= 0:
    raise ImproperlyConfigured(
        f"SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0. "
        f"Valeur actuelle : {SAKA_SILO_REDIS_RATE}"
    )
if SAKA_SILO_REDIS_RATE > 1.0:
    raise ImproperlyConfigured(
        f"SAKA_SILO_REDIS_RATE doit être strictement supérieur à 0 et inférieur ou égal à 1. "
        f"Valeur actuelle : {SAKA_SILO_REDIS_RATE}"
    )

# Validation : Si SAKA_SILO_REDIS_ENABLED = True alors SAKA_SILO_REDIS_RATE doit être valide
if SAKA_SILO_REDIS_ENABLED and (SAKA_SILO_REDIS_RATE <= 0 or SAKA_SILO_REDIS_RATE > 1.0):
    raise ImproperlyConfigured(
        f"SAKA_SILO_REDIS_ENABLED est True mais SAKA_SILO_REDIS_RATE est invalide. "
        f"Valeur actuelle : {SAKA_SILO_REDIS_RATE}"
    )

# PROTECTION HOSTILE : Validation des settings SAKA critiques en production
if not DEBUG:
    # En production, la redistribution DOIT être activée si SAKA est activé
    if ENABLE_SAKA and not SAKA_SILO_REDIS_ENABLED:
        raise ImproperlyConfigured(
            "SAKA_SILO_REDIS_ENABLED doit être True en production si ENABLE_SAKA=True. "
            "La redistribution est obligatoire pour respecter la philosophie de circulation obligatoire EGOEJO."
        )

# ==============================================
# IMPACT ORACLES (Architecture pour données externes)
# ==============================================
# Configuration des oracles d'impact (APIs externes pour enrichir P3/P4)
IMPACT_ORACLES = {
    'CO2_API_ENDPOINT': os.environ.get('IMPACT_ORACLES_CO2_API_ENDPOINT', ''),
    'CO2_API_KEY': os.environ.get('IMPACT_ORACLES_CO2_API_KEY', ''),
    'SOCIAL_API_ENDPOINT': os.environ.get('IMPACT_ORACLES_SOCIAL_API_ENDPOINT', ''),
    'SOCIAL_API_KEY': os.environ.get('IMPACT_ORACLES_SOCIAL_API_KEY', ''),
}

