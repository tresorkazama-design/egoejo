# Vérification Tests Unitaires Backend

**Date** : 2025-01-27  
**Objectif** : Vérifier l'existence et la couverture des tests de conformité backend

---

## ✅ Tests de Conformité Existants

### 1. **Test : Aucune Conversion SAKA ↔ EUR**

**Fichier** : `backend/tests/compliance/test_no_saka_eur_conversion.py`

**Statut** : ✅ **EXISTE ET COMPLET**

**Couverture** :
- ✅ Scan récursif de TOUS les fichiers Python dans `backend/`
- ✅ Détection de fonctions retournant un taux SAKA/EUR
- ✅ Détection de calculs de valeur monétaire du SAKA
- ✅ Détection d'affichages monétaires du SAKA
- ✅ Patterns interdits compilés depuis `test_patterns.json`
- ✅ Rapport détaillé (fichier, ligne, code snippet)

**Verdict** : ✅ **CONFORME** - Le test existe et scanne tous les modèles/services.

---

### 2. **Test : Séparation SAKA/EUR**

**Fichier** : `backend/tests/compliance/test_saka_eur_separation.py`

**Statut** : ✅ **EXISTE ET COMPLET**

**Couverture** :
- ✅ Aucune fonction de conversion SAKA ↔ EUR
- ✅ Aucun affichage monétaire du SAKA
- ✅ Aucune référence EUR dans services SAKA
- ✅ Aucune référence EUR dans modèles SAKA

**Verdict** : ✅ **CONFORME**

---

### 3. **Test : Étanchéité SAKA/EUR**

**Fichier** : `backend/tests/compliance/test_saka_eur_etancheite.py`

**Statut** : ✅ **EXISTE ET COMPLET**

**Couverture** :
- ✅ Aucune ForeignKey entre `UserWallet` et `SakaWallet`
- ✅ Aucune relation directe (ForeignKey, OneToOne)
- ✅ Aucune fonction liant UserWallet à SakaWallet

**Verdict** : ✅ **CONFORME**

---

### 4. **Test : Protection Admin**

**Fichier** : `backend/tests/compliance/test_admin_protection.py`

**Statut** : ✅ **EXISTE**

**Couverture** :
- ✅ Protection contre modification directe SAKA/EUR via Django Admin

**Verdict** : ✅ **CONFORME** (mais voir audit backend pour failles critiques)

---

## ❌ Tests de Permissions ViewSet - COUVERTURE INCOMPLÈTE

### Analyse des ViewSets Critiques

**Fichiers analysés** :
- `backend/core/api/saka_views.py` - 8 endpoints SAKA
- `backend/core/api/projects.py` - 3 endpoints Projets
- `backend/core/api/content_views.py` - 7 endpoints Contenus
- `backend/core/api/polls.py` - 4 endpoints Sondages
- `backend/core/api/fundraising.py` - 2 endpoints Financement
- `backend/finance/views.py` - 3 endpoints Wallet

**Total** : ~27 endpoints critiques

### Tests de Permissions Existants

**Fichier** : `backend/core/tests/cms/test_content_permissions.py`

**Statut** : ✅ **EXISTE** mais **COUVERTURE PARTIELLE**

**Couverture actuelle** :
- ✅ Tests pour `EducationalContentViewSet` :
  - ✅ Utilisateur anonyme → 403
  - ✅ Contributor → peut créer, ne peut pas publish/reject/archive
  - ✅ Editor → peut créer, publish, reject, archive
  - ✅ Admin → peut tout faire

**Verdict** : ✅ **CONFORME** pour Content, mais **MANQUE** pour autres ViewSets.

---

## 🔴 Tests de Permissions Manquants

### 1. **SAKA Views (`saka_views.py`)**

**Endpoints à tester** :
- ❌ `saka_silo_view` - `IsAuthenticated` → Test manquant
- ❌ `saka_compost_preview_view` - `IsAuthenticated` → Test manquant
- ❌ `saka_compost_trigger_view` - `IsAdminUser` → Test manquant
- ❌ `saka_stats_view` - `IsAdminUser` → Test manquant
- ❌ `saka_compost_logs_view` - `IsAdminUser` → Test manquant
- ❌ `saka_cycles_view` - `IsAuthenticated` → Test manquant
- ❌ `saka_silo_redistribute` - `IsAdminUser` → Test manquant
- ❌ `saka_redistribute_view` - `IsAdminUser` → Test manquant
- ❌ `saka_transactions_view` - `IsAuthenticated` → Test manquant

**Fichier à créer** : `backend/core/tests/api/test_saka_permissions.py`

**Priorité** : 🔴 **CRITIQUE**

---

### 2. **Projects Views (`projects.py`)**

**Endpoints à tester** :
- ❌ `ProjetListCreate` - `IsAuthenticatedOrReadOnly` → Test manquant
- ❌ `ProjetRetrieveUpdateDestroy` - `IsAuthenticatedOrReadOnly` → Test manquant
- ❌ `boost_project` - `IsAuthenticated` → Test manquant

