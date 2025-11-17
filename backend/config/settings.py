
import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY must be set")
if len(SECRET_KEY) < 50:
    import warnings
    warnings.warn("SECRET_KEY should be at least 50 characters long for production use")

DEBUG = os.environ.get('DEBUG', '0') == '1'

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
    # Vérifier si on est sur Railway via la présence de certaines variables
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_PROJECT_ID'):
        # Extraire le domaine depuis RAILWAY_PUBLIC_DOMAIN
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        if railway_domain:
            # Ajouter le domaine Railway si pas déjà présent
            if railway_domain not in ALLOWED_HOSTS:
                ALLOWED_HOSTS.append(railway_domain)
        elif not ALLOWED_HOSTS:
            # Si pas de domaine Railway et ALLOWED_HOSTS vide, générer une erreur
            raise RuntimeError(
                "ALLOWED_HOSTS must be set in production. "
                "Set RAILWAY_PUBLIC_DOMAIN or ALLOWED_HOSTS environment variable."
            )

INSTALLED_APPS = [
    'jazzmin', # <--- AJOUTEZ ICI EN PREMIER
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt.token_blacklist',
    'core', # <--- Votre application Core
]
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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
    'OPTIONS': {'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
    ]},
}]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

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

# Support DATABASE_URL (standard Railway/Heroku) ou variables individuelles
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    import dj_database_url
    db_config = dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    # Configuration optimisée pour Railway (évite les timeouts de connexion)
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

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Configuration de sécurité (redéfinie plus bas selon DEBUG)
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
_static_dir = BASE_DIR / 'static'
STATICFILES_DIRS = [_static_dir] if _static_dir.exists() else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOWED_ORIGINS = [u.strip() for u in os.environ.get('CORS_ALLOWED_ORIGINS','').split(',') if u.strip()]
CSRF_TRUSTED_ORIGINS = [u.strip() for u in os.environ.get('CSRF_TRUSTED_ORIGINS','').split(',') if u.strip()]

# Si CORS_ALLOWED_ORIGINS est vide en développement, autoriser localhost par défaut
if DEBUG and not CORS_ALLOWED_ORIGINS:
    CORS_ALLOWED_ORIGINS = [
        'http://localhost:3000',
        'http://localhost:5173',
        'http://127.0.0.1:3000',
        'http://127.0.0.1:5173',
    ]
    CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

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
    }
else:
    REST_FRAMEWORK = {
        'DEFAULT_AUTHENTICATION_CLASSES': _auth_classes,
        'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle','rest_framework.throttling.UserRateThrottle'],
        'DEFAULT_THROTTLE_RATES': {'anon': os.environ.get('THROTTLE_ANON','10/minute'), 'user': os.environ.get('THROTTLE_USER','100/minute')}
    }

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get('ACCESS_TOKEN_MINUTES','60'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('REFRESH_TOKEN_DAYS','7'))),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('JWT',),
}

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

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST','')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT') or 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER','')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD','')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS','1') == '1'

# ====================================================================
# CORRECTION DÉFINITIVE POUR DÉVELOPPEMENT LOCAL (HTTPS/SSL)
# Force le SSL/Cookies sécurisés à OFF quand DEBUG=True (pour localhost)
# ====================================================================
if DEBUG:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_SECONDS = 0
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    # En production, forcer HTTPS et cookies sécurisés
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '31536000'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('SECURE_HSTS_INCLUDE_SUBDOMAINS', '1') == '1'
    SECURE_HSTS_PRELOAD = os.environ.get('SECURE_HSTS_PRELOAD', '1') == '1'
# Fichiers Média (Images, Vidéos, PDF uploadés par les utilisateurs)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'