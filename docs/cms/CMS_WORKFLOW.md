# 📝 CMS Workflow - Documentation Technique EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0  
**Objectif** : Documentation complète du workflow CMS EGOEJO

---

## 🎯 Vue d'Ensemble

Le CMS EGOEJO permet la gestion complète des contenus éducatifs (podcasts, vidéos, PDF, articles, etc.) avec un workflow de validation strict et des permissions basées sur les rôles.

**Caractéristiques** :
- ✅ Workflow complet : draft → pending → published → archived
- ✅ Rôles : Contributor, Editor, Admin
- ✅ Permissions strictes sur endpoints
- ✅ XSS sanitization (bleach)
- ✅ Export JSON/CSV
- ✅ Pagination API
- ✅ Tests complets (unit, integration, contract, E2E)

---

## 📁 Architecture

### Backend

**Fichiers Principaux** :
- **`backend/core/models/content.py`** : Modèle `EducationalContent`
  - Statuts : draft, pending, published, rejected, archived
  - Champs : title, slug, type, status, description, author, etc.
  - Méthode `transition_to()` : Validation des transitions

- **`backend/core/api/content_views.py`** : `EducationalContentViewSet`
  - Endpoints : list, retrieve, create, publish, reject, archive, unpublish
  - Export : export_json, export_csv
  - Permissions : CanPublishContent, CanRejectContent, CanArchiveContent

- **`backend/core/permissions.py`** : Permissions basées sur les rôles
  - `CanPublishContent` : Editor/Admin uniquement
  - `CanRejectContent` : Editor/Admin uniquement
  - `CanArchiveContent` : Editor/Admin uniquement
  - `CanCreateContent` : Contributor/Editor/Admin

- **`backend/core/security/sanitization.py`** : Sanitization XSS
  - `sanitize_string()` : Échappement HTML (par défaut)
  - `sanitize_html()` : Sanitization HTML avec bleach (tags autorisés uniquement)

### Frontend

**Fichiers Principaux** :
- **`frontend/frontend/src/app/pages/Contenus.jsx`** : Page principale contenus
- **`frontend/frontend/e2e/contenus.spec.js`** : Tests E2E mock-only
- **`frontend/frontend/e2e/cms-workflow-fullstack.spec.js`** : Tests E2E full-stack

---

## 🔄 Workflow

### États (Status)

1. **draft** : Brouillon (créé par Contributor)
2. **pending** : En attente de validation (soumis par Contributor/Editor)
3. **published** : Publié (validé par Editor/Admin)
4. **rejected** : Rejeté (par Editor/Admin)
5. **archived** : Archivé (par Editor/Admin, terminal)

### Transitions Autorisées

| De | Vers | Rôle Requis | Notes |
|----|------|-------------|-------|
| draft | pending | Contributor, Editor | Soumission |
| pending | published | Admin | Publication |
| pending | rejected | Editor, Admin | Rejet |
| published | archived | Admin | Archivage |
| rejected | draft | Contributor | Retour en brouillon |
| rejected | pending | Contributor | Nouvelle soumission |

