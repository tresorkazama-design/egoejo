# 🔍 DIAGNOSTIC & PLAN PRs - Tests Ultra-Élargis EGOEJO

**Date** : 2025-01-XX  
**Objectif** : Diagnostic vérifié + Plan PRs atomiques (P0 puis P1)

---

## ✅ A) DIAGNOSTIC VÉRIFIÉ DANS LE REPO

### 1. Contract Tests API

**État** : ❌ **MANQUE COMPLÈTEMENT**

**Vérification** :
```bash
# Aucun fichier test_*contract*.py trouvé
# Aucun test vérifiant schémas de réponse API
```

**Fichiers à créer** :
- `backend/core/tests/api/test_contract_health.py`
- `backend/core/tests/api/test_contract_saka.py`
- `backend/core/tests/api/test_contract_cms.py`
- `backend/core/tests/api/test_contract_projects.py`
- `backend/finance/tests/test_contract_webhooks_stripe.py`

---

### 2. E2E Full-Stack Critiques

**État** : ⚠️ **PARTIEL** (seulement 2 tests dans `e2e-fullstack.yml`)

**Vérification** :
- ✅ `frontend/frontend/e2e/flux-complet-saka-vote.spec.js` : EXISTE
- ✅ `frontend/frontend/e2e/flux-complet-projet-financement.spec.js` : EXISTE
- ❌ `frontend/frontend/e2e/onboarding-login-dashboard.spec.js` : **MANQUE**
- ❌ `frontend/frontend/e2e/contenu-saka-reward.spec.js` : **MANQUE**
- ⚠️ `frontend/frontend/e2e/flux-complet-projet-financement.spec.js` : EXISTE mais traçabilité incomplète

**Fichiers à créer/modifier** :
- `frontend/frontend/e2e/onboarding-login-dashboard.spec.js` (NOUVEAU)
- `frontend/frontend/e2e/contenu-saka-reward.spec.js` (NOUVEAU)
- Modifier `frontend/frontend/e2e/flux-complet-projet-financement.spec.js` (compléter traçabilité)

---

### 3. Stripe Payments

**État** : ⚠️ **PARTIEL**

**Vérification** :
- ✅ `backend/finance/views.py` : `StripeWebhookView` existe (ligne 158-302)
- ✅ `backend/finance/ledger_services/ledger.py` : `process_stripe_payment_webhook()` existe
- ✅ Idempotence : **EXISTE** (via `idempotency_key` dans `ledger.py` ligne 389-409)
- ❌ Signature webhook : **MANQUE** (commentaire ligne 168 : "à implémenter si nécessaire")
- ❌ Contract tests webhook : **MANQUE**
- ❌ E2E Playwright paiement réel : **MANQUE**
- ❌ Mode test strict : **MANQUE** (pas de vérification STRIPE_API_KEY test only en CI)

**Fichiers à créer/modifier** :
- Modifier `backend/finance/views.py` : Ajouter vérification signature webhook
- `backend/finance/tests/test_contract_webhooks_stripe.py` (NOUVEAU)
- `backend/finance/tests/test_stripe_webhook_signature.py` (NOUVEAU)
- `backend/finance/tests/test_stripe_webhook_idempotence.py` (NOUVEAU)
- `frontend/frontend/e2e/stripe-payment-real.spec.js` (NOUVEAU)
- Modifier `.github/workflows/ci.yml` : Ajouter vérification mode test strict

---

### 4. CMS Workflow

**État** : ✅ **EXISTE** (workflow complet) mais gaps tests

**Vérification** :
- ✅ `backend/core/api/content_views.py` : Endpoints publish/reject/archive/unpublish existent
- ✅ `backend/core/tests/cms/test_content_permissions.py` : Tests permissions existent
- ✅ `backend/core/tests/cms/test_content_workflow_transitions.py` : Tests workflow existent
- ❌ Tests XSS sanitization : **MANQUE**
- ❌ Tests pagination : **MANQUE**
- ❌ Tests export JSON/CSV : **MANQUE** (endpoints manquants aussi)
- ❌ E2E complet workflow : **MANQUE**

**Fichiers à créer/modifier** :
- `backend/core/tests/cms/test_xss_sanitization.py` (NOUVEAU)
- `backend/core/tests/cms/test_pagination.py` (NOUVEAU)
- `backend/core/api/content_views.py` : Ajouter endpoints export JSON/CSV
- `backend/core/tests/cms/test_content_export.py` (NOUVEAU)
- `frontend/frontend/e2e/cms-workflow-complete.spec.js` (NOUVEAU)

---

### 5. Artefacts CI

