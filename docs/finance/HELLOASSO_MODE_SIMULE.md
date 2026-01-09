# 💳 HELLOASSO - MODE SIMULÉ EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0  
**Objectif** : Implémentation minimale HelloAsso en mode simulé (tests CI sans réseau externe)

---

## 🎯 Vue d'Ensemble

Le système HelloAsso EGOEJO permet de recevoir des dons via HelloAsso (association loi 1901, reçu fiscal). L'implémentation est en **mode simulé** pour les tests CI, évitant toute dépendance réseau externe.

**Caractéristiques** :
- ✅ Client HelloAsso injectable/mockable
- ✅ Endpoints checkout et webhook
- ✅ Idempotence via `event.id` + `payment.id`
- ✅ Vérification signature webhook (X-HelloAsso-Signature)
- ✅ Mode simulé par défaut (pas de réseau externe en CI)
- ✅ Tests contractuels complets

---

## 📁 Architecture

### Fichiers Principaux

- **`backend/finance/helloasso_client.py`** : Client HelloAsso mockable
  - `HelloAssoClient` : Interface injectable
  - `get_access_token()` : Obtient token OAuth (mocké en mode simulé)
  - `create_payment_form()` : Crée formulaire de paiement (mocké)
  - `verify_webhook_signature()` : Vérifie signature webhook

- **`backend/finance/ledger_services/helloasso_ledger.py`** : Service Ledger HelloAsso
  - `process_helloasso_payment_webhook()` : Traite webhook et alloue aux Ledgers
  - `extract_helloasso_fee_from_webhook()` : Extrait/estime les frais HelloAsso

- **`backend/finance/views.py`** : Endpoints API
  - `HelloAssoCheckoutView` : `POST /api/payments/helloasso/start/`
  - `HelloAssoWebhookView` : `POST /api/payments/helloasso/webhook/`

---

## 🔧 Configuration

### Variables d'Environnement

```bash
# HelloAsso Configuration (Mode Simulé)
HELLOASSO_CLIENT_ID=your_client_id  # Optionnel en mode simulé
HELLOASSO_CLIENT_SECRET=your_client_secret  # Optionnel en mode simulé
HELLOASSO_WEBHOOK_SECRET=your_webhook_secret  # Obligatoire pour vérification signature

# Mode Simulé (par défaut: True)
HELLOASSO_SIMULATED_MODE=True  # Pas de réseau externe en CI
```

### Configuration Django Settings

Les variables d'environnement sont automatiquement chargées dans `backend/config/settings.py` :

```python
# HelloAsso Configuration (Mode Simulé)
HELLOASSO_CLIENT_ID = os.environ.get('HELLOASSO_CLIENT_ID', '')
HELLOASSO_CLIENT_SECRET = os.environ.get('HELLOASSO_CLIENT_SECRET', '')
HELLOASSO_WEBHOOK_SECRET = os.environ.get('HELLOASSO_WEBHOOK_SECRET', '')

# Mode Simulé : Par défaut activé (pas de réseau externe en CI)
HELLOASSO_SIMULATED_MODE = os.environ.get('HELLOASSO_SIMULATED_MODE', 'True').lower() == 'true'
```

---

## 📖 Utilisation

### Endpoint Checkout (Créer Formulaire de Paiement)

**POST** `/api/payments/helloasso/start/`

**Authentification** : Requise (JWT)

**Body JSON** :
```json
{
  "amount": "100.00",
  "project_id": 123,
  "metadata": {}
}
```

**Réponse 200** :
```json
{
  "success": true,
  "payment_form_url": "https://simulated.helloasso.com/payment/mock_123_456",
  "payment_form_id": "mock_form_123_456",
  "expires_at": "2025-12-31T23:59:59Z"
}
```

**Erreurs** :
- `400` : `amount` manquant ou invalide
- `401` : Non authentifié
- `404` : Projet introuvable
- `500` : Erreur serveur

### Endpoint Webhook (Recevoir Paiement)

**POST** `/api/payments/helloasso/webhook/`

**Authentification** : Aucune (webhook HelloAsso)

