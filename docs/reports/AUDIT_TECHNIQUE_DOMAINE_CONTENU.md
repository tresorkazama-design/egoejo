# AUDIT TECHNIQUE STRICT : DOMAINE "CONTENU" (Backend)

**Date** : 2025-01-XX  
**Auditeur** : Senior Technical Auditor  
**Scope** : Backend Django - Domaine Contenu (EducationalContent, Intent, Media, etc.)

---

## 1. CARTOGRAPHIE

### 1.1 Modèles Django

| Modèle | Fichier | Relations | Description |
|--------|---------|-----------|-------------|
| `EducationalContent` | `backend/core/models/content.py` | `author` → User (SET_NULL), `project` → Projet (SET_NULL), `likes` (reverse FK), `comments` (reverse FK) | Contenu éducatif (podcast, vidéo, PDF, article, poème, chanson) |
| `ContentLike` | `backend/core/models/content.py` | `user` → User (CASCADE), `content` → EducationalContent (CASCADE), `unique_together(user, content)` | Like sur un contenu (1 like max par user) |
| `ContentComment` | `backend/core/models/content.py` | `user` → User (SET_NULL), `content` → EducationalContent (CASCADE) | Commentaire sur un contenu |
| `Intent` | `backend/core/models/intents.py` | Aucune relation | Intention d'engagement (formulaire Rejoindre) |
| `Media` | `backend/core/models/projects.py` | `projet` → Projet (CASCADE) | Média associé à un projet (pas directement lié au contenu éducatif) |

**Relations identifiées :**
- `EducationalContent.author` → `User` (nullable, SET_NULL)
- `EducationalContent.project` → `Projet` (nullable, SET_NULL)
- `ContentLike.user` → `User` (CASCADE)
- `ContentLike.content` → `EducationalContent` (CASCADE)
- `ContentComment.user` → `User` (nullable, SET_NULL)
- `ContentComment.content` → `EducationalContent` (CASCADE)

### 1.2 Endpoints DRF

| Endpoint | Méthode | Route | ViewSet/View | Permissions | Serializer |
|----------|---------|-------|--------------|-------------|------------|
| Liste contenus | GET | `/api/contents/` | `EducationalContentViewSet.list()` | `AllowAny` | `EducationalContentSerializer` |
| Détail contenu | GET | `/api/contents/{id}/` | `EducationalContentViewSet.retrieve()` | `AllowAny` | `EducationalContentSerializer` |
| Créer contenu | POST | `/api/contents/` | `EducationalContentViewSet.create()` | `AllowAny` | `EducationalContentSerializer` |
| Publier contenu | POST | `/api/contents/{id}/publish/` | `EducationalContentViewSet.publish()` | `AllowAny` | `EducationalContentSerializer` |
| Marquer consommé | POST | `/api/contents/{id}/mark-consumed/` | `EducationalContentViewSet.mark_consumed()` | `IsAuthenticated` (vérifié manuellement) | N/A |
| Rejoindre (Intent) | POST | `/api/rejoindre/` | `rejoindre()` | `AllowAny` | `IntentSerializer` |
| Admin Intent | GET | `/api/intents/admin/` | `admin_data()` | `require_admin_token()` | `IntentSerializer` |
| Export Intent | GET | `/api/intents/export/` | `export_intents()` | `require_admin_token()` | CSV |
| Delete Intent | DELETE | `/api/intents/{id}/` | `delete_intent()` | `require_admin_token()` | N/A |

**Fichiers :**
- `backend/core/api/content_views.py` : EducationalContentViewSet
- `backend/core/api/intents.py` : Intent endpoints
- `backend/core/urls.py` : Routes DRF
- `backend/config/urls.py` : Routes legacy (doublon)

### 1.3 Tasks Celery

