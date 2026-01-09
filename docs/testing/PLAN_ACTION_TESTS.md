# 🎯 Plan d'Action - Stratégie Tests EGOEJO

**Date** : 2025-01-XX  
**Statut** : Plan validé, prêt pour implémentation

---

## ✅ ÉTAPES COMPLÉTÉES

### ÉTAPE 0 - Inventaire ✅
- ✅ Inventaire complet backend (tests, marqueurs, structure)
- ✅ Inventaire complet frontend (unit, E2E, lint)
- ✅ Inventaire CI workflows (15 workflows)
- ✅ Inventaire scripts audit (3 scripts)
- 📄 **Document** : `docs/testing/INVENTAIRE_TESTS_EXISTANTS.md`

### ÉTAPE 1 - Matrice de Couverture ✅
- ✅ Matrice complète (10 domaines x 6 niveaux)
- ✅ Identification gaps P0/P1/P2
- 📄 **Document** : `docs/testing/MATRICE_COUVERTURE_TESTS.md`

---

## 🚀 PROCHAINES ÉTAPES - PLAN D'IMPLÉMENTATION

### ÉTAPE 2 - Tests P0 BLOQUANTS

#### A) Contract Tests API

**Objectif** : Vérifier que les endpoints API respectent leur contrat (status codes, champs obligatoires, erreurs)

**Fichiers à créer** :
- `backend/core/tests/api/test_contract_health.py` : Contract `/api/health`
- `backend/core/tests/api/test_contract_saka.py` : Contract endpoints SAKA (grant/transactions/vote)
- `backend/core/tests/api/test_contract_cms.py` : Contract endpoints CMS (publish/reject/archive)
- `backend/core/tests/api/test_contract_projects.py` : Contract endpoints projets (create/publish/list)
- `backend/finance/tests/test_contract_webhooks_stripe.py` : Contract webhooks Stripe

**Approche** :
- Utiliser `pytest` avec `pytest-httpx` ou `requests` pour appels HTTP
- Vérifier status codes (200, 400, 401, 403, 404, 500)
- Vérifier champs obligatoires (présence, type, format)
- Vérifier messages d'erreur (structure, contenu)
- Pas de schéma OpenAPI formel (trop lourd), mais validation minimale

**Exemple structure** :
```python
# backend/core/tests/api/test_contract_health.py
@pytest.mark.django_db
def test_health_endpoint_returns_200(client):
    response = client.get('/api/health/')
    assert response.status_code == 200
    assert 'status' in response.json()
    assert response.json()['status'] == 'ok'

@pytest.mark.django_db
def test_health_endpoint_has_required_fields(client):
    response = client.get('/api/health/')
    data = response.json()
    assert 'status' in data
    assert 'timestamp' in data
```

**Marqueurs** : `@pytest.mark.critical` (nouveau marqueur à définir dans `pytest.ini`)

**Durée estimée** : ~2-3 min

---

#### B) Permissions Tests Complets

**Objectif** : Garantir que tous les endpoints sensibles vérifient les permissions (anonyme vs user vs admin)

**Fichiers à créer/modifier** :
- `backend/core/tests/api/test_cms_permissions_complete.py` : Permissions CMS complètes
- `backend/finance/tests/test_finance_permissions_complete.py` : Permissions finance complètes
- Modifier `backend/core/tests/api/test_saka_permissions.py` : Compléter si manquant

**Approche** :
- Tester anonyme (401 OU 403 selon DRF)
- Tester user normal (403 si admin requis)
- Tester admin (200)
- Utiliser `APIClient` Django REST Framework

**Exemple structure** :
```python
# backend/core/tests/api/test_cms_permissions_complete.py
@pytest.mark.django_db
@pytest.mark.critical
def test_cms_publish_requires_auth(client):
    response = client.post('/api/cms/content/1/publish/')
    assert response.status_code in [401, 403]

@pytest.mark.django_db
@pytest.mark.critical
def test_cms_publish_requires_admin(client, admin_user):
    client.force_authenticate(user=admin_user)
    response = client.post('/api/cms/content/1/publish/')
    assert response.status_code == 200
```

**Marqueurs** : `@pytest.mark.critical`

**Durée estimée** : ~3-5 min

---

#### C) E2E Full-Stack Ultra Robustes

**Objectif** : Tests E2E complets avec backend réel + DB + Redis (pas de mocks pour flux critiques)

