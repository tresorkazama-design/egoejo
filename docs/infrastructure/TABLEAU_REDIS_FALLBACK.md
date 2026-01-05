# Tableau Usage Redis → Fallback

## 📊 Vue d'ensemble

| Usage | Fallback Actuel | Fallback Proposé | Dégradation Acceptable | Logs | Test |
|-------|----------------|------------------|------------------------|------|------|
| **Channels (WebSockets)** | InMemoryChannelLayer | ✅ Déjà implémenté + `safe_group_send()` | ✅ Oui - WebSockets fonctionnent mais limités à un seul worker | ✅ `logger.error()` | ✅ Test créé |
| **Celery (Tâches)** | ❌ Aucun | `execute_task_sync()` - Mode synchrone | ⚠️ Oui - Tâches exécutées de manière synchrone | ✅ `logger.warning()` | ✅ Test créé |
| **Cache** | LocMemCache | ✅ Déjà implémenté + `safe_cache_*()` | ✅ Oui - Cache en mémoire (perdu au redémarrage) | ✅ `logger.warning()` | ✅ Test créé |

---

## 🔍 Détails par Usage

### 1. Channels (WebSockets)

**Usage** : Communication temps réel (chat, sondages)

**Configuration** :
- Redis : `channels_redis.core.RedisChannelLayer`
- Fallback : `channels.layers.InMemoryChannelLayer`

**Fallback Proposé** :
- Wrapper `safe_group_send()` qui gère les exceptions
- Logs explicites en cas d'erreur

**Dégradation** :
- ✅ WebSockets fonctionnent mais limités à un seul worker
- ✅ Messages perdus si plusieurs workers (acceptable)

**Code** :
```python
from core.utils.channels_fallback import safe_group_send

# Utilisation
if not safe_group_send(self.group_name, message):
    logger.warning(f"Impossible d'envoyer le message au groupe {self.group_name}")
```

---

### 2. Celery (Tâches Asynchrones)

**Usage** : Tâches en arrière-plan (emails, compostage SAKA, embeddings)

**Configuration** :
- Redis : Broker et backend Celery (DB 2)

**Fallback Proposé** :
- Wrapper `execute_task_sync()` qui exécute de manière synchrone si Redis indisponible
- Logs explicites en cas de fallback

**Dégradation** :
- ⚠️ Tâches exécutées de manière synchrone (peut ralentir les requêtes)
- ✅ Fonctionnalité préservée (emails envoyés, compostage exécuté)

**Code** :
```python
from core.utils.celery_fallback import execute_task_sync

# Utilisation
execute_task_sync(send_email_task, to_email, subject, html_content)
```

---

### 3. Cache

**Usage** : Cache des requêtes API, projets, contenus

**Configuration** :
- Redis : `django.core.cache.backends.redis.RedisCache` (DB 1)
- Fallback : `django.core.cache.backends.locmem.LocMemCache`

**Fallback Proposé** :
- Wrappers `safe_cache_get()`, `safe_cache_set()`, `safe_cache_delete()`
- Logs explicites en cas d'erreur

**Dégradation** :
- ✅ Cache en mémoire (perdu au redémarrage)
- ✅ Performance légèrement réduite (cache local vs Redis)

**Code** :
```python
from core.utils.cache_fallback import safe_cache_get, safe_cache_set

# Utilisation
cached_data = safe_cache_get('key', default_value)
safe_cache_set('key', value, 300)
```

---

## 📝 Modifications Minimales

### Fichiers à Modifier

1. **`backend/core/api/projects.py`** (cache)
   - Remplacer `cache.get()` par `safe_cache_get()`
   - Remplacer `cache.set()` par `safe_cache_set()`

2. **`backend/core/consumers.py`** (channels)
   - Remplacer `await self.channel_layer.group_send()` par `safe_group_send()`

3. **`backend/core/tasks.py`** (celery)
   - Remplacer `.delay()` par `execute_task_sync()`

4. **`backend/core/api/impact_views.py`** (celery)
   - Remplacer `.delay()` par `execute_task_sync()`

5. **`backend/core/api/content_views.py`** (celery)
   - Remplacer `.delay()` par `execute_task_sync()`

---

## ✅ Validation

### Tests

- ✅ 10 tests de résilience créés
- ✅ Tous les tests passent (sauf 1 à corriger)
- ✅ Couverture : Cache, Channels, Celery

### Logs

- ✅ Logs ERROR pour pannes Redis
- ✅ Logs WARNING pour fallbacks activés
- ✅ Logs INFO pour Redis disponible

---

**Fin du document**

*Le tableau résume tous les usages Redis et leurs fallbacks gracieux.*