| Task | Fichier | Déclencheur | Description |
|------|---------|-------------|-------------|
| `scan_file_antivirus` | `backend/core/tasks_security.py` | Upload fichier (`EducationalContent.file`) | Scan ClamAV (optionnel, fallback si non disponible) |
| `validate_file_type` | `backend/core/tasks_security.py` | Upload fichier (`EducationalContent.file`) | Validation type MIME avec `python-magic` |
| `generate_embedding_task` | `backend/core/tasks_embeddings.py` | Création contenu | Génération embedding (OpenAI ou Sentence Transformers) |
| `batch_generate_embeddings` | `backend/core/tasks_embeddings.py` | Manuel/admin | Batch génération embeddings |
| `generate_audio_content` | `backend/core/tasks_audio.py` | Publication contenu (`publish/`) | Génération TTS (OpenAI ou ElevenLabs) |
| `batch_generate_audio` | `backend/core/tasks_audio.py` | Manuel/admin | Batch génération audio |

**Dépendances externes :**
- ClamAV (antivirus) : Optionnel, fallback si non disponible
- `python-magic` : Optionnel, fallback si non installé
- OpenAI API : Embeddings + TTS
- ElevenLabs API : TTS alternatif
- Sentence Transformers : Embeddings local (fallback)

---

## 2. CMS/ADMIN

### 2.1 Django Admin