**Fichiers à créer** :
- `frontend/frontend/e2e/onboarding-login-dashboard.spec.js` : Onboarding -> login -> dashboard
- `frontend/frontend/e2e/contenu-saka-reward.spec.js` : Cycle contenu -> SAKA reward
- Modifier `frontend/frontend/e2e/flux-complet-projet-financement.spec.js` : Compléter traçabilité

**Approche** :
- Utiliser mode `full-stack` Playwright (nécessite backend réel)
- Utiliser `waitForFunction` pour éviter flakiness
- Vérifier UI + API (appels API réels)
- Utiliser fixtures auth existantes (`e2e/fixtures/auth.js`)

**Exemple structure** :
```javascript
// frontend/frontend/e2e/onboarding-login-dashboard.spec.js
import { test, expect } from '@playwright/test';
import { loginAsUser } from './fixtures/auth';

test.describe('Onboarding -> Login -> Dashboard', () => {
  test('complete flow', async ({ page }) => {
    // 1. Onboarding
    await page.goto('/');
    await page.click('text=Rejoindre');
    // ... remplir formulaire
    
    // 2. Login
    await loginAsUser(page, 'test@example.com', 'password');
    
    // 3. Dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('text=Tableau de bord')).toBeVisible();
  });
});
```

**Configuration** : Ajouter au projet `full-stack` dans `playwright.config.js`

**Durée estimée** : ~10-15 min par test

---

#### D) Tests Anti-Dérive

**Objectif** : Détecter les violations de la Constitution EGOEJO (promesses financières, symboles monétaires)

**Fichiers à créer** :
- `backend/core/tests/compliance/test_promesses_financieres.py` : Validation promesses "dons nets"
- Modifier `scripts/audit_content.py` : Ajouter validation promesses financières (si manquant)

**Approche** :
- Scanner texte contenus/projets pour promesses "100% des dons" sans "nets après frais"
- Utiliser regex ou parsing simple
- Intégrer dans workflow compliance

**Exemple structure** :
```python
# backend/core/tests/compliance/test_promesses_financieres.py
@pytest.mark.egoejo_compliance
def test_promesses_financieres_doivent_mentionner_frais():
    """Vérifie que les promesses financières mentionnent 'nets après frais'"""
    # Scanner tous les contenus publiés
    # Vérifier que si "100% des dons" ou "tous les dons" -> doit contenir "nets après frais"
    pass
```

**Marqueurs** : `@pytest.mark.egoejo_compliance`

**Durée estimée** : ~1-2 min

---

#### E) Tests Data Integrity

**Objectif** : Vérifier l'intégrité des données (transaction_type, cohérence SakaWallet <-> SakaTransaction)

**Fichiers à créer** :
- `backend/core/tests/models/test_data_integrity_complete.py` : Intégrité complète

**Approche** :
- Vérifier que transaction_type est toujours non-null (déjà fait, mais compléter)
- Vérifier cohérence SakaWallet <-> SakaTransaction (somme transactions = solde wallet)
- Détection bypass raw SQL (déjà fait dans `test_saka_wallet_raw_sql.py`, mais compléter)

**Exemple structure** :
```python
# backend/core/tests/models/test_data_integrity_complete.py
@pytest.mark.critical
@pytest.mark.egoejo_compliance
def test_saka_wallet_transaction_consistency():
    """Vérifie que la somme des transactions = solde wallet"""
    wallet = SakaWallet.objects.create(user=user, balance=100)
    SakaTransaction.objects.create(wallet=wallet, amount=50, transaction_type='grant')
    SakaTransaction.objects.create(wallet=wallet, amount=50, transaction_type='grant')
    # Vérifier que wallet.balance = 100 (somme transactions)
    assert wallet.balance == 100
```

**Marqueurs** : `@pytest.mark.critical` + `@pytest.mark.egoejo_compliance`

**Durée estimée** : ~2-3 min

---

### ÉTAPE 3 - Tests P1 IMPORTANTS

#### A) Accessibilité Automatisée

**Objectif** : Tests accessibilité automatisés (axe-core) sur pages clés

**Fichiers à créer** :
- `frontend/frontend/src/__tests__/accessibility/a11y.test.jsx` : Tests a11y unitaires
- `frontend/frontend/e2e/accessibility.spec.js` : Tests a11y E2E

