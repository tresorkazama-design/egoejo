# AUDIT CMS EGOEJO - SYSTÈME DE GESTION DE CONTENU

**Date** : 2025-01-XX  
**Auditeur** : Senior Technical Auditor  
**Scope** : CMS au sens large (Admin Django, Endpoints API, Workflow, Rôles, Logs, Versioning, Export)

---

## 1. ÉTAT ACTUEL DU CMS

### 1.1 Workflow de Publication

**Statuts définis** (`backend/core/models/content.py:24-29`) :
- ✅ `draft` : Brouillon
- ✅ `pending` : En attente de validation
- ✅ `published` : Publié
- ✅ `rejected` : Rejeté
- ❌ **MANQUE** : `archived` (pas de statut archivé)

**Transitions actuelles** :
- `draft` → `pending` : Via création API (automatique si `status` non fourni)
- `pending` → `published` : Via endpoint `/api/contents/{id}/publish/` (POST)
- `pending` → `rejected` : ❌ **MANQUE** (pas d'endpoint)
- `published` → `archived` : ❌ **MANQUE** (pas de statut, pas d'endpoint)
- `published` → `draft` : ❌ **MANQUE** (pas d'endpoint unpublish)

**Fichiers concernés** :
- `backend/core/models/content.py:24-29` : Définition des statuts
- `backend/core/api/content_views.py:248-298` : Endpoint `publish/` uniquement

### 1.2 Rôles et Permissions

**Rôles existants** :

| Rôle | Groupe Django | Permission | Usage CMS |
|------|---------------|------------|-----------|
| **Admin** | `is_superuser=True` | Tous droits Django Admin | ✅ Accès admin Django |
| **Founder** | `Founders_V1_Protection` | `IsFounderOrReadOnly` | ❌ Non utilisé pour contenu |
| **Staff** | `is_staff=True` | Accès admin Django | ⚠️ Accès admin mais pas de permissions spécifiques |
| **Editor** | ❌ **MANQUE** | ❌ **MANQUE** | ❌ Non défini |
| **Contributor** | ❌ **MANQUE** | ❌ **MANQUE** | ❌ Non défini |

**Permissions actuelles** (`backend/core/api/content_views.py:33`) :
- ✅ `permissions.AllowAny` : **PUBLIC** (n'importe qui peut créer/modifier/publier)
- ❌ **CRITIQUE** : Pas de restriction sur `publish/` (n'importe qui peut publier)
- ❌ **CRITIQUE** : Pas de restriction sur `create/` (n'importe qui peut créer)
- ❌ **CRITIQUE** : Pas de restriction sur modification (pas de `UpdateModelMixin` mais pas de protection)

**Fichiers concernés** :
- `backend/core/api/content_views.py:33` : `permission_classes = [permissions.AllowAny]`
- `backend/core/permissions.py:28-44` : `IsFounderOrReadOnly` (non utilisé pour contenu)
- `backend/config/settings.py:479` : `FOUNDER_GROUP_NAME` (non utilisé pour contenu)

### 1.3 Django Admin

**Configuration actuelle** (`backend/core/admin.py:61-66`) :

```python
@admin.register(EducationalContent)
class EducationalContentAdmin(admin.ModelAdmin):
    list_display = ("title", "type", "status", "created_at")
    list_filter = ("type", "status", "created_at")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
```

**Problèmes identifiés** :

- ❌ **MANQUE** : Pas d'actions personnalisées (`actions = []`)
  - Pas d'action "Publier en masse"
  - Pas d'action "Rejeter en masse"
  - Pas d'action "Archiver en masse"
  - Pas d'action "Générer audio en masse"

- ❌ **MANQUE** : Pas de `readonly_fields` :
  - `created_at`, `updated_at` modifiables
  - `embedding_source_hash`, `audio_source_hash` modifiables
  - `author` modifiable (devrait être readonly après création)

- ❌ **MANQUE** : Pas de `date_hierarchy` (navigation temporelle)

- ❌ **MANQUE** : Pas de `raw_id_fields` (pour `author`, `project` si beaucoup d'utilisateurs/projets)

- ❌ **MANQUE** : Pas de `autocomplete_fields` (recherche rapide)

- ❌ **MANQUE** : Pas de `get_queryset()` personnalisé (filtrage par rôle)

- ❌ **MANQUE** : Pas de `has_add_permission()`, `has_change_permission()`, `has_delete_permission()` (contrôle d'accès)

- ❌ **MANQUE** : Pas de `save_model()` (pas de log d'audit lors modification admin)

**Fichiers concernés** :
- `backend/core/admin.py:61-66`

### 1.4 Endpoints API CMS

**Endpoints existants** (`backend/core/api/content_views.py`) :

| Endpoint | Méthode | Permission | Action | Workflow |
|----------|---------|------------|--------|----------|
| `/api/contents/` | GET | `AllowAny` | Liste | ✅ OK |
| `/api/contents/{id}/` | GET | `AllowAny` | Détail | ✅ OK |
| `/api/contents/` | POST | `AllowAny` | Créer | ⚠️ Public (devrait être authentifié) |
| `/api/contents/{id}/publish/` | POST | `AllowAny` | Publier | 🔴 **CRITIQUE** : Public (devrait être staff/admin) |
| `/api/contents/{id}/mark-consumed/` | POST | `IsAuthenticated` (vérifié manuellement) | Marquer consommé | ✅ OK |

**Endpoints manquants** :

- ❌ **MANQUE** : `PUT /api/contents/{id}/` (modification)
- ❌ **MANQUE** : `PATCH /api/contents/{id}/` (modification partielle)
- ❌ **MANQUE** : `DELETE /api/contents/{id}/` (suppression)
- ❌ **MANQUE** : `POST /api/contents/{id}/reject/` (rejeter)
- ❌ **MANQUE** : `POST /api/contents/{id}/unpublish/` (dépublication)
- ❌ **MANQUE** : `POST /api/contents/{id}/archive/` (archivage)
- ❌ **MANQUE** : `GET /api/contents/drafts/` (liste brouillons utilisateur)
- ❌ **MANQUE** : `GET /api/contents/pending/` (liste en attente pour reviewer)

**Fichiers concernés** :
- `backend/core/api/content_views.py:11-16` : `CreateModelMixin` uniquement (pas `UpdateModelMixin`, pas `DestroyModelMixin`)

### 1.5 Logs d'Audit

**Modèle AuditLog** (`backend/core/models/audit.py:11-29`) :
- ✅ Existe : `actor`, `action`, `target_type`, `target_id`, `metadata`, `created_at`
- ✅ Utilisé dans d'autres endpoints (`chat.py`, `polls.py`, `moderation.py`)

**Utilisation dans CMS** :

- ❌ **MANQUE** : Pas de `log_action()` dans `perform_create()` (`content_views.py:106-170`)
- ❌ **MANQUE** : Pas de `log_action()` dans `publish()` (`content_views.py:248-298`)
- ❌ **MANQUE** : Pas de `log_action()` dans admin (`admin.py:61-66`, pas de `save_model()`)

**Fonction disponible** (`backend/core/api/common.py:37-53`) :
```python
def log_action(actor, action: str, target_type: str, target_id: Optional[Any] = None, metadata: Optional[Dict[str, Any]] = None) -> None
```

**Actions à logger** :
- `content_create` : Création d'un contenu
- `content_update` : Modification d'un contenu
- `content_publish` : Publication
- `content_reject` : Rejet
- `content_archive` : Archivage
- `content_delete` : Suppression
- `content_status_change` : Changement de statut

**Fichiers concernés** :
- `backend/core/api/content_views.py` : Pas de `log_action()`
- `backend/core/admin.py:61-66` : Pas de `save_model()` avec `log_action()`

### 1.6 Versioning

**État actuel** :

- ❌ **MANQUE** : Aucun système de versioning
- ❌ **MANQUE** : Pas de `django-reversion` installé
- ❌ **MANQUE** : Pas de modèle `ContentVersion` ou équivalent
- ❌ **MANQUE** : Pas d'historique des modifications
- ❌ **MANQUE** : Pas de rollback possible

**Champs de tracking** :
- ✅ `created_at` : Date de création
- ✅ `updated_at` : Date de dernière modification
- ❌ **MANQUE** : `published_at` (date de publication)
- ❌ **MANQUE** : `archived_at` (date d'archivage)
- ❌ **MANQUE** : `modified_by` (qui a modifié)
- ❌ **MANQUE** : `published_by` (qui a publié)
- ❌ **MANQUE** : `rejected_by` (qui a rejeté)

**Fichiers concernés** :
- `backend/core/models/content.py:122-123` : Seulement `created_at`, `updated_at`

### 1.7 Export

**État actuel** :

- ❌ **MANQUE** : Pas d'export JSON dans admin
- ❌ **MANQUE** : Pas d'export CSV dans admin
- ❌ **MANQUE** : Pas d'endpoint API `/api/contents/export/`
- ❌ **MANQUE** : Pas de format compatible tiers (WordPress, Ghost, etc.)

**Exemple existant** (`backend/core/api/intents.py:148-182`) :
- ✅ Export CSV pour `Intent` (fonction `export_intents()`)
- ✅ Format CSV avec colonnes : `id`, `nom`, `email`, `profil`, `message`, `created_at`, `ip`, `user_agent`, `document_url`
- ✅ Limite 10000 enregistrements
- ✅ Filtres par date, profil, recherche

**Fichiers concernés** :
- `backend/core/admin.py:61-66` : Pas d'actions d'export
- `backend/core/api/content_views.py` : Pas d'endpoint export

---

## 2. ANALYSE DÉTAILLÉE

### 2.1 Workflow Actuel vs. Workflow Cible

**Workflow actuel** :
```
[draft] → [pending] → [published]
                ↓
           [rejected]
```

**Problèmes** :
- Pas de transition `published` → `archived`
- Pas de transition `published` → `draft` (unpublish)
- Pas de transition `rejected` → `pending` (réouverture)
- Pas de workflow de review (assignation à un reviewer)

**Workflow cible recommandé** :
```
[draft] → [pending] → [published] → [archived]
                ↓           ↓
           [rejected]   [draft] (unpublish)
                ↓
           [pending] (réouverture)
```

### 2.2 Permissions et Rôles Recommandés

**Rôles CMS V1** :

| Rôle | Permissions | Groupe Django | Usage |
|------|-------------|---------------|-------|
| **Admin** | Tous droits (CRUD + publish + reject + archive + delete) | `is_superuser=True` | Gestion complète |
| **Editor** | CRUD + publish + reject (pas delete, pas archive) | `Content_Editors` | Édition et publication |
| **Contributor** | Create + Update own (draft/pending uniquement) | `Content_Contributors` | Création et modification de ses contenus |
| **Reviewer** | Read + Update status (pending → published/rejected) | `Content_Reviewers` | Validation des contenus |

**Permissions DRF recommandées** :

```python
# Permissions personnalisées
class IsContentEditor(permissions.BasePermission):
    """Editor peut créer, modifier, publier, rejeter"""
    
class IsContentContributor(permissions.BasePermission):
    """Contributor peut créer et modifier ses propres contenus (draft/pending)"""
    
class IsContentReviewer(permissions.BasePermission):
    """Reviewer peut changer le statut (pending → published/rejected)"""
```

### 2.3 Logs d'Audit Recommandés

**Actions à logger** :

| Action | Trigger | Metadata |
|--------|---------|----------|
| `content_create` | `perform_create()` | `{"title": "...", "type": "...", "status": "pending"}` |
| `content_update` | `perform_update()` | `{"fields_changed": ["title", "description"], "old_status": "pending", "new_status": "pending"}` |
| `content_publish` | `publish()` | `{"published_by": user.id, "published_at": "..."}` |
| `content_reject` | `reject()` | `{"rejected_by": user.id, "rejection_reason": "..."}` |
| `content_archive` | `archive()` | `{"archived_by": user.id, "archived_at": "..."}` |
| `content_delete` | `perform_destroy()` | `{"deleted_by": user.id}` |
| `content_status_change` | Changement `status` | `{"old_status": "...", "new_status": "...", "changed_by": user.id}` |

**Implémentation recommandée** :

```python
# Dans perform_create()
log_action(
    request.user if request.user.is_authenticated else None,
    "content_create",
    "educational_content",
    content.id,
    {"title": content.title, "type": content.type, "status": content.status}
)

# Dans publish()
log_action(
    request.user,
    "content_publish",
    "educational_content",
    content.id,
    {"published_by": request.user.id, "old_status": old_status, "new_status": "published"}
)
```

### 2.4 Versioning Minimal Recommandé

**Option 1 : Champs de tracking simples** (recommandé pour V1) :

```python
# Ajouter dans EducationalContent
published_at = models.DateTimeField(null=True, blank=True)
archived_at = models.DateTimeField(null=True, blank=True)
modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="modified_contents")
published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="published_contents")
rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="rejected_contents")
```

**Option 2 : django-reversion** (pour V2 si besoin d'historique complet) :

```python
# Installation : pip install django-reversion
# Configuration dans admin.py
import reversion

@reversion.register()
class EducationalContentAdmin(admin.ModelAdmin):
    # ...
```

**Recommandation V1** : Option 1 (champs de tracking) + `AuditLog` pour historique complet.

### 2.5 Export Recommandé

**Format JSON** (API) :

```python
@action(detail=False, methods=["get"], url_path="export")
def export(self, request):
    """Export JSON de tous les contenus (admin uniquement)"""
    # Filtres : ?status=published&format=json&limit=1000
```

**Format CSV** (Admin + API) :

```python
# Dans admin.py
@admin.action(description="Exporter les contenus sélectionnés en CSV")
def export_selected_csv(modeladmin, request, queryset):
    # Générer CSV avec colonnes : id, title, type, status, author, created_at, published_at
```

**Format compatible tiers** :

- **WordPress** : Format WXR (XML) pour import WordPress
- **Ghost** : Format JSON Ghost
- **Markdown** : Export Markdown pour migration vers Jekyll/Hugo

---

## 3. TABLEAU DE PROBLÈMES

| Problème | Gravité | Fichier(s) | Correctif proposé | Test à ajouter |
|----------|---------|------------|-------------------|---------------|
| **Permissions AllowAny sur publish/** | 🔴 CRITIQUE | `backend/core/api/content_views.py:33, 248` | Ajouter `IsStaffUser` ou `IsContentEditor` | Test permission publish |
| **Pas d'endpoint reject/** | 🔴 CRITIQUE | `backend/core/api/content_views.py` | Ajouter `@action reject()` | Test reject endpoint |
| **Pas d'endpoint archive/** | 🔴 CRITIQUE | `backend/core/api/content_views.py` | Ajouter `@action archive()` | Test archive endpoint |
| **Pas d'endpoint update/** | 🔴 CRITIQUE | `backend/core/api/content_views.py:11-16` | Ajouter `UpdateModelMixin` | Test update endpoint |
| **Pas de log_action dans CMS** | 🔴 CRITIQUE | `backend/core/api/content_views.py:106, 248` | Ajouter `log_action()` dans `perform_create()`, `publish()` | Test audit log création |
| **Pas de statut archived** | 🟡 ÉLEVÉ | `backend/core/models/content.py:24-29` | Ajouter `("archived", "Archivé")` dans `STATUS_CHOICES` | Test statut archived |
| **Pas de champs tracking (published_by, etc.)** | 🟡 ÉLEVÉ | `backend/core/models/content.py` | Ajouter `published_at`, `published_by`, `modified_by`, etc. | Test tracking champs |
| **Admin basique sans actions** | 🟡 ÉLEVÉ | `backend/core/admin.py:61-66` | Ajouter actions : publish, reject, archive, export | Test actions admin |
| **Pas de permissions par rôle** | 🟡 ÉLEVÉ | `backend/core/api/content_views.py`, `backend/core/permissions.py` | Créer `IsContentEditor`, `IsContentContributor`, `IsContentReviewer` | Test permissions rôles |
| **Pas de versioning** | 🟡 ÉLEVÉ | `backend/core/models/content.py` | Ajouter champs tracking OU django-reversion | Test versioning |
| **Pas d'export JSON/CSV** | 🟡 ÉLEVÉ | `backend/core/admin.py`, `backend/core/api/content_views.py` | Ajouter action export admin + endpoint export API | Test export JSON/CSV |
| **Pas de readonly_fields admin** | 🟠 MOYEN | `backend/core/admin.py:61-66` | Ajouter `readonly_fields = ("created_at", "updated_at", "author")` | Test readonly admin |
| **Pas de date_hierarchy admin** | 🟠 MOYEN | `backend/core/admin.py:61-66` | Ajouter `date_hierarchy = "created_at"` | Test navigation temporelle |
| **Pas de get_queryset admin** | 🟠 MOYEN | `backend/core/admin.py:61-66` | Filtrer par rôle (contributor voit seulement ses contenus) | Test queryset admin |
| **Pas d'endpoint unpublish/** | 🟠 MOYEN | `backend/core/api/content_views.py` | Ajouter `@action unpublish()` | Test unpublish endpoint |
| **Pas de workflow review** | 🟠 MOYEN | `backend/core/models/content.py` | Ajouter champ `reviewer` (ForeignKey User) | Test assignation reviewer |
| **Pas de groupes Django Editor/Contributor** | 🟠 MOYEN | `backend/core/apps.py` ou migration | Créer groupes `Content_Editors`, `Content_Contributors`, `Content_Reviewers` | Test groupes Django |
| **Pas de save_model admin** | 🟢 FAIBLE | `backend/core/admin.py:61-66` | Ajouter `save_model()` avec `log_action()` | Test audit log admin |
| **Pas de raw_id_fields admin** | 🟢 FAIBLE | `backend/core/admin.py:61-66` | Ajouter `raw_id_fields = ("author", "project")` | Test performance admin |
| **Pas de format export tiers** | 🟢 FAIBLE | `backend/core/api/content_views.py` | Ajouter export WordPress/Ghost/Markdown | Test export tiers |

---

## 4. RECOMMANDATIONS CMS V1 ROBUSTE ET SIMPLE

### 4.1 Workflow Minimal V1

**Statuts** :
- `draft` : Brouillon (auteur peut modifier)
- `pending` : En attente de validation (auteur ne peut plus modifier)
- `published` : Publié (visible publiquement)
- `rejected` : Rejeté (avec raison optionnelle)
- `archived` : Archivé (masqué mais conservé)

**Transitions** :
- `draft` → `pending` : Soumission par auteur
- `pending` → `published` : Validation par editor/reviewer
- `pending` → `rejected` : Rejet par editor/reviewer
- `published` → `archived` : Archivage par admin/editor
- `published` → `draft` : Dépublication par admin/editor
- `rejected` → `pending` : Réouverture par editor/admin

### 4.2 Rôles Minimal V1

**3 rôles** (simplifié) :

1. **Admin** (`is_superuser=True`) :
   - Tous droits (CRUD + publish + reject + archive + delete)
   - Accès admin Django complet

2. **Editor** (groupe `Content_Editors`) :
   - CRUD sur tous les contenus
   - Publier/rejeter/archiver
   - Pas de suppression définitive

3. **Contributor** (groupe `Content_Contributors`) :
   - Créer des contenus (status=draft)
   - Modifier ses propres contenus (si status=draft ou pending)
   - Soumettre pour validation (draft → pending)
   - Pas de publication/rejet

**Permissions DRF** :

```python
# backend/core/permissions.py

class IsContentEditor(permissions.BasePermission):
    """Editor peut gérer tous les contenus"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_staff or
            request.user.groups.filter(name='Content_Editors').exists()
        )

class IsContentContributor(permissions.BasePermission):
    """Contributor peut créer et modifier ses propres contenus"""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':  # Create
            return request.user.is_authenticated
        if request.method in ['PUT', 'PATCH']:  # Update
            return request.user.is_authenticated
        return False
    
    def has_object_permission(self, request, view, obj):
        # Contributor peut modifier seulement ses propres contenus en draft/pending
        if obj.author != request.user:
            return False
        if obj.status not in ['draft', 'pending']:
            return False
        return True
```

### 4.3 Logs d'Audit Minimal V1

**Implémentation** :

```python
# Dans perform_create()
from core.api.common import log_action

log_action(
    request.user if request.user.is_authenticated else None,
    "content_create",
    "educational_content",
    content.id,
    {
        "title": content.title,
        "type": content.type,
        "status": content.status,
        "author_id": content.author.id if content.author else None
    }
)

# Dans publish()
old_status = content.status
content.status = "published"
content.published_at = timezone.now()
content.published_by = request.user
content.save()

log_action(
    request.user,
    "content_publish",
    "educational_content",
    content.id,
    {
        "old_status": old_status,
        "new_status": "published",
        "published_by": request.user.id
    }
)
```

### 4.4 Versioning Minimal V1

**Champs à ajouter** :

```python
# Migration à créer
class Migration(migrations.Migration):
    operations = [
        migrations.AddField(
            model_name='educationalcontent',
            name='published_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='educationalcontent',
            name='archived_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='educationalcontent',
            name='modified_by',
            field=models.ForeignKey(
                User, on_delete=models.SET_NULL, null=True,
                related_name="modified_contents"
            ),
        ),
        migrations.AddField(
            model_name='educationalcontent',
            name='published_by',
            field=models.ForeignKey(
                User, on_delete=models.SET_NULL, null=True,
                related_name="published_contents"
            ),
        ),
        migrations.AddField(
            model_name='educationalcontent',
            name='rejected_by',
            field=models.ForeignKey(
                User, on_delete=models.SET_NULL, null=True,
                related_name="rejected_contents"
            ),
        ),
        migrations.AddField(
            model_name='educationalcontent',
            name='rejection_reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
```

**Historique complet** : Via `AuditLog` (déjà existant, à utiliser).

### 4.5 Export Minimal V1

**Format JSON** (API) :

```python
@action(detail=False, methods=["get"], url_path="export")
@permission_classes([permissions.IsStaffUser])
def export(self, request):
    """Export JSON de tous les contenus (staff uniquement)"""
    status_filter = request.query_params.get("status")
    format_type = request.query_params.get("format", "json")
    limit = int(request.query_params.get("limit", 1000))
    
    queryset = EducationalContent.objects.all()
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    queryset = queryset[:limit]
    
    if format_type == "csv":
        # Générer CSV
        return csv_response(queryset)
    else:
        # Générer JSON
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
```

**Format CSV** (Admin) :

```python
@admin.action(description="Exporter les contenus sélectionnés en CSV")
def export_selected_csv(modeladmin, request, queryset):
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="contenus.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['id', 'title', 'type', 'status', 'author', 'created_at', 'published_at'])
    
    for content in queryset:
        writer.writerow([
            content.id,
            content.title,
            content.type,
            content.status,
            content.author.username if content.author else '',
            content.created_at.isoformat() if content.created_at else '',
            content.published_at.isoformat() if content.published_at else '',
        ])
    
    return response
```

---

## 5. PLAN D'IMPLÉMENTATION CMS V1

### Phase 1 : Sécurité (Critique)

1. **Ajouter permissions** :
   - Créer `IsContentEditor`, `IsContentContributor` dans `backend/core/permissions.py`
   - Modifier `EducationalContentViewSet.permission_classes`
   - Restreindre `publish/` à `IsContentEditor` ou `IsStaffUser`

2. **Ajouter endpoints manquants** :
   - `reject/` : Rejeter un contenu
   - `archive/` : Archiver un contenu
   - `unpublish/` : Dépublication
   - `UpdateModelMixin` : Modification

3. **Ajouter statut `archived`** :
   - Migration pour ajouter `("archived", "Archivé")` dans `STATUS_CHOICES`

### Phase 2 : Tracking et Logs (Élevé)

4. **Ajouter champs de tracking** :
   - Migration pour `published_at`, `archived_at`, `modified_by`, `published_by`, `rejected_by`, `rejection_reason`

5. **Implémenter logs d'audit** :
   - Ajouter `log_action()` dans `perform_create()`, `publish()`, `reject()`, `archive()`, `perform_update()`
   - Ajouter `save_model()` dans admin avec `log_action()`

### Phase 3 : Admin Amélioré (Moyen)

6. **Améliorer admin Django** :
   - Ajouter actions : `publish_selected`, `reject_selected`, `archive_selected`, `export_selected_csv`
   - Ajouter `readonly_fields`, `date_hierarchy`, `raw_id_fields`
   - Ajouter `get_queryset()` pour filtrer par rôle

7. **Créer groupes Django** :
   - Migration pour créer `Content_Editors`, `Content_Contributors`, `Content_Reviewers`

### Phase 4 : Export (Moyen)

8. **Implémenter export** :
   - Endpoint API `/api/contents/export/` (JSON/CSV)
   - Action admin `export_selected_csv`

---

## 6. FICHIERS À CRÉER/MODIFIER

### Fichiers à modifier

1. `backend/core/models/content.py` :
   - Ajouter `archived` dans `STATUS_CHOICES`
   - Ajouter champs : `published_at`, `archived_at`, `modified_by`, `published_by`, `rejected_by`, `rejection_reason`

2. `backend/core/api/content_views.py` :
   - Modifier `permission_classes`
   - Ajouter `UpdateModelMixin`, `DestroyModelMixin`
   - Ajouter actions : `reject()`, `archive()`, `unpublish()`, `export()`
   - Ajouter `log_action()` dans toutes les méthodes

3. `backend/core/admin.py` :
   - Améliorer `EducationalContentAdmin` (actions, readonly_fields, date_hierarchy, etc.)
   - Ajouter `save_model()` avec `log_action()`

4. `backend/core/permissions.py` :
   - Ajouter `IsContentEditor`, `IsContentContributor`, `IsContentReviewer`

### Fichiers à créer

5. `backend/core/migrations/XXXX_add_cms_tracking_fields.py` :
   - Migration pour champs de tracking

6. `backend/core/migrations/XXXX_add_cms_groups.py` :
   - Migration pour créer groupes Django

7. `backend/core/tests/cms/test_content_workflow.py` :
   - Tests workflow (draft → pending → published → archived)

8. `backend/core/tests/cms/test_content_permissions.py` :
   - Tests permissions par rôle

9. `backend/core/tests/cms/test_content_audit.py` :
   - Tests logs d'audit

---

## 7. RECOMMANDATIONS FINALES

### CMS V1 Minimal et Robuste

**Principe** : "Simple mais complet"

1. **Workflow** : 5 statuts (draft, pending, published, rejected, archived) avec transitions claires
2. **Rôles** : 3 rôles (Admin, Editor, Contributor) avec permissions granulaires
3. **Logs** : `AuditLog` pour toutes les actions critiques (create, update, publish, reject, archive, delete)
4. **Versioning** : Champs de tracking (`published_by`, `modified_by`, etc.) + `AuditLog` pour historique
5. **Export** : JSON (API) + CSV (Admin) pour compatibilité tiers

**Complexité** : Moyenne (pas de django-reversion, pas de workflow engine complexe)

**Maintenabilité** : Élevée (code simple, tests complets, documentation claire)

**Évolutivité** : Prête pour V2 (django-reversion, workflow engine, UI admin custom)

---

## 8. CONCLUSION

**Score CMS actuel** : 35/100

**Points forts** :
- ✅ Modèle `EducationalContent` bien structuré
- ✅ Modèle `AuditLog` existe et fonctionne
- ✅ Endpoint `publish/` fonctionne (mais permissions trop permissives)

**Points critiques** :
- 🔴 Permissions trop permissives (`AllowAny` sur `publish/`)
- 🔴 Pas d'endpoints reject/archive/unpublish
- 🔴 Pas de logs d'audit dans CMS
- 🔴 Pas de versioning (même minimal)
- 🔴 Pas d'export

**Verdict** : Le CMS actuel est **trop permissif** et **incomplet**. Il nécessite des corrections **critiques** avant utilisation en production.

**Recommandation** : Implémenter le plan CMS V1 (4 phases) pour un CMS robuste et simple, prêt pour production.

---

**Prochaines étapes** :
1. Phase 1 : Sécurité (permissions + endpoints manquants)
2. Phase 2 : Tracking et logs
3. Phase 3 : Admin amélioré
4. Phase 4 : Export