**EducationalContentAdmin** (`backend/core/admin.py:62-66`) :
- ✅ `list_display` : `("title", "type", "status", "created_at")`
- ✅ `list_filter` : `("type", "status", "created_at")`
- ✅ `search_fields` : `("title", "description")`
- ✅ `prepopulated_fields` : `{"slug": ("title",)}`
- ❌ **MANQUE** : `readonly_fields` (pour `created_at`, `updated_at`, `embedding_source_hash`, `audio_source_hash`)
- ❌ **MANQUE** : `date_hierarchy` (pour navigation temporelle)
- ❌ **MANQUE** : `actions` personnalisées (publier en masse, générer audio en masse)
- ❌ **MANQUE** : `raw_id_fields` (pour `author`, `project` si beaucoup d'utilisateurs/projets)
- ❌ **MANQUE** : `autocomplete_fields` (pour recherche rapide)

**ContentLike** et **ContentComment** :
- ❌ **MANQUE** : Admin personnalisé (enregistrement simple uniquement)
- ❌ **MANQUE** : Filtres, recherche, actions

**Intent** :
- ❌ **MANQUE** : Admin personnalisé (enregistrement simple uniquement)
- ❌ **MANQUE** : Filtres par date, profil, export CSV depuis admin

### 2.2 Audit Log

- ❌ **MANQUE** : Aucun log d'audit (`AuditLog`) pour les modifications de `EducationalContent`
- ❌ **MANQUE** : Pas de tracking des changements de statut (draft → pending → published)
- ❌ **MANQUE** : Pas de tracking des publications/dépublications

**Fichier concerné** : `backend/core/admin.py`

### 2.3 Versioning

- ❌ **MANQUE** : Aucun système de versioning (pas de `django-reversion` ou équivalent)
- ❌ **MANQUE** : Pas de gestion des "edits" (historique des modifications)
- ❌ **MANQUE** : Pas de rollback possible

**Risque** : Perte de données en cas de modification accidentelle, pas de traçabilité des changements.

### 2.4 Soft Delete / Archivage

- ❌ **MANQUE** : Pas de soft delete (suppression définitive uniquement)
- ❌ **MANQUE** : Pas de champ `is_deleted` ou `deleted_at`
- ❌ **MANQUE** : Pas d'archivage automatique des contenus anciens

**Risque** : Perte de données en cas de suppression accidentelle, pas de récupération possible.

---

## 3. SÉCURITÉ & CONFORMITÉ EGOEJO

### 3.1 Séparation SAKA/EUR

✅ **CONFORME** : Aucune interaction avec le domaine EUR détectée
- `EducationalContent` n'a pas de ForeignKey vers `UserWallet` ou modèles finance
- Les endpoints de contenu n'utilisent pas `formatMoney` ou fonctions EUR
- Le système SAKA est utilisé uniquement pour la récolte (`harvest_saka`) lors de la consommation de contenu

**Vérification** : Aucun pattern `EUR`, `€`, `finance`, `money`, `currency` détecté dans `content_views.py` et `content.py`.

### 3.2 Upload de fichiers

**Validation actuelle** :
- ✅ Scan antivirus asynchrone (`scan_file_antivirus`) via ClamAV
- ✅ Validation type MIME (`validate_file_type`) via `python-magic`
- ❌ **MANQUE** : Limite de taille de fichier explicite dans le modèle
- ❌ **MANQUE** : Validation de la taille dans le serializer
- ❌ **MANQUE** : Validation du nom de fichier (caractères spéciaux, longueur)
- ❌ **MANQUE** : Validation de l'extension (whitelist)
- ❌ **MANQUE** : Quarantaine temporaire avant publication (fichier scanné mais non accessible)

**Fichiers concernés** :
- `backend/core/models/content.py` : `file` et `audio_file` (pas de `max_length` ou validation)
- `backend/core/api/content_views.py` : `perform_create()` (pas de validation taille)
- `backend/core/serializers/content.py` : Pas de validation custom

**Risque** : Upload de fichiers volumineux (DoS), fichiers malveillants non détectés si ClamAV indisponible.

### 3.3 Rate Limiting

**Configuration actuelle** :
- ✅ Rate limiting global DRF activé (`AnonRateThrottle`, `UserRateThrottle`)
- ✅ Limites : `anon: 10/minute`, `user: 100/minute`, `ip: 100/hour`
- ❌ **MANQUE** : Rate limiting spécifique pour `/api/contents/` (upload de fichiers)
- ❌ **MANQUE** : Rate limiting pour `/api/contents/{id}/mark-consumed/` (prévention abus SAKA)
- ❌ **MANQUE** : Rate limiting pour `/api/rejoindre/` (prévention spam)

**Fichiers concernés** :
- `backend/config/settings.py` : Configuration globale uniquement
- `backend/core/api/content_views.py` : Pas de `throttle_classes` spécifique

**Risque** : Abus de création de contenus, spam d'intentions, exploitation du système SAKA.

### 3.4 XSS / HTML Sanitization

**Sanitization actuelle** :
- ✅ Module `backend/core/security/sanitization.py` existe avec `sanitize_string()`
- ❌ **MANQUE** : Aucune utilisation de `sanitize_string()` dans `EducationalContentSerializer`
- ❌ **MANQUE** : Pas de sanitization du champ `description` (TextField, peut contenir HTML)
- ❌ **MANQUE** : Pas de sanitization du champ `text` dans `ContentComment`
- ❌ **MANQUE** : Pas de sanitization du champ `message` dans `Intent`

**Fichiers concernés** :
- `backend/core/serializers/content.py` : Pas de validation/sanitization
- `backend/core/api/intents.py` : Pas de sanitization du `message`

**Risque** : Injection XSS via description, commentaires, messages d'intention.

---

## 4. ROBUSTESSE & PERFORMANCE

### 4.1 N+1 Queries

**Problèmes identifiés** :
- ❌ **MANQUE** : Pas de `select_related()` pour `author` dans `get_queryset()`
- ❌ **MANQUE** : Pas de `select_related()` pour `project` dans `get_queryset()`
- ❌ **MANQUE** : Pas de `prefetch_related()` pour `likes` et `comments` dans `get_queryset()`
- ❌ **MANQUE** : Propriétés `likes_count` et `comments_count` utilisent `.count()` (N+1)

**Fichier concerné** : `backend/core/api/content_views.py:94-104`

**Impact** : Si 100 contenus avec 10 likes et 5 commentaires chacun → 1 + 100 + 1000 + 500 = 1601 requêtes.

### 4.2 Index Database

**Index existants** :
- ✅ `slug` : `unique=True` (index automatique)
- ❌ **MANQUE** : Pas d'index sur `status` (filtrage fréquent)
- ❌ **MANQUE** : Pas d'index sur `created_at` (tri par défaut)
- ❌ **MANQUE** : Pas d'index sur `type` (filtrage)
- ❌ **MANQUE** : Pas d'index sur `category` (filtrage)
- ❌ **MANQUE** : Pas d'index composite `(status, created_at)` pour requêtes filtrées + triées
- ❌ **MANQUE** : Pas d'index sur `author` (Foreign Key, index automatique mais pas optimisé pour requêtes fréquentes)
- ❌ **MANQUE** : Pas d'index sur `ContentLike(user, content)` (déjà `unique_together`, mais pas d'index explicite)
- ❌ **MANQUE** : Pas d'index sur `ContentComment(content, created_at)` (tri fréquent)

