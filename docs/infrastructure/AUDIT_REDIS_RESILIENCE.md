# Audit Infrastructure : Résilience Redis

## 📋 Vue d'ensemble

Ce document identifie tous les usages Redis dans EGOEJO et propose des fallbacks gracieux pour chaque usage.

### Objectif

Garantir que l'application continue de fonctionner même si Redis est indisponible, avec une dégradation fonctionnelle acceptable.

---

## 🔍 Usages Redis Identifiés

### 1. Django Channels (WebSockets)

**Usage** : Communication temps réel (chat, sondages)

**Configuration actuelle** :
```python
# backend/config/settings.py
if REDIS_URL:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {'hosts': [REDIS_URL]},
        }
    }
else:
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        }
    }
```

**Fallback actuel** : ✅ Déjà implémenté (InMemoryChannelLayer)

**Problème** : Pas de détection de panne Redis en cours d'exécution

---

### 2. Celery (Tâches Asynchrones)

**Usage** : Tâches en arrière-plan (emails, compostage SAKA, embeddings)

**Configuration actuelle** :
```python
# backend/config/celery.py
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
app.conf.broker_url = REDIS_URL.replace('/0', '/2')  # DB 2 pour Celery broker
app.conf.result_backend = REDIS_URL.replace('/0', '/2')  # DB 2 pour Celery results
```

**Fallback actuel** : ❌ Aucun fallback (Celery nécessite un broker)

**Problème** : Si Redis est indisponible, les tâches Celery ne peuvent pas être exécutées

---

### 3. Django Cache

**Usage** : Cache des requêtes API, projets, contenus

**Configuration actuelle** :
```python
# backend/config/settings.py
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.redis.RedisCache',
            'LOCATION': REDIS_URL.replace('/0', '/1'),  # DB 1 pour le cache
            'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
            'KEY_PREFIX': 'egoejo',
            'TIMEOUT': 300,
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
```

**Fallback actuel** : ✅ Déjà implémenté (LocMemCache)

**Problème** : Pas de détection de panne Redis en cours d'exécution

---

## 📊 Tableau Usage → Fallback

| Usage | Fallback Actuel | Fallback Proposé | Dégradation Acceptable |
|-------|----------------|------------------|------------------------|
| **Channels (WebSockets)** | InMemoryChannelLayer | ✅ Déjà implémenté | ✅ Oui - WebSockets fonctionnent mais limités à un seul worker |
| **Celery (Tâches)** | ❌ Aucun | Mode synchrone avec retry | ⚠️ Oui - Tâches exécutées de manière synchrone si Redis indisponible |
| **Cache** | LocMemCache | ✅ Déjà implémenté | ✅ Oui - Cache en mémoire (perdu au redémarrage) |

---

## 🛠️ Modifications Proposées

### 1. Détection de Panne Redis

**Fichier** : `backend/core/utils/redis_health.py` (NOUVEAU)

```python
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
        return {
            'available': False,
            'backend': cache.__class__.__name__,
            'error': str(e)
        }
```

### 2. Fallback Celery (Mode Synchrone)

**Fichier** : `backend/core/utils/celery_fallback.py` (NOUVEAU)

```python
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
        Résultat de la tâche
    """
    if check_redis_available():
        # Redis disponible, utiliser Celery normalement
        return task_func.delay(*args, **kwargs)
    else:
        # Redis indisponible, exécuter de manière synchrone
        logger.warning(
            f"Redis indisponible - Exécution synchrone de la tâche {task_func.__name__}"
        )
        return task_func(*args, **kwargs)
```

### 3. Wrapper pour Channels avec Fallback

**Fichier** : `backend/core/utils/channels_fallback.py` (NOUVEAU)

```python
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
```

### 4. Wrapper pour Cache avec Fallback

**Fichier** : `backend/core/utils/cache_fallback.py` (NOUVEAU)

```python
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
        logger.warning(f"Erreur lors de la récupération du cache ({key}) : {e}")
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
        logger.warning(f"Erreur lors de la définition du cache ({key}) : {e}")
        return False
```

---

## 📝 Modifications Minimales de Code

### 1. Modifier les tâches Celery pour utiliser le fallback

**Fichier** : `backend/core/tasks.py`

```python
# Ajouter en haut du fichier
from core.utils.celery_fallback import execute_task_sync

# Modifier les appels de tâches
# AVANT :
send_email_task.delay(to_email, subject, html_content)

# APRÈS :
execute_task_sync(send_email_task, to_email, subject, html_content)
```

### 2. Modifier les consumers pour utiliser le fallback

**Fichier** : `backend/core/consumers.py`