**Fichier à créer** : `backend/core/tests/api/test_projects_permissions.py`

**Priorité** : 🔴 **CRITIQUE**

---

### 3. **Polls Views (`polls.py`)**

**Endpoints à tester** :
- ❌ `PollViewSet.list` - `IsAuthenticatedOrReadOnly` → Test manquant
- ❌ `PollViewSet.create` - `IsAuthenticated` → Test manquant
- ❌ `PollViewSet.vote` - `IsAuthenticated` → Test manquant
- ❌ `PollViewSet.close` - `IsAuthenticated` → Test manquant

**Fichier à créer** : `backend/core/tests/api/test_polls_permissions.py`

**Priorité** : 🟡 **MOYEN**

---

### 4. **Finance Views (`finance/views.py`)**

**Endpoints à tester** :
- ❌ `PocketTransferView` - `IsAuthenticated` → Test manquant
- ❌ `WalletPassAppleView` - `IsAuthenticated` → Test manquant
- ❌ `WalletPassGoogleView` - `IsAuthenticated` → Test manquant

**Fichier à créer** : `backend/finance/tests/test_views_permissions.py`

**Priorité** : 🟡 **MOYEN**

---

## 📊 Tableau Récapitulatif

| ViewSet/Endpoint | Permission | Test Existant | Fichier Test | Priorité |
|:-----------------|:-----------|:--------------|:-------------|:---------|
| `EducationalContentViewSet` | Variable | ✅ **OUI** | `test_content_permissions.py` | ✅ **OK** |
| `saka_views.*` | `IsAuthenticated` / `IsAdminUser` | ❌ **NON** | `test_saka_permissions.py` | 🔴 **CRITIQUE** |
| `projects.*` | `IsAuthenticatedOrReadOnly` | ❌ **NON** | `test_projects_permissions.py` | 🔴 **CRITIQUE** |
| `polls.*` | `IsAuthenticated` / `IsAuthenticatedOrReadOnly` | ❌ **NON** | `test_polls_permissions.py` | 🟡 **MOYEN** |
| `finance.*` | `IsAuthenticated` | ❌ **NON** | `test_views_permissions.py` | 🟡 **MOYEN** |

---

## 🎯 Recommandations

### Priorité 1 (Immédiat)

1. **Créer `test_saka_permissions.py`**
   ```python
   # backend/core/tests/api/test_saka_permissions.py
   - test_saka_silo_view_requires_authentication
   - test_saka_compost_trigger_requires_admin
   - test_saka_stats_requires_admin
   - test_saka_redistribute_requires_admin
   - test_saka_transactions_requires_authentication
   ```

2. **Créer `test_projects_permissions.py`**
   ```python
   # backend/core/tests/api/test_projects_permissions.py
   - test_projet_list_allows_read_only
   - test_projet_create_requires_authentication
   - test_projet_update_requires_authentication
   - test_boost_project_requires_authentication
   ```

### Priorité 2 (Sous 1 mois)

3. **Créer `test_polls_permissions.py`**
4. **Créer `test_views_permissions.py`** (finance)

---

## ✅ Template de Test de Permission

```python
"""
Tests de permissions pour [ViewSet/Endpoint].

Vérifie que les permissions sont correctement appliquées selon les rôles :
- Utilisateur anonyme → 401/403
- Utilisateur authentifié → 200/201
- Admin → 200/201
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

@pytest.fixture
def client():
    return APIClient()

@pytest.fixture
def anonymous_user():
    return None

@pytest.fixture
def authenticated_user(db):
    return User.objects.create_user(
        username='user',
        email='user@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user(db):
    user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='testpass123'
    )
    user.is_superuser = True
    user.is_staff = True
    user.save()
    return user

def test_endpoint_requires_authentication(client, anonymous_user):
    """Test que l'endpoint nécessite une authentification"""
    response = client.get('/api/endpoint/')
    assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

def test_endpoint_allows_authenticated_user(client, authenticated_user):
    """Test que l'endpoint autorise les utilisateurs authentifiés"""
    client.force_authenticate(user=authenticated_user)
    response = client.get('/api/endpoint/')
    assert response.status_code == status.HTTP_200_OK

def test_endpoint_requires_admin(client, authenticated_user, admin_user):
    """Test que l'endpoint nécessite les droits admin"""
    client.force_authenticate(user=authenticated_user)
    response = client.get('/api/admin-endpoint/')
    assert response.status_code == status.HTTP_403_FORBIDDEN
    
    client.force_authenticate(user=admin_user)
    response = client.get('/api/admin-endpoint/')
    assert response.status_code == status.HTTP_200_OK
```

---

**Document généré le** : 2025-01-27  
**Statut** : ✅ Analyse complète

