# 🔍 DIAGNOSTIC STRIPE - PHASE TEST MODE

**Date** : 2025-01-27  
**Objectif** : Compléter Stripe en mode test (sandbox) + tests P0

---

## ✅ CE QUI EXISTE DÉJÀ

### 1. Backend
- ✅ `StripeWebhookView` dans `backend/finance/views.py`
  - Route : `/api/finance/stripe/webhook/`
  - Gère `payment_intent.succeeded`
  - **Note** : "Vérification de la signature Stripe (à implémenter si nécessaire)" - **MANQUE**
  
- ✅ `process_stripe_payment_webhook()` dans `backend/finance/ledger_services/ledger.py`
  - Répartition proportionnelle des frais
  - Extraction des frais depuis webhook
  - **Idempotence** : Partiellement implémentée via `idempotency_key` (UUID v5 depuis `payment_intent.id`)

### 2. Tests Existants
- ✅ `backend/finance/tests/test_stripe_segregation.py` : Tests d'intégration (6 tests)
- ✅ `backend/finance/tests/test_ledger_fee_allocation.py` : Tests unitaires (8 tests)
- ✅ `backend/finance/tests/test_contract_webhooks_stripe.py` : Tests contract (6 tests)

### 3. Settings
- ✅ `STRIPE_FIXED_FEE` (0.25€)
- ✅ `STRIPE_PERCENT_FEE` (1.5%)
- ✅ `STRIPE_FEE_ESTIMATE` (3%)
- ❌ **MANQUE** : `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`

---

## ❌ GAPS P0 À IMPLÉMENTER

### 1. Signature Verification Webhook (P0 BLOQUANT)
- **Status** : Commentaire "à implémenter si nécessaire" dans `StripeWebhookView`
- **Action** : Implémenter vérification signature avec `STRIPE_WEBHOOK_SECRET`
- **Tests** : Tests unitaires + contract tests

### 2. Idempotence Complète (P0 BLOQUANT)
- **Status** : Partiellement implémentée (UUID v5 depuis `payment_intent.id`)
- **Gap** : Tests manquants pour vérifier que replay `event.id` est no-op
- **Action** : Ajouter tests d'idempotence avec replay du même `event.id`

### 3. Contract Tests Schema Minimal (P0)
- **Status** : Tests contract existants mais incomplets
- **Gap** : Vérification des champs obligatoires du payload webhook
- **Action** : Améliorer tests contract pour valider schéma minimal

### 4. Mode Test Strict (P0 BLOQUANT)
- **Status** : Aucun guard pour refuser clés live en CI
- **Action** : Ajouter guard dans `StripeWebhookView` et `checkout-session` endpoint
- **Tests** : Tests pour vérifier que clés live sont refusées en CI

### 5. Endpoint Checkout-Session (P0)
- **Status** : **ABSENT** (aucun endpoint trouvé)
- **Action** : Créer `POST /api/payments/stripe/checkout-session` (test only)
- **Tests** : Contract tests pour l'endpoint

### 6. E2E Playwright Hybride (P0)
- **Status** : **ABSENT**
- **Action** : Créer test E2E hybride :
  - UI déclenche création checkout-session -> reçoit URL
  - Simuler webhook côté backend via POST signé (fixture) -> UI reflète transaction
- **Fixtures** : Stripe event + signature

### 7. Documentation (P1)
- **Status** : **ABSENT**
- **Action** : Créer `docs/finance/STRIPE_TEST_MODE.md`

---

## 📋 PLAN D'EXÉCUTION

### Étape 1 : Settings Stripe
- Ajouter `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET` dans `settings.py`
- Ajouter guard pour mode test (refuser clés live en CI)

### Étape 2 : Signature Verification
- Implémenter `verify_stripe_signature()` dans `StripeWebhookView`
- Ajouter tests unitaires + contract tests

### Étape 3 : Idempotence
- Améliorer idempotence avec `event.id` (en plus de `payment_intent.id`)
- Ajouter tests pour replay `event.id`

### Étape 4 : Contract Tests
- Améliorer tests contract pour valider schéma minimal (champs obligatoires)

### Étape 5 : Endpoint Checkout-Session
- Créer `StripeCheckoutSessionView` dans `backend/finance/views.py`
- Ajouter route `/api/payments/stripe/checkout-session`
- Contract tests

### Étape 6 : E2E Playwright
- Créer test E2E hybride dans `frontend/frontend/e2e/`
- Fixtures Stripe event + signature

### Étape 7 : Documentation
- Créer `docs/finance/STRIPE_TEST_MODE.md`

---

## 🔧 FICHIERS À MODIFIER/CRÉER

### Modifications
- `backend/config/settings.py` : Ajouter settings Stripe
- `backend/finance/views.py` : Ajouter signature verification + guard test mode + checkout-session endpoint
- `backend/core/urls.py` : Ajouter route checkout-session

### Créations
- `backend/finance/tests/test_stripe_signature.py` : Tests signature verification
- `backend/finance/tests/test_stripe_idempotence.py` : Tests idempotence
- `backend/finance/tests/test_stripe_checkout_session.py` : Tests checkout-session
- `frontend/frontend/e2e/stripe-payment.spec.js` : Test E2E hybride
- `frontend/frontend/e2e/fixtures/stripe-webhook-event.json` : Fixture Stripe event
- `docs/finance/STRIPE_TEST_MODE.md` : Documentation

---

## ✅ CRITÈRES DE SUCCÈS

1. ✅ Signature webhook vérifiée (tests passent)
2. ✅ Idempotence complète (replay event.id = no-op)
3. ✅ Contract tests valident schéma minimal
4. ✅ Guard test mode refuse clés live en CI
5. ✅ Endpoint checkout-session fonctionne (test only)
6. ✅ E2E Playwright hybride passe
7. ✅ Documentation complète

---

**Statut** : 🔄 **EN COURS D'IMPLÉMENTATION**