**Fichiers concernés** :
- `backend/core/models/content.py` : Pas de `class Meta: indexes = [...]`
- Migrations : Aucune migration d'index détectée

**Impact** : Requêtes lentes sur grandes tables, scans complets de table pour filtres.

### 4.3 Pagination

- ❌ **MANQUE** : Pas de pagination configurée dans `EducationalContentViewSet`
- ❌ **MANQUE** : Pas de `pagination_class` dans le ViewSet
- ❌ **MANQUE** : Pas de configuration globale de pagination DRF pour ce ViewSet

**Fichier concerné** : `backend/core/api/content_views.py`

**Risque** : Retour de milliers de contenus en une seule requête (DoS, performance).

### 4.4 Cache Redis

**Cache actuel** :
- ✅ Cache Redis pour liste des contenus publiés (`educational_contents_published`, 10 min)
- ✅ Invalidation du cache lors de la publication (`cache.delete()`)
- ❌ **MANQUE** : Pas de cache pour le détail d'un contenu (`/api/contents/{id}/`)
- ❌ **MANQUE** : Pas de cache pour les filtres par `type` ou `category`
- ❌ **MANQUE** : Pas de stratégie d'invalidation lors de modification d'un contenu (hors publication)
- ❌ **MANQUE** : Pas de cache pour les likes/comments count (calculés à chaque requête)

**Fichier concerné** : `backend/core/api/content_views.py:35-92`

**Impact** : Charge DB inutile pour contenus fréquemment consultés.

### 4.5 Monitoring & Métriques

**Monitoring actuel** :
- ✅ Logging basique (`logger.error`, `logger.warning`) dans les tasks Celery
- ❌ **MANQUE** : Pas d'intégration Sentry pour les erreurs critiques
- ❌ **MANQUE** : Pas de métriques de performance (temps de réponse, nombre de requêtes)
- ❌ **MANQUE** : Pas de tracking des uploads de fichiers (taille, type, échecs)
- ❌ **MANQUE** : Pas de tracking des générations d'embeddings/audio (succès/échecs, coûts)
- ❌ **MANQUE** : Pas d'alertes sur les échecs de scan antivirus

**Fichiers concernés** :
- `backend/core/api/content_views.py` : Pas de monitoring
- `backend/core/tasks_audio.py` : Logging basique uniquement
- `backend/core/tasks_embeddings.py` : Logging basique uniquement
- `backend/core/tasks_security.py` : Logging basique uniquement

---

## 5. TABLEAU DE PROBLÈMES