```python
# Ajouter en haut du fichier
from core.utils.channels_fallback import safe_group_send

# Modifier les appels group_send
# AVANT :
await self.channel_layer.group_send(self.group_name, message)

# APRÈS :
if not safe_group_send(self.group_name, message):
    logger.warning(f"Impossible d'envoyer le message au groupe {self.group_name}")
```

### 3. Modifier les vues utilisant le cache

**Fichier** : `backend/core/api/projects.py`

```python
# Ajouter en haut du fichier
from core.utils.cache_fallback import safe_cache_get, safe_cache_set

# Modifier les appels cache
# AVANT :
cached_data = cache.get(cache_key)

# APRÈS :
cached_data = safe_cache_get(cache_key)
```

---

## 🧪 Test de Résilience

**Fichier** : `backend/tests/infrastructure/test_redis_resilience.py` (NOUVEAU)

```python
"""
Tests de résilience Redis
"""
import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.cache import cache
from core.utils.redis_health import check_redis_available, get_redis_status
from core.utils.cache_fallback import safe_cache_get, safe_cache_set
from core.utils.channels_fallback import safe_group_send
from core.utils.celery_fallback import execute_task_sync

class TestRedisResilience(TestCase):
    """Tests de résilience en cas de panne Redis"""
    
    def test_redis_health_check_success(self):
        """Test que la vérification de santé Redis fonctionne"""
        status = get_redis_status()
        self.assertIn('available', status)
        self.assertIn('backend', status)
    
    def test_redis_health_check_failure(self):
        """Test que la vérification de santé détecte une panne Redis"""
        with patch('django.core.cache.cache.set', side_effect=Exception("Redis unavailable")):
            available = check_redis_available()
            self.assertFalse(available)
    
    def test_cache_fallback_on_redis_failure(self):
        """Test que le cache fonctionne avec fallback si Redis est indisponible"""
        # Simuler une panne Redis
        with patch('django.core.cache.cache.set', side_effect=Exception("Redis unavailable")):
            result = safe_cache_set('test_key', 'test_value')
            self.assertFalse(result)  # Doit retourner False mais ne pas crasher
        
        # Test de récupération avec fallback
        with patch('django.core.cache.cache.get', side_effect=Exception("Redis unavailable")):
            result = safe_cache_get('test_key', 'default_value')
            self.assertEqual(result, 'default_value')  # Doit retourner la valeur par défaut
    
    def test_channels_fallback_on_redis_failure(self):
        """Test que Channels fonctionne avec fallback si Redis est indisponible"""
        # Simuler une panne Redis
        with patch('channels.layers.get_channel_layer', side_effect=Exception("Redis unavailable")):
            result = safe_group_send('test_group', {'type': 'test_message'})
            self.assertFalse(result)  # Doit retourner False mais ne pas crasher
    
    def test_celery_fallback_on_redis_failure(self):
        """Test que Celery fonctionne avec fallback si Redis est indisponible"""
        # Créer une tâche de test
        @shared_task
        def test_task(value):
            return value * 2
        
        # Simuler une panne Redis
        with patch('core.utils.redis_health.check_redis_available', return_value=False):
            # La tâche doit être exécutée de manière synchrone
            result = execute_task_sync(test_task, 5)
            self.assertEqual(result, 10)  # 5 * 2 = 10
```

---

## 📊 Logs Explicites

### Ajout de logs dans les utilitaires

Tous les utilitaires de fallback incluent des logs explicites :

```python
logger.error(f"Redis indisponible : {e}", exc_info=True)
logger.warning(f"Redis indisponible - Exécution synchrone de la tâche {task_func.__name__}")
logger.warning(f"Erreur lors de la récupération du cache ({key}) : {e}")
```

### Monitoring Redis

**Fichier** : `backend/core/tasks_monitoring.py`

Ajouter une tâche de monitoring Redis :

```python
@shared_task
def check_redis_health():
    """
    Tâche de monitoring Redis (exécutée toutes les heures)
    """
    from core.utils.redis_health import get_redis_status
    
    status = get_redis_status()
    
    if not status['available']:
        logger.critical(
            f"Redis indisponible - Backend: {status['backend']}, "
            f"Erreur: {status['error']}"
        )
    else:
        logger.info(f"Redis disponible - Backend: {status['backend']}")
    
    return status
```

---

## ✅ Checklist de Validation

- [ ] Utilitaires de fallback créés
- [ ] Modifications minimales appliquées
- [ ] Tests de résilience créés
- [ ] Logs explicites ajoutés
- [ ] Monitoring Redis configuré
- [ ] Documentation mise à jour

---

**Fin du document**

*La résilience Redis garantit que l'application continue de fonctionner même en cas de panne Redis, avec une dégradation fonctionnelle acceptable.*