**Approche** :
- Utiliser `@axe-core/react` pour tests unitaires
- Utiliser `@axe-core/playwright` pour tests E2E
- Tester pages clés : Accueil, Vision, Contenus, Projet, Dashboard

**Exemple structure** :
```javascript
// frontend/frontend/e2e/accessibility.spec.js
import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Accessibility', () => {
  test('home page is accessible', async ({ page }) => {
    await page.goto('/');
    await injectAxe(page);
    await checkA11y(page);
  });
});
```

**Durée estimée** : ~2-3 min

---

#### B) XSS Sanitization

**Objectif** : Vérifier que le contenu est sanitized (pas de XSS)

**Fichiers à créer** :
- `backend/core/tests/cms/test_xss_sanitization.py` : Tests XSS backend
- `frontend/frontend/src/utils/__tests__/xss.test.js` : Tests XSS frontend

**Approche** :
- Injecter payloads XSS dans description contenu
- Vérifier que le HTML est échappé/sanitized
- Utiliser `bleach` ou équivalent backend
- Utiliser `DOMPurify` ou équivalent frontend

**Durée estimée** : ~1-2 min

---

#### C) Pagination/Perf Light

**Objectif** : Vérifier que la pagination fonctionne (ne charge pas "tout")

**Fichiers à créer** :
- `backend/core/tests/api/test_pagination.py` : Tests pagination API
- `frontend/frontend/e2e/pagination.spec.js` : Tests pagination E2E

**Approche** :
- Vérifier que l'API retourne `page_size` résultats max
- Vérifier que l'UI affiche pagination si > `page_size` résultats
- Vérifier que le nombre de requêtes API est limité

**Durée estimée** : ~1-2 min

---

#### D) Retry/Backoff

**Objectif** : Vérifier que useFetch retry/backoff fonctionne

**Fichiers à créer** :
- `frontend/frontend/src/hooks/__tests__/useFetch-retry.test.js` : Tests retry useFetch

**Approche** :
- Mock API pour retourner erreur 500
- Vérifier que useFetch retry (3 tentatives)
- Vérifier que le backoff augmente entre tentatives

**Durée estimée** : ~1 min

---

#### E) Rate-Limit

**Objectif** : Vérifier que le rate-limit fonctionne sur endpoints sensibles

**Fichiers à créer** :
- `backend/core/tests/api/test_rate_limit.py` : Tests rate-limit

**Approche** :
- Faire N requêtes rapides sur endpoint sensible
- Vérifier que la N+1ème requête retourne 429 (Too Many Requests)
- Vérifier que le rate-limit est reset après délai

**Durée estimée** : ~1-2 min

---

#### F) Websocket/Chat Smoke

**Objectif** : Tests smoke websocket/chat (si feature existante)

**Fichiers à créer** :
- `frontend/frontend/e2e/websocket-chat.spec.js` : Tests smoke websocket

**Approche** :
- Connecter websocket
- Envoyer message
- Vérifier réception
- Déconnecter
- Vérifier auth websocket

**Durée estimée** : ~1-2 min (si feature existante)

---

### ÉTAPE 4 - CI Wiring

#### A) Jobs Structurés

**Objectif** : Structurer la suite en jobs distincts (lint, backend unit, backend permissions, backend compliance, frontend unit, frontend e2e, a11y)

**Fichiers à créer/modifier** :
- Modifier `.github/workflows/ci.yml` : Ajouter jobs distincts
- Créer `.github/workflows/test-comprehensive.yml` : Workflow tests complets

**Structure jobs** :
```yaml
jobs:
  lint-audit:
    # Lint + audit statique
  backend-unit:
    # Backend unit tests (sans compliance)
  backend-permissions:
    # Backend permissions tests (critical)
  backend-compliance:
    # Backend compliance tests (egoejo_compliance)
  frontend-unit:
    # Frontend unit tests
  frontend-e2e-critical:
    # Frontend E2E critiques (shard 1/2 + 2/2)
  a11y:
    # Accessibilité (non bloquant au début, puis bloquant)
```

**Durée estimée** : ~30 min

---

#### B) Artefacts CI

**Objectif** : Générer artefacts JUnit + HTML report Playwright + JSON compliance

**Fichiers à créer/modifier** :
- Modifier `backend/pytest.ini` : Ajouter `--junitxml=junit.xml`
- Modifier workflows CI : Upload artefacts