**Headers** :
- `X-HelloAsso-Signature` : Signature HMAC-SHA256 (obligatoire si `HELLOASSO_WEBHOOK_SECRET` configuré)

**Body JSON** (événement HelloAsso) :
```json
{
  "eventType": "Payment",
  "eventId": "evt_123",
  "data": {
    "payment": {
      "id": "payment_123",
      "amount": 10000,
      "fee": 80,
      "metadata": {
        "user_id": "123",
        "project_id": "456",
        "donation_amount": "100.00",
        "tip_amount": "0.00"
      }
    }
  }
}
```

**Réponse 200** :
```json
{
  "status": "success",
  "donation": {
    "amount_gross": "100.00",
    "helloasso_fee": "0.80",
    "amount_net": "99.20",
    "transaction_id": 789
  },
  "tip": null
}
```

**Erreurs** :
- `400` : JSON invalide, `eventType` manquant, `user_id` manquant
- `401` : Signature invalide
- `404` : Utilisateur ou projet introuvable
- `500` : Erreur serveur

---

## 🔐 Sécurité

### Vérification Signature Webhook

HelloAsso utilise un header `X-HelloAsso-Signature` avec un secret partagé :
- Format : HMAC-SHA256 du payload avec le secret
- Vérification automatique si `HELLOASSO_WEBHOOK_SECRET` est configuré
- En mode développement (secret manquant), accepte sans signature (warning log)

### Idempotence

L'idempotence est garantie via :
- `event.id` : Identifiant unique de l'événement HelloAsso
- `payment.id` : Identifiant unique du paiement
- Génération UUID v5 déterministe : `uuid5(namespace, f"helloasso_{event_id}_{payment_id}")`
- Vérification dans `WalletTransaction` avant création

**Replay** : Si un événement est rejoué, retourne `200` avec message "Événement déjà traité (idempotence)" sans créer de nouvelle transaction.

---

## 💰 Frais HelloAsso

### Estimation des Frais

HelloAsso ne fournit pas toujours les frais dans le webhook. En mode simulé, on utilise une estimation basée sur les frais HelloAsso standards :

- **Frais variables** : 0.8% du montant
- **Frais fixes** : 0.25€ par transaction
- **Formule** : `fees = (amount * 0.008) + 0.25`

Si les frais sont fournis dans le webhook (`payment.fee`), ils sont utilisés directement.

### Stockage des Frais

Les frais HelloAsso sont stockés dans `WalletTransaction.stripe_fee` (même champ que Stripe pour cohérence du modèle) :
- `amount_gross` : Montant brut (avant frais)
- `stripe_fee` : Frais HelloAsso (part proportionnelle si donation + tip)
- `amount_net` : Montant net (après frais)

---

## 🧪 Tests

### Tests Contractuels

Les tests sont disponibles dans `backend/finance/tests/test_helloasso_contract.py` :

**Tests Checkout** :
- ✅ `test_checkout_requires_authentication` : Anon forbidden (401/403)
- ✅ `test_checkout_requires_amount` : Amount requis (400)
- ✅ `test_checkout_validates_amount_format` : Format amount validé (400)
- ✅ `test_checkout_validates_amount_positive` : Amount > 0 (400)
- ✅ `test_checkout_creates_payment_form` : Création formulaire (200)
- ✅ `test_checkout_handles_missing_project` : Projet introuvable (404)

**Tests Webhook** :
- ✅ `test_webhook_accepts_post_only` : POST uniquement (405/404)
- ✅ `test_webhook_requires_valid_json` : JSON valide (400)
- ✅ `test_webhook_requires_event_type` : EventType requis (400)
- ✅ `test_webhook_validates_signature` : Signature validée (401)
- ✅ `test_webhook_handles_payment_event` : Traitement Payment (200)
- ✅ `test_webhook_ignores_unknown_events` : Événements inconnus ignorés (200)
- ✅ `test_webhook_handles_missing_user_id` : User_id manquant (400)

**Tests Idempotence** :
- ✅ `test_webhook_idempotence_replay_event` : Replay event.id = no-op