**Transitions Interdites** :
- draft → published (doit passer par pending)
- published → pending (doit être archivé d'abord)
- archived → * (terminal, aucune transition)

### Rôles et Permissions

| Action | Contributor | Editor | Admin |
|--------|-------------|--------|-------|
| Créer (draft) | ✅ | ✅ | ✅ |
| Soumettre (pending) | ✅ | ✅ | ✅ |
| Publier | ❌ | ✅ | ✅ |
| Rejeter | ❌ | ✅ | ✅ |
| Archiver | ❌ | ✅ | ✅ |
| Dépublication | ❌ | ✅ | ✅ |
| Export | ❌ | ✅ | ✅ |

---

## 🔐 Sécurité

### XSS Sanitization

**Implémentation** :
- **Backend** : `sanitize_string()` et `sanitize_html()` dans `core.security.sanitization`
- **Bleach** : Utilisé pour sanitization HTML (tags et attributs autorisés uniquement)
- **Tags autorisés** : `p`, `br`, `strong`, `em`, `u`, `a`, `ul`, `ol`, `li`, `blockquote`, `code`, `pre`
- **Attributs autorisés** : `a.href`, `a.title`

**Tests** : `backend/core/tests/cms/test_xss_sanitization.py`
- ✅ Script tags échappés
- ✅ Attributs onclick supprimés
- ✅ URLs javascript: supprimées
- ✅ Tags sécurisés préservés

### Permissions

- ✅ Vérification systématique des permissions avant chaque action
- ✅ Rejet des utilisateurs non autorisés (403 Forbidden)
- ✅ Audit log pour toutes les actions (create, publish, reject, archive)

---

## 📖 API Endpoints

### Liste des Contenus

**GET** `/api/contents/`

**Permissions** : AllowAny (public)

**Query params** :
- `status` : Filtre par statut (draft, pending, published, rejected, archived)
- `page` : Numéro de page (pagination)
- `page_size` : Nombre d'éléments par page (max: 100)

**Réponse** :
```json
{
  "count": 100,
  "next": "http://api/contents/?page=2",
  "previous": null,
  "results": [...]
}
```

### Créer un Contenu

**POST** `/api/contents/`

**Permissions** : IsAuthenticated + CanCreateContent

**Body** :
```json
{
  "title": "Mon Contenu",
  "slug": "mon-contenu",
  "type": "article",
  "description": "Description du contenu",
  "category": "ressources"
}
```

**Réponse** : 201 Created (status="pending" par défaut)

### Publier un Contenu

**POST** `/api/contents/{id}/publish/`

**Permissions** : IsAuthenticated + CanPublishContent (Editor/Admin)

**Réponse** : 200 OK (status="published")

**Note** : Vérification de compliance éditoriale avant publication (bloquant)

### Rejeter un Contenu

**POST** `/api/contents/{id}/reject/`

**Permissions** : IsAuthenticated + CanRejectContent (Editor/Admin)

**Body** :
```json
{
  "rejection_reason": "Raison du rejet"
}
```

**Réponse** : 200 OK (status="rejected")

### Archiver un Contenu

**POST** `/api/contents/{id}/archive/`

**Permissions** : IsAuthenticated + CanArchiveContent (Editor/Admin)

**Réponse** : 200 OK (status="archived")

### Export JSON

**GET** `/api/contents/export/json/`

**Permissions** : IsAuthenticated + IsStaff ou Editor

**Query params** :
- `status` : Filtre par statut (défaut: published)
- `limit` : Limite le nombre de résultats (max: 10000)

**Réponse** : 200 OK (Content-Type: application/json, Content-Disposition: attachment)

### Export CSV

**GET** `/api/contents/export/csv/`

**Permissions** : IsAuthenticated + IsStaff ou Editor

**Query params** :
- `status` : Filtre par statut (défaut: published)
- `limit` : Limite le nombre de résultats (max: 10000)

**Réponse** : 200 OK (Content-Type: text/csv, Content-Disposition: attachment)

---

## 🧪 Tests

### Tests Backend

**Fichiers** :
- **`backend/core/tests/cms/test_content_permissions.py`** : Tests permissions
- **`backend/core/tests/cms/test_content_workflow_transitions.py`** : Tests workflow
- **`backend/core/tests/cms/test_xss_sanitization.py`** : Tests XSS
- **`backend/core/tests/api/test_contract_cms_actions.py`** : Contract tests API

**Tests Inclus** :
- ✅ Permissions (anon, contributor, editor, admin)
- ✅ Transitions workflow (valides/invalides)
- ✅ XSS sanitization (script tags, onclick, javascript:)
- ✅ Contract tests (status codes, champs, erreurs)

**Exécution** :
```bash
# Tous les tests CMS
pytest backend/core/tests/cms/ -v
pytest backend/core/tests/api/test_contract_cms_actions.py -v

# Tests spécifiques
pytest backend/core/tests/cms/test_xss_sanitization.py -v
```

### Tests E2E

**Fichiers** :
- **`frontend/frontend/e2e/contenus.spec.js`** : Tests mock-only (UI)
- **`frontend/frontend/e2e/cms-workflow-fullstack.spec.js`** : Tests full-stack (workflow complet)

**Tests Inclus** :
- ✅ Workflow complet : create → publish → archive → export
- ✅ Pagination API
- ✅ Export JSON/CSV

**Exécution** :
```bash
# Tests full-stack
E2E_MODE=full-stack npx playwright test e2e/cms-workflow-fullstack.spec.js
```

---

## 📊 Pagination

### Configuration

La pagination est gérée automatiquement par DRF via `DEFAULT_PAGINATION_CLASS` dans `settings.py`.

**Paramètres** :
- `page` : Numéro de page (défaut: 1)
- `page_size` : Nombre d'éléments par page (défaut: 20, max: 100)

### Format de Réponse

**Avec pagination** :
```json
{
  "count": 100,
  "next": "http://api/contents/?page=2",
  "previous": null,
  "results": [...]
}
```

**Sans pagination** (rétrocompatibilité) :
```json
[...]
```

### Tests Pagination

**E2E** : `frontend/frontend/e2e/cms-workflow-fullstack.spec.js`
- ✅ Vérifie structure pagination DRF
- ✅ Vérifie que `page_size` limite les résultats

---

## 📤 Export

### Export JSON

**Endpoint** : `GET /api/contents/export/json/`

**Permissions** : Admin ou Editor

**Format** :
```json
[
  {
    "id": 1,
    "title": "Mon Contenu",
    "slug": "mon-contenu",
    "status": "published",
    ...
  },
  ...
]
```

### Export CSV

**Endpoint** : `GET /api/contents/export/csv/`

**Permissions** : Admin ou Editor

**Format** :
```csv
id,title,slug,type,status,category,description,author_id,author_username,...
1,Mon Contenu,mon-contenu,article,published,ressources,Description,1,user1,...
```

**Colonnes** :
- id, title, slug, type, status, category, description
- author_id, author_username, anonymous_display_name
- external_url, created_at, updated_at, published_at, published_by_id
- tags, project_id

### Tests Export

**Contract tests** : `backend/core/tests/api/test_contract_cms_actions.py`
- ✅ Export JSON requiert authentification (401/403)
- ✅ Export JSON requiert admin/editor (403 si contributor)
- ✅ Export JSON retourne 200 avec JSON valide
- ✅ Export CSV retourne 200 avec CSV valide

---

## 🚀 Utilisation

### Workflow Typique

1. **Contributor crée un contenu** :
   ```bash
   POST /api/contents/
   {
     "title": "Mon Contenu",
     "slug": "mon-contenu",
     "type": "article",
     "description": "Description"
   }
   ```
   → Status: `pending`

2. **Editor/Admin publie** :
   ```bash
   POST /api/contents/{id}/publish/
   ```
   → Status: `published`

3. **Contenu visible publiquement** :
   ```bash
   GET /api/contents/?status=published
   ```

4. **Archivage** :
   ```bash
   POST /api/contents/{id}/archive/
   ```
   → Status: `archived`

### Export des Données

**Export JSON** :
```bash
GET /api/contents/export/json/?status=published&limit=1000
```

**Export CSV** :
```bash
GET /api/contents/export/csv/?status=published&limit=1000
```

---

## 🐛 Dépannage

### Le contenu n'est pas publié

1. **Vérifier les permissions** : L'utilisateur doit être Editor ou Admin
2. **Vérifier le status** : Le contenu doit être en `pending`
3. **Vérifier la compliance** : Le contenu doit être conforme (vérification bloquante)

### Erreur 403 Forbidden

- L'utilisateur n'a pas la permission requise
- Vérifier le rôle (Contributor ne peut pas publier/rejeter/archiver)

### Erreur XSS détectée

- Les balises `<script>` et attributs `onclick` sont automatiquement échappés
- Utiliser `sanitize_html()` si HTML autorisé (tags sécurisés uniquement)

---

## 📚 Références

- **Code Source** :
  - `backend/core/models/content.py` : Modèle EducationalContent
  - `backend/core/api/content_views.py` : ViewSet et endpoints
  - `backend/core/permissions.py` : Permissions basées sur les rôles
  - `backend/core/security/sanitization.py` : Sanitization XSS

- **Tests** :
  - `backend/core/tests/cms/` : Tests CMS
  - `backend/core/tests/api/test_contract_cms_actions.py` : Contract tests
  - `frontend/frontend/e2e/cms-workflow-fullstack.spec.js` : E2E full-stack

- **Documentation** :
  - Django REST Framework : https://www.django-rest-framework.org/
  - Bleach : https://bleach.readthedocs.io/

---

**Statut** : ✅ **OPÉRATIONNEL**  
**Dernière Mise à Jour** : 2025-01-27