| Problème | Gravité | Fichier(s) | Correctif proposé | Test à ajouter |
|----------|---------|------------|-------------------|---------------|
| **Pas d'index DB sur `status`, `created_at`, `type`, `category`** | 🔴 CRITIQUE | `backend/core/models/content.py` | Ajouter `class Meta: indexes = [models.Index(fields=['status', 'created_at']), models.Index(fields=['type']), models.Index(fields=['category'])]` | Test de performance avec 1000+ contenus |
| **N+1 queries dans `get_queryset()`** | 🔴 CRITIQUE | `backend/core/api/content_views.py:94-104` | Ajouter `select_related('author', 'project').prefetch_related('likes', 'comments')` | Test avec `assertNumQueries()` |
| **Pas de pagination** | 🔴 CRITIQUE | `backend/core/api/content_views.py` | Ajouter `pagination_class = PageNumberPagination` et configurer `page_size = 20` | Test pagination avec 100+ contenus |
| **Pas de limite de taille de fichier** | 🔴 CRITIQUE | `backend/core/models/content.py`, `backend/core/api/content_views.py` | Ajouter validation dans serializer : `max_size = 50 * 1024 * 1024` (50MB) | Test upload fichier > 50MB |
| **Pas de sanitization XSS** | 🔴 CRITIQUE | `backend/core/serializers/content.py`, `backend/core/api/intents.py` | Utiliser `sanitize_string()` dans `validate_description()`, `validate_text()`, `validate_message()` | Test injection XSS dans description/commentaire |
| **Pas de rate limiting spécifique upload** | 🟡 ÉLEVÉ | `backend/core/api/content_views.py` | Ajouter `throttle_classes = [UserRateThrottle]` avec limite `5/minute` pour `create()` | Test rate limit upload |
| **Pas de rate limiting pour `mark-consumed`** | 🟡 ÉLEVÉ | `backend/core/api/content_views.py:172` | Ajouter `throttle_classes = [UserRateThrottle]` avec limite `10/minute` | Test rate limit mark-consumed |
| **Pas de cache pour détail contenu** | 🟡 ÉLEVÉ | `backend/core/api/content_views.py` | Ajouter cache dans `retrieve()` : `cache.get(f'content_{pk}')` avec TTL 5 min | Test cache hit/miss |
| **Pas d'audit log** | 🟡 ÉLEVÉ | `backend/core/admin.py`, `backend/core/api/content_views.py` | Utiliser `AuditLog.objects.create()` dans `publish()` et `perform_create()` | Test création AuditLog |
| **Pas de versioning** | 🟡 ÉLEVÉ | `backend/core/models/content.py` | Installer `django-reversion` et enregistrer `EducationalContent` | Test rollback version |
| **Pas de soft delete** | 🟡 ÉLEVÉ | `backend/core/models/content.py` | Ajouter `is_deleted = BooleanField(default=False)`, `deleted_at = DateTimeField(null=True)` | Test soft delete + récupération |
| **Admin incomplet** | 🟠 MOYEN | `backend/core/admin.py:62-66` | Ajouter `readonly_fields`, `date_hierarchy`, `actions`, `raw_id_fields` | Test admin fonctionnalités |
| **Pas de validation extension fichier** | 🟠 MOYEN | `backend/core/api/content_views.py:148-158` | Ajouter whitelist extensions : `['.pdf', '.mp3', '.mp4', '.jpg', '.png']` | Test upload extension interdite |
| **Pas de validation nom fichier** | 🟠 MOYEN | `backend/core/api/content_views.py` | Sanitizer nom fichier (caractères spéciaux, longueur max 255) | Test nom fichier malveillant |
| **Pas de monitoring Sentry** | 🟠 MOYEN | `backend/core/api/content_views.py`, `backend/core/tasks_*.py` | Intégrer `sentry_sdk.capture_exception()` dans les `except Exception` | Test erreur Sentry |
| **Pas de métriques performance** | 🟠 MOYEN | `backend/core/api/content_views.py` | Utiliser `PerformanceMetric.objects.create()` pour tracking temps réponse | Test métriques |
| **Cache invalidation incomplète** | 🟠 MOYEN | `backend/core/api/content_views.py:170, 295` | Invalider cache lors de modification (pas seulement publication) | Test invalidation cache |
| **Pas de quarantaine fichiers** | 🟠 MOYEN | `backend/core/api/content_views.py:148-158` | Marquer fichier comme "quarantaine" jusqu'à scan antivirus OK | Test quarantaine |
| **Fallback ClamAV trop permissif** | 🟠 MOYEN | `backend/core/tasks_security.py:28-33` | Si ClamAV indisponible, bloquer upload (ne pas considérer comme sûr) | Test ClamAV indisponible |
| **Pas d'index composite** | 🟠 MOYEN | `backend/core/models/content.py` | Ajouter `models.Index(fields=['status', 'created_at'])` | Test requête filtrée + triée |
| **Propriétés `likes_count`/`comments_count` N+1** | 🟠 MOYEN | `backend/core/models/content.py:131-137` | Utiliser `annotate(likes_count=Count('likes'))` dans queryset | Test N+1 avec `assertNumQueries()` |
| **Pas de validation hash embedding/audio** | 🟢 FAIBLE | `backend/core/tasks_embeddings.py`, `backend/core/tasks_audio.py` | Vérifier hash avant génération (déjà fait partiellement) | Test hash identique skip |
| **Admin Intent basique** | 🟢 FAIBLE | `backend/core/admin.py:97` | Ajouter admin personnalisé avec filtres, recherche, export | Test admin Intent |
| **Pas de validation tags JSON** | 🟢 FAIBLE | `backend/core/models/content.py:49-53` | Valider format tags (liste de strings, max 10 tags, longueur max) | Test tags invalides |
| **Doublon routes** | 🟢 FAIBLE | `backend/config/urls.py:93-102` | Supprimer routes legacy, utiliser uniquement `core/urls.py` | Test routes uniques |