**Tests Sécurité** :
- ✅ `test_webhook_handles_missing_secret` : Secret manquant géré (200 ou 401)

**Tests Ledger** :
- ✅ `test_webhook_stores_net_amount_and_fees` : Net_amount et fees stockés correctement

### Exécution des Tests

```bash
# Tous les tests HelloAsso
pytest backend/finance/tests/test_helloasso_contract.py -v

# Tests spécifiques
pytest backend/finance/tests/test_helloasso_contract.py::TestHelloAssoIdempotence -v
```

---

## ⚠️ Limitations et Notes Importantes

### 1. Mode Simulé Uniquement

L'implémentation actuelle est en **mode simulé** uniquement :
- Pas d'appels réseau réels vers HelloAsso
- Tous les endpoints retournent des réponses mockées
- Adapté pour tests CI sans dépendance externe

**Mode Réel** : Non implémenté (TODO si nécessaire)

### 2. Sandbox HelloAsso

HelloAsso ne fournit pas de sandbox public exploitable en CI. L'implémentation utilise donc un **mode contractuel simulé** :
- Tests contractuels sur signature webhook + schéma payload + idempotence
- Smoke test manuel documenté (procédure) + validation via endpoint de réception
- Flag `HELLOASSO_SIMULATED_MODE=1` pour éviter réseau externe en CI

### 3. Frais Estimés

Si HelloAsso ne fournit pas les frais dans le webhook, une estimation est utilisée :
- ⚠️ Les frais réels peuvent différer légèrement
- ✅ L'estimation est basée sur les frais HelloAsso standards (0.8% + 0.25€)

### 4. Signature Webhook

La vérification de signature utilise `X-HelloAsso-Signature` avec HMAC-SHA256 :
- Format : `HMAC-SHA256(payload, HELLOASSO_WEBHOOK_SECRET)`
- En mode développement (secret manquant), accepte sans signature (warning log)

---

## 📊 Comparaison Stripe vs HelloAsso

| Caractéristique | Stripe | HelloAsso |
|----------------|--------|-----------|
| **Mode Test** | Sandbox public | Mode simulé (pas de sandbox) |
| **Signature** | `Stripe-Signature` (t=timestamp,v1=signature) | `X-HelloAsso-Signature` (HMAC-SHA256) |
| **Idempotence** | `event.id` + `payment_intent.id` | `event.id` + `payment.id` |
| **Frais** | Extrait depuis `balance_transaction.fee` | Estimé si non fourni (0.8% + 0.25€) |
| **Format Montant** | Centimes | Centimes |
| **Reçu Fiscal** | Non | Oui (association loi 1901) |

---

## 🔄 Intégration avec Ledgers

HelloAsso utilise la même logique de Ledger que Stripe :
- `allocate_payment_to_ledgers()` : Répartition proportionnelle des frais
- `PROJECT_ESCROW` : Donation net (après frais)
- `OPERATING` : Tip net (après frais)
- Garantie : `Sum(Net) + Sum(Fees) = Total Payment`

---

## 📚 Références

- **Code Source** :
  - `backend/finance/helloasso_client.py` : Client HelloAsso
  - `backend/finance/ledger_services/helloasso_ledger.py` : Service Ledger
  - `backend/finance/views.py` : Endpoints API

- **Tests** : `backend/finance/tests/test_helloasso_contract.py`
- **Configuration** : `backend/config/settings.py` (lignes 536-542)
- **Routes** : `backend/core/urls.py` (lignes 112-113)

---

## 🔔 Support Multi-Providers

EGOEJO supporte **plusieurs providers de paiement** :
- **Stripe** : Paiement international, cartes bancaires
- **HelloAsso** : Association loi 1901, reçu fiscal

**Garanties** :
- ✅ Tests contractuels pour chaque provider
- ✅ Traçabilité totale (audit logs)
- ✅ Non-convertibilité SAKA/EUR (séparation stricte)
- ✅ Transparence des frais (nets après frais mentionnés)

---

**Statut** : ✅ **OPÉRATIONNEL (Mode Simulé)**  
**Dernière Mise à Jour** : 2025-01-27

