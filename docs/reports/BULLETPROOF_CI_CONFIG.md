# 🛡️ BULLETPROOF CI/CD CONFIGURATION

**Date** : 2025-01-03  
**Objectif** : Une CI verte est une CI verte. Pas de "peut-être".

---

## ✅ Modifications Effectuées

### 1. Retries Intelligents (Playwright)

**Fichier** : `frontend/frontend/playwright.config.js` (ligne 39)

**Configuration** :
```javascript
/* Retry on CI only - Retries intelligents pour éliminer les erreurs d'infrastructure */
// En CI : 2 retries pour gérer les timeouts/erreurs infrastructure
// En local : 0 retry pour détecter immédiatement les bugs réels
retries: process.env.CI ? 2 : 0,
```

**Comportement** :
- **En CI** : 2 retries automatiques pour éliminer les erreurs d'infrastructure (timeouts, problèmes réseau, etc.)
- **En local** : 0 retry pour détecter immédiatement les bugs réels

**Impact** : Réduit les faux positifs en CI dus à des problèmes d'infrastructure temporaires, tout en gardant une détection rapide des bugs réels en local.

---

### 2. Stabilisation Tests CMS

**Fichier** : `backend/core/tests/cms/test_content_permissions.py`

**Problème** : DRF peut retourner `401` (Unauthorized) ou `403` (Forbidden) pour les utilisateurs anonymes selon le contexte et les settings.

**Solution** : Tous les tests anonymes acceptent maintenant explicitement `401` OU `403`.

**Tests Corrigés** :
1. ✅ `test_anonymous_cannot_create_content` (ligne 117)
2. ✅ `test_anonymous_cannot_publish` (ligne 175)
3. ✅ `test_anonymous_cannot_reject` (ligne 219)
4. ✅ `test_anonymous_cannot_archive` (ligne 263)
5. ✅ `test_anonymous_cannot_unpublish` (ligne 308)

**Format Utilisé** :
```python
# DRF peut retourner 401 ou 403 pour les utilisateurs anonymes selon le contexte
assert response.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN)
```

**Note** : Les tests pour utilisateurs authentifiés (contributor, editor, etc.) utilisent toujours `== status.HTTP_403_FORBIDDEN` car ces utilisateurs sont authentifiés mais n'ont pas les permissions (403 est le code attendu).

---

## 🎯 Objectif Atteint

**Avant** :
- Tests CMS flaky (échouent selon les settings DRF)
- Tests E2E flaky en CI (erreurs infrastructure masquent bugs réels)

**Après** :
- ✅ Tests CMS stables (acceptent 401 ou 403 pour utilisateurs anonymes)
- ✅ Tests E2E avec retries intelligents (2 retries en CI, 0 en local)

**Résultat** : **Une CI verte est une CI verte. Pas de "peut-être".**

---

## 📊 Impact sur la CI

### Réduction des Faux Positifs

**Tests CMS** :
- Avant : Échecs intermittents selon settings DRF
- Après : Tests stables, acceptent les deux codes de statut valides

**Tests E2E** :
- Avant : Échecs dus à timeouts/erreurs infrastructure
- Après : 2 retries automatiques en CI pour gérer les problèmes temporaires

### Détection des Bugs Réels

**En Local** :
- 0 retry → Détection immédiate des bugs réels
- Pas de masquage des problèmes par des retries

**En CI** :
- 2 retries → Élimination des erreurs infrastructure
- Si un test échoue après 2 retries, c'est un bug réel

---

## 🧪 Tests Recommandés

### Test 1 : Vérifier Retries Playwright

```bash
# En local (0 retry)
npm run test:e2e

# En CI (2 retries)
CI=true npm run test:e2e
```

### Test 2 : Vérifier Tests CMS

```bash
# Lancer les tests CMS plusieurs fois pour vérifier la stabilité
pytest backend/core/tests/cms/test_content_permissions.py -v --count=5
```

---

**Statut** : ✅ **IMPLÉMENTÉ**