---

## 6. TESTS MANQUANTS

### 6.1 Tests Unitaires

**Modèles** :
- ❌ Test validation `EducationalContent` (champs requis, choix valides)
- ❌ Test `compute_text_hash()` (hash identique pour même texte)
- ❌ Test `likes_count` et `comments_count` (propriétés)
- ❌ Test `ContentLike.unique_together` (1 like max par user)
- ❌ Test `Intent` validation (email, message longueur)

**Serializers** :
- ❌ Test `EducationalContentSerializer` validation (champs requis)
- ❌ Test sanitization XSS dans serializer
- ❌ Test validation taille fichier dans serializer
- ❌ Test `read_only_fields` (status, created_at)

### 6.2 Tests API

**Endpoints** :
- ❌ Test pagination `/api/contents/` (page, page_size)
- ❌ Test filtres multiples (`?status=published&type=article&category=guides`)
- ❌ Test rate limiting upload (`POST /api/contents/`)
- ❌ Test rate limiting mark-consumed
- ❌ Test cache hit/miss pour liste et détail
- ❌ Test invalidation cache lors modification
- ❌ Test upload fichier > limite taille (400 Bad Request)
- ❌ Test upload extension interdite (400 Bad Request)
- ❌ Test scan antivirus échoue (fichier malveillant supprimé)
- ❌ Test génération embedding échoue (retry, fallback)
- ❌ Test génération audio échoue (retry, fallback)

**Permissions** :
- ❌ Test `publish/` sans authentification (devrait fonctionner mais loguer)
- ❌ Test `mark-consumed/` sans authentification (401)
- ❌ Test création contenu anonyme (author=null)

### 6.3 Tests Celery Integration

**Tasks** :
- ❌ Test `scan_file_antivirus` avec ClamAV disponible
- ❌ Test `scan_file_antivirus` avec ClamAV indisponible (fallback)
- ❌ Test `validate_file_type` avec `python-magic` disponible
- ❌ Test `validate_file_type` avec `python-magic` indisponible (fallback)
- ❌ Test `generate_embedding_task` OpenAI (succès)
- ❌ Test `generate_embedding_task` OpenAI (échec, retry)
- ❌ Test `generate_embedding_task` Sentence Transformers (fallback)
- ❌ Test `generate_audio_content` OpenAI (succès)
- ❌ Test `generate_audio_content` hash identique (skip)
- ❌ Test `batch_generate_embeddings` (batch processing)

### 6.4 Tests Performance

- ❌ Test N+1 queries avec 100 contenus (assertNumQueries < 10)
- ❌ Test requête avec index (EXPLAIN ANALYZE)
- ❌ Test cache performance (temps réponse < 50ms)
- ❌ Test pagination performance (1000+ contenus)

### 6.5 Tests Sécurité

- ❌ Test injection XSS dans `description` (échappement HTML)
- ❌ Test injection XSS dans `ContentComment.text`
- ❌ Test upload fichier malveillant (suppression automatique)
- ❌ Test upload fichier volumineux (DoS)
- ❌ Test rate limiting (429 Too Many Requests)
- ❌ Test honeypot Intent (détection spam)

### 6.6 Tests Conformité EGOEJO

- ❌ Test aucune interaction EUR dans domain contenu
- ❌ Test SAKA récolte uniquement via `mark-consumed` (pas de conversion)
- ❌ Test pas de symboles monétaires dans endpoints contenu

---

