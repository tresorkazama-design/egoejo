import os
from pathlib import Path
from datetime import timedelta

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