**Artefacts** :
- `backend/junit.xml` : JUnit report backend
- `frontend/frontend/playwright-report/` : HTML report Playwright
- `backend/compliance-report.json` : JSON compliance

**Durée estimée** : ~15 min

---

#### C) Sharding E2E

**Objectif** : Paralléliser tests E2E avec sharding

**Fichiers à créer/modifier** :
- Modifier `.github/workflows/test-comprehensive.yml` : Ajouter sharding E2E

**Approche** :
- Utiliser `playwright test --shard=1/2` et `--shard=2/2`
- Diviser tests E2E en 2 shards

**Durée estimée** : ~10 min

---

#### D) Retries Intelligents

**Objectif** : Retries intelligents sur E2E UNIQUEMENT si timeout/infrastructure (pas sur erreurs fonctionnelles)

**Fichiers à créer/modifier** :
- Modifier `playwright.config.js` : Configurer retries (déjà fait, mais améliorer)
- Ajouter retries backend si timeout

**Approche** :
- Retries Playwright : 2 en CI (déjà fait)
- Retries backend : Ajouter si timeout/infrastructure

**Durée estimée** : ~5 min

---

#### E) Healthchecks

**Objectif** : Healthchecks (postgres/redis/backend/front) avant E2E

**Fichiers à créer/modifier** :
- Modifier workflows CI : Ajouter healthchecks avant E2E

**Approche** :
- Vérifier postgres : `pg_isready` (déjà fait via services)
- Vérifier redis : `redis-cli ping` (déjà fait via services)
- Vérifier backend : `curl http://localhost:8000/api/health/`
- Vérifier frontend : `curl http://localhost:5173/`

**Durée estimée** : ~10 min

---

### ÉTAPE 5 - Livrables

#### A) Test Plan Opposable

**Fichiers à créer** :
- `docs/testing/TEST_STRATEGY_END_TO_END.md` : Stratégie tests end-to-end
- `docs/testing/REQUIRED_CHECKS.md` : Checklist auto (si existe, compléter)

**Contenu** :
- Objectif de chaque test
- Risque couvert
- Niveau (P0/P1/P2)
- Temps d'exécution visé
- Garanties déterministes

**Durée estimée** : ~30 min

---

#### B) Commandes Locales

**Fichiers à créer/modifier** :
- Modifier `test_protocol.ps1` : Ajouter commandes "run all" + "run critical only"
- Créer `scripts/run-tests-all.sh` : Script bash pour "run all"
- Créer `scripts/run-tests-critical.sh` : Script bash pour "run critical only"

**Commandes** :
```bash
# Run all tests
./scripts/run-tests-all.sh

# Run critical only (P0)
./scripts/run-tests-critical.sh
```

**Durée estimée** : ~15 min

---

#### C) Garanties Anti-Flaky

**Fichiers à créer/modifier** :
- Modifier `frontend/frontend/e2e/utils/test-helpers.js` : Ajouter helpers anti-flaky
- Documenter dans `docs/testing/TEST_STRATEGY_END_TO_END.md`

**Helpers** :
- `waitForFunction` : Attendre condition
- `waitForAPI` : Attendre réponse API
- `retryOnFlaky` : Retry sur erreurs flaky

**Durée estimée** : ~20 min

---

## 📊 RÉSUMÉ TEMPS ESTIMÉ

| Étape | Temps Estimé |
|-------|--------------|
| ÉTAPE 2 (P0) | ~4-6 heures |
| ÉTAPE 3 (P1) | ~2-3 heures |
| ÉTAPE 4 (CI) | ~1-2 heures |
| ÉTAPE 5 (Livrables) | ~1-2 heures |
| **TOTAL** | **~8-13 heures** |

---

## ✅ VALIDATION FINALE

Avant de merger, vérifier :
- ✅ Tous les tests P0 passent
- ✅ Tous les tests P1 passent
- ✅ CI wiring fonctionne (jobs, sharding, artefacts)
- ✅ Documentation complète (test plan, checklist)
- ✅ Commandes locales fonctionnent
- ✅ Garanties anti-flaky en place

---

## 🚀 PROCHAINES ACTIONS

1. **Valider ce plan** avec l'équipe
2. **Commencer ÉTAPE 2** (Tests P0 bloquants)
3. **Implémenter par petites PRs** (une feature à la fois)
4. **Tester chaque PR** avant merge
5. **Documenter au fur et à mesure**