## 7. RECOMMANDATIONS PRIORITAIRES

### 🔴 CRITIQUE (À corriger immédiatement)

1. **Ajouter index DB** : `status`, `created_at`, `type`, `category` + index composite
2. **Corriger N+1 queries** : `select_related()` + `prefetch_related()` + `annotate()`
3. **Ajouter pagination** : `PageNumberPagination` avec `page_size = 20`
4. **Limiter taille fichiers** : Validation 50MB max dans serializer
5. **Sanitization XSS** : Utiliser `sanitize_string()` dans tous les serializers

### 🟡 ÉLEVÉ (À corriger rapidement)

6. **Rate limiting upload** : 5/minute pour `create()`
7. **Rate limiting mark-consumed** : 10/minute pour prévenir abus SAKA
8. **Cache détail contenu** : TTL 5 minutes
9. **Audit log** : Tracking modifications statut
10. **Versioning** : `django-reversion` pour historique
11. **Soft delete** : Champ `is_deleted` + `deleted_at`

### 🟠 MOYEN (Amélioration continue)

12. **Admin amélioré** : Filtres, actions, readonly_fields
13. **Validation fichiers** : Extension whitelist, nom fichier
14. **Monitoring Sentry** : Intégration erreurs critiques
15. **Métriques performance** : Tracking temps réponse
16. **Quarantaine fichiers** : Statut temporaire avant scan OK

---

## 8. FICHIERS À MODIFIER

### Modifications critiques

1. `backend/core/models/content.py` : Ajouter index, soft delete, validation
2. `backend/core/api/content_views.py` : N+1, pagination, rate limiting, cache, sanitization
3. `backend/core/serializers/content.py` : Validation taille fichier, sanitization XSS
4. `backend/core/admin.py` : Admin amélioré, audit log

### Modifications élevées

5. `backend/core/tasks_security.py` : Fallback ClamAV plus strict
6. `backend/core/api/intents.py` : Sanitization message
7. Migrations : Créer migration pour index DB

### Tests à créer

8. `backend/core/tests/test_content_models.py` : Tests modèles
9. `backend/core/tests/test_content_api.py` : Tests API (extension de `tests_content.py`)
10. `backend/core/tests/test_content_tasks.py` : Tests Celery
11. `backend/core/tests/test_content_security.py` : Tests sécurité
12. `backend/core/tests/test_content_performance.py` : Tests performance

---

## 9. RISQUES RÉSIDUELS

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| **DoS via upload fichiers volumineux** | Moyenne | Élevé | Limite 50MB + rate limiting |
| **XSS via description/commentaire** | Moyenne | Élevé | Sanitization obligatoire |
| **Abus SAKA via mark-consumed** | Faible | Moyen | Rate limiting + seuil progression |
| **Perte données (pas de soft delete)** | Faible | Élevé | Soft delete + backup régulier |
| **Performance dégradée (N+1, pas d'index)** | Élevée | Moyen | Corrections critiques |
| **Fichiers malveillants (ClamAV indisponible)** | Faible | Élevé | Blocage upload si ClamAV down |

---

## 10. CONCLUSION

**Score global** : 55/100

**Points forts** :
- ✅ Séparation SAKA/EUR respectée
- ✅ Cache Redis pour liste publiés
- ✅ Tasks Celery bien structurées
- ✅ Tests API de base présents

**Points critiques** :
- 🔴 Performance (N+1, index manquants, pas de pagination)
- 🔴 Sécurité (pas de sanitization XSS, pas de limite taille fichier)
- 🔴 Robustesse (pas de versioning, pas de soft delete, pas d'audit log)

**Verdict** : Le domaine "Contenu" nécessite des corrections **critiques** avant mise en production à grande échelle. Les problèmes de performance et de sécurité doivent être corrigés en priorité.

---

**Prochaines étapes** :
1. Corriger les 5 problèmes critiques (index, N+1, pagination, taille fichier, XSS)
2. Ajouter les tests manquants (unitaires, API, Celery, sécurité)
3. Implémenter les améliorations élevées (rate limiting, cache, audit log)
4. Re-audit après corrections