**État** : ⚠️ **PARTIEL**

**Vérification** :
- ✅ Playwright report : Upload existe dans `e2e-fullstack.yml` et `audit-global.yml`
- ❌ JUnit XML backend : **MANQUE** (pas de `--junitxml` dans `pytest.ini`)
- ❌ JSON compliance : **MANQUE** (pas d'export JSON compliance)

**Fichiers à modifier** :
- `backend/pytest.ini` : Ajouter `--junitxml=junit.xml`
- `.github/workflows/egoejo-compliance.yml` : Ajouter upload JUnit + JSON compliance

---

### 6. WebSocket Chat E2E

**État** : ⚠️ **PARTIEL** (backend existe, tests E2E manquent)

**Vérification** :
- ✅ `backend/core/consumers.py` : `ChatConsumer` existe
- ✅ `frontend/frontend/src/hooks/useWebSocket.js` : Hook WebSocket existe
- ✅ Tests unitaires frontend : Existent (mocks)
- ❌ Tests E2E Playwright WebSocket réel : **MANQUE**
- ❌ Tests integration backend (Channels testing) : **MANQUE**

**Fichiers à créer** :
- `backend/core/tests/consumers/test_chat_consumer.py` (NOUVEAU)
- `frontend/frontend/e2e/websocket-chat-real.spec.js` (NOUVEAU)

---

### 7. P1 - Accessibilité, Pagination, etc.

**État** : ❌ **MANQUE** (sauf partiel)

**Vérification** :
- ❌ Tests a11y (axe-core) : **MANQUE**
- ❌ Tests pagination API : **MANQUE**
- ❌ Tests retry/backoff useFetch : **MANQUE**
- ❌ Tests rate-limit : **MANQUE**

**Fichiers à créer** :
- `frontend/frontend/src/__tests__/accessibility/a11y.test.jsx` (NOUVEAU)
- `frontend/frontend/e2e/accessibility.spec.js` (NOUVEAU)
- `backend/core/tests/api/test_rate_limit.py` (NOUVEAU)
- `frontend/frontend/src/hooks/__tests__/useFetch-retry.test.js` (NOUVEAU)

---

## 📋 B) SÉQUENCEMENT PRs (P0 BLOQUANTS PUIS P1)

### PR #1 : Contract Tests API (P0 BLOQUANT)

**Objectif** : Ajouter tests contract pour endpoints critiques (health, SAKA, CMS, projects, Stripe webhook)

**Fichiers à créer** :
- `backend/core/tests/api/test_contract_health.py`
- `backend/core/tests/api/test_contract_saka.py`
- `backend/core/tests/api/test_contract_cms.py`
- `backend/core/tests/api/test_contract_projects.py`
- `backend/finance/tests/test_contract_webhooks_stripe.py`

**Fichiers à modifier** :
- `backend/pytest.ini` : Ajouter marqueur `@pytest.mark.contract` (optionnel)

**Commandes de validation** :
```bash
cd backend
pytest core/tests/api/test_contract_*.py -v
pytest finance/tests/test_contract_webhooks_stripe.py -v
```

**Durée estimée** : ~2-3 heures

---

### PR #2 : Stripe Webhook Signature + Idempotence (P0 BLOQUANT)

**Objectif** : Implémenter vérification signature webhook Stripe + tests idempotence

**Fichiers à modifier** :
- `backend/finance/views.py` : Ajouter vérification signature (ligne 172)
- `backend/config/settings.py` : Ajouter `STRIPE_WEBHOOK_SECRET`

**Fichiers à créer** :
- `backend/finance/tests/test_stripe_webhook_signature.py`
- `backend/finance/tests/test_stripe_webhook_idempotence.py`

**Commandes de validation** :
```bash
cd backend
pytest finance/tests/test_stripe_webhook_signature.py -v
pytest finance/tests/test_stripe_webhook_idempotence.py -v
```

**Durée estimée** : ~1-2 heures

---

### PR #3 : E2E Full-Stack Critiques (P0 BLOQUANT)

**Objectif** : Ajouter tests E2E manquants (onboarding/login/dashboard, contenu->SAKA reward, projet->financement EUR->traçabilité)

**Fichiers à créer** :
- `frontend/frontend/e2e/onboarding-login-dashboard.spec.js`
- `frontend/frontend/e2e/contenu-saka-reward.spec.js`

**Fichiers à modifier** :
- `frontend/frontend/e2e/flux-complet-projet-financement.spec.js` : Compléter traçabilité

**Commandes de validation** :
```bash
cd frontend/frontend
npm run test:e2e -- e2e/onboarding-login-dashboard.spec.js
npm run test:e2e -- e2e/contenu-saka-reward.spec.js
npm run test:e2e -- e2e/flux-complet-projet-financement.spec.js
```

**Durée estimée** : ~3-4 heures

---

### PR #4 : CMS XSS + Pagination + Export (P0 BLOQUANT)

**Objectif** : Ajouter tests XSS sanitization, pagination, et endpoints export JSON/CSV

**Fichiers à créer** :
- `backend/core/tests/cms/test_xss_sanitization.py`
- `backend/core/tests/cms/test_pagination.py`
- `backend/core/tests/cms/test_content_export.py`

**Fichiers à modifier** :
- `backend/core/api/content_views.py` : Ajouter endpoints export JSON/CSV

**Commandes de validation** :
```bash
cd backend
pytest core/tests/cms/test_xss_sanitization.py -v
pytest core/tests/cms/test_pagination.py -v
pytest core/tests/cms/test_content_export.py -v
```

**Durée estimée** : ~2-3 heures

---

### PR #5 : CMS E2E Workflow Complet (P0 BLOQUANT)

**Objectif** : Ajouter test E2E workflow complet (Contributor -> Editor -> Reviewer -> Archive -> Export)

**Fichiers à créer** :
- `frontend/frontend/e2e/cms-workflow-complete.spec.js`

**Commandes de validation** :
```bash
cd frontend/frontend
npm run test:e2e -- e2e/cms-workflow-complete.spec.js
```

**Durée estimée** : ~2 heures

---

### PR #6 : Stripe E2E Paiement Réel (P0 BLOQUANT)

**Objectif** : Ajouter test E2E paiement Stripe réel (checkout -> webhook -> UI)

**Fichiers à créer** :
- `frontend/frontend/e2e/stripe-payment-real.spec.js`

**Fichiers à modifier** :
- `.github/workflows/ci.yml` : Ajouter vérification mode test strict (STRIPE_API_KEY test only)

**Commandes de validation** :
```bash
cd frontend/frontend
npm run test:e2e -- e2e/stripe-payment-real.spec.js
```

**Durée estimée** : ~2-3 heures

---

### PR #7 : Artefacts CI (P0 BLOQUANT)

**Objectif** : Ajouter artefacts JUnit backend + JSON compliance

**Fichiers à modifier** :
- `backend/pytest.ini` : Ajouter `--junitxml=junit.xml`
- `.github/workflows/egoejo-compliance.yml` : Ajouter upload JUnit + JSON compliance
- `.github/workflows/ci.yml` : Ajouter upload JUnit backend

**Commandes de validation** :
```bash
cd backend
pytest --junitxml=junit.xml -v
# Vérifier que junit.xml est généré
```

**Durée estimée** : ~30 min

---

### PR #8 : WebSocket Chat E2E Réel (P1)

**Objectif** : Ajouter tests E2E WebSocket chat réel + integration backend

**Fichiers à créer** :
- `backend/core/tests/consumers/test_chat_consumer.py`
- `frontend/frontend/e2e/websocket-chat-real.spec.js`

**Commandes de validation** :
```bash
cd backend
pytest core/tests/consumers/test_chat_consumer.py -v
cd frontend/frontend
npm run test:e2e -- e2e/websocket-chat-real.spec.js
```

**Durée estimée** : ~2-3 heures

---

### PR #9 : Accessibilité (P1)

**Objectif** : Ajouter tests a11y automatisés (axe-core)

**Fichiers à créer** :
- `frontend/frontend/src/__tests__/accessibility/a11y.test.jsx`
- `frontend/frontend/e2e/accessibility.spec.js`

**Commandes de validation** :
```bash
cd frontend/frontend
npm run test:a11y
npm run test:e2e -- e2e/accessibility.spec.js
```

**Durée estimée** : ~1-2 heures

---

### PR #10 : Rate-Limit + Retry/Backoff (P1)

**Objectif** : Ajouter tests rate-limit + retry/backoff useFetch

**Fichiers à créer** :
- `backend/core/tests/api/test_rate_limit.py`
- `frontend/frontend/src/hooks/__tests__/useFetch-retry.test.js`

**Commandes de validation** :
```bash
cd backend
pytest core/tests/api/test_rate_limit.py -v
cd frontend/frontend
npm test -- useFetch-retry.test.js
```

**Durée estimée** : ~1-2 heures

---

## 🚀 C) EXÉCUTION PR #1 (P0 LA PLUS CRITIQUE)

**PR #1 : Contract Tests API**

Commençons par implémenter les contract tests pour les endpoints critiques.

