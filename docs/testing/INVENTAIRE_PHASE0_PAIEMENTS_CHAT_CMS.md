# 📋 PHASE 0 - INVENTAIRE COMPLET (Paiements, Chat, CMS)

**Date** : 2025-01-XX  
**Objectif** : Inventorier l'existant avant d'ajouter les tests manquants

---

## 🎯 RÉSUMÉ EXÉCUTIF

| Feature | État | Tests Existants | Gaps P0 | Gaps P1 |
|---------|------|-----------------|---------|---------|
| **Stripe Payments** | ⚠️ **PARTIEL** | Unit/Integration | E2E réel, Contract, Signature | Checkout session endpoint |
| **HelloAsso** | ❌ **MANQUE** | Aucun | Tout | - |
| **WebSocket Chat** | ✅ **EXISTE** | Unit frontend | E2E réel, Integration backend | Modération, anti-abus |
| **CMS Workflow** | ✅ **EXISTE** | Permissions, Workflow | E2E complet, Export, Versioning | Audit log complet |

---

## 1️⃣ STRIPE PAYMENTS

### A) Backend - Modules Existants

**Fichiers** :
- ✅ `backend/finance/views.py` : `StripeWebhookView` (ligne 158-302)
- ✅ `backend/finance/ledger_services/ledger.py` : `process_stripe_payment_webhook()` (ligne 357+)
- ✅ `backend/core/urls.py` : Route `/api/finance/stripe/webhook/` (ligne 109)

**Endpoints Existants** :
- ✅ `POST /api/finance/stripe/webhook/` : Webhook Stripe (existe)
- ❌ `POST /api/payments/stripe/checkout-session` : **MANQUE** (pas d'endpoint pour créer checkout session)
- ❌ `POST /api/payments/stripe/payment-intent` : **MANQUE** (pas d'endpoint pour créer payment intent)

**Fonctionnalités Implémentées** :
- ✅ Réception webhook `payment_intent.succeeded`
- ✅ Extraction frais Stripe depuis `balance_transaction.fee`
- ✅ Répartition proportionnelle frais (donation + tip)
- ✅ Stockage `amount_gross`, `stripe_fee`, `amount_net` dans `WalletTransaction`
- ✅ Allocation vers Ledgers (PROJECT_ESCROW, OPERATING)
- ⚠️ **Signature verification** : **PARTIEL** (commentaire ligne 168 : "à implémenter si nécessaire")
- ⚠️ **Idempotence** : **PARTIEL** (commentaire ligne 169 : "via idempotency_key", mais pas implémenté)

**Fonctionnalités Manquantes** :
- ❌ Endpoint création checkout session
- ❌ Endpoint création payment intent
- ❌ Vérification signature webhook (STRIPE_WEBHOOK_SECRET)
- ❌ Idempotence via `event.id` (locking transaction)
- ❌ AuditLog obligatoire (payment_created, payment_succeeded, webhook_received)
- ❌ Mode test strict (STRIPE_API_KEY test only en CI)

**Settings/Config** :
- ⚠️ `STRIPE_SECRET_KEY` : Utilisé dans `ledger.py` (ligne 300) mais pas vérifié si test/live
- ⚠️ `STRIPE_WEBHOOK_SECRET` : **MANQUE** (pas de vérification signature)
- ⚠️ `STRIPE_FIXED_FEE` : Défini dans `ledger.py` (ligne 23)
- ⚠️ `STRIPE_PERCENT_FEE` : Défini dans `ledger.py` (ligne 24)

### B) Tests Existants

**Fichiers** :
- ✅ `backend/finance/tests/test_stripe_segregation.py` : Tests répartition frais (466 lignes)
- ✅ `backend/finance/tests/test_ledger_fee_allocation.py` : Tests allocation frais

**Tests Inclus** :
- ✅ `test_stripe_segregation.py` :
  - `test_webhook_segregation_proportionnelle` : Répartition proportionnelle
  - `test_webhook_segregation_donation_100_pourcent` : 100% donation
  - `test_webhook_segregation_tip_100_pourcent` : 100% tip
  - `test_webhook_segregation_fees_egaux` : Frais égaux
  - `test_webhook_segregation_montants_egaux` : Montants égaux
  - `test_webhook_segregation_tip_minimal` : Tip minimal
  - `test_webhook_segregation_donation_minimal` : Donation minimal
  - `test_webhook_segregation_fees_zero` : Frais zéro
  - `test_webhook_segregation_integrity` : Intégrité (Net Projet + Net Asso + Frais = Total)

- ✅ `test_ledger_fee_allocation.py` :
  - Tests calcul répartition frais
  - Tests extraction frais depuis webhook
  - Tests allocation vers Ledgers

**Gaps Tests** :
- ❌ **Contract tests** : Pas de tests contract (schéma payload webhook)
- ❌ **Signature verification tests** : Pas de tests vérification signature
- ❌ **Idempotence tests** : Pas de tests idempotence (replay event)
- ❌ **E2E Playwright** : Pas de tests E2E paiement réel (checkout -> webhook -> UI)
- ❌ **AuditLog tests** : Pas de tests audit log obligatoire
- ❌ **Mode test tests** : Pas de tests mode test strict (refus clés live en CI)

### C) Frontend - Intégration Stripe

**Fichiers** :
- ⚠️ **À VÉRIFIER** : Recherche dans `frontend/frontend/src/` pour intégration Stripe Checkout

**Gaps Frontend** :
- ❌ Tests E2E Playwright paiement Stripe (checkout -> confirmation -> UI)

---

## 2️⃣ HELLOASSO

### A) Backend - Modules Existants

**Fichiers** :
- ❌ **AUCUN** : Pas de module HelloAsso

**Endpoints Existants** :
- ❌ `POST /api/payments/helloasso/start` : **MANQUE**
- ❌ `POST /api/payments/helloasso/webhook` : **MANQUE**

**Fonctionnalités Manquantes** :
- ❌ Client HelloAsso (OAuth token)
- ❌ Gestion token OAuth
- ❌ Webhook HelloAsso
- ❌ Validation signature (si mécanisme)
- ❌ Idempotence
- ❌ Audit log
- ❌ Stockage net_amount/frais

**Settings/Config** :
- ❌ `HELLOASSO_CLIENT_ID` : **MANQUE**
- ❌ `HELLOASSO_CLIENT_SECRET` : **MANQUE**
- ❌ `HELLOASSO_WEBHOOK_SECRET` : **MANQUE**
- ❌ `HELLOASSO_SANDBOX_ENABLED` : **MANQUE**

**Documentation HelloAsso Sandbox** :
- ⚠️ **À RECHERCHER** : HelloAsso fournit-il un sandbox public exploitable en CI ?
  - Si OUI : Implémenter tests E2E avec sandbox
  - Si NON : Mode contractuel simulé (tests contractuels + smoke test manuel documenté)

### B) Tests Existants

**Fichiers** :
- ❌ **AUCUN** : Pas de tests HelloAsso

**Gaps Tests** :
- ❌ **Tout** : Aucun test HelloAsso

---

## 3️⃣ WEBSOCKET CHAT

### A) Backend - Modules Existants

**Fichiers** :
- ✅ `backend/core/consumers.py` : `ChatConsumer` (ligne 7-52)
- ✅ `backend/core/routing.py` : Routes WebSocket (ligne 5-8)
- ✅ `backend/config/asgi.py` : Configuration ASGI (ligne 19-35)
- ✅ `backend/core/models/chat.py` : Modèles `ChatThread`, `ChatMessage`, `ChatMembership`

**Technologie** :
- ✅ **Django Channels** : Utilisé (`channels.generic.websocket.AsyncJsonWebsocketConsumer`)

**Routes WebSocket** :
- ✅ `ws://localhost:8000/ws/chat/<thread_id>/` : Chat temps réel (existe)
- ✅ `ws://localhost:8000/ws/polls/<poll_id>/` : Sondages temps réel (existe)

**Authentification** :
- ✅ **JWT via query param** : `ws://.../ws/chat/1/?token=<jwt_token>` (ligne 45 dans `useWebSocket.js`)
- ✅ **AuthMiddlewareStack** : Utilisé dans `asgi.py` (ligne 22)
- ✅ **Vérification anonyme** : `if user.is_anonymous: await self.close(code=4401)` (ligne 13-15)

**Rooms/Groups** :
- ✅ **Channel groups** : `chat_thread_{thread_id}` (ligne 10)
- ✅ **Membership check** : `_is_member()` vérifie si user est membre du thread (ligne 17-20)
- ✅ **Permissions** : Anonyme refusé (code 4401), non-membre refusé (code 4403)

**Persistence** :
- ✅ **DB** : Messages persistés dans `ChatMessage` (modèle existe)
- ✅ **Broadcast** : Via `channel_layer.group_send()` (ligne 37-46)

**Fonctionnalités Implémentées** :
- ✅ Connexion WebSocket avec auth JWT
- ✅ Rejoindre room (thread)
- ✅ Envoyer message (via API REST `POST /api/chat/messages/`)
- ✅ Recevoir message (broadcast via WebSocket)
- ✅ Typing indicator (ligne 36-46)
- ✅ Heartbeat ping/pong (ligne 32-34)

**Fonctionnalités Manquantes** :
- ⚠️ **Modération** : **PARTIEL** (modèle `ModerationReport` existe, mais pas de modération automatique chat)
- ⚠️ **Anti-abus** : **PARTIEL** (pas de rate-limit messages, pas de détection spam)
- ⚠️ **Audit log** : **PARTIEL** (pas de log obligatoire messages envoyés/reçus)
- ⚠️ **Communautés** : **PARTIEL** (threads existent, mais pas de mapping communauté -> channel group explicite)

### B) Tests Existants

**Fichiers Backend** :
- ❌ **AUCUN** : Pas de tests backend WebSocket (Channels testing)

**Fichiers Frontend** :
- ✅ `frontend/frontend/src/components/__tests__/ChatWindow.test.jsx` : Tests unitaires ChatWindow
- ✅ `frontend/frontend/src/app/pages/__tests__/Chat.test.jsx` : Tests unitaires Chat
- ✅ `frontend/frontend/src/app/__tests__/chat-integration.test.jsx` : Tests intégration chat

**Tests Inclus** :
- ✅ Tests unitaires frontend (mocks WebSocket)
- ⚠️ Tests intégration frontend (partiels, mocks)

**Gaps Tests** :
- ❌ **Unit backend** : Pas de tests permissions consumer (anon denied)
- ❌ **Integration backend** : Pas de tests client WS (Channels testing) connect/send/receive
- ❌ **E2E Playwright** : Pas de tests E2E WebSocket réel (login -> connect -> send -> receive -> broadcast)
- ❌ **Modération tests** : Pas de tests modération messages
- ❌ **Anti-abus tests** : Pas de tests rate-limit, spam detection

### C) Frontend - Intégration WebSocket

**Fichiers** :
- ✅ `frontend/frontend/src/hooks/useWebSocket.js` : Hook WebSocket (181 lignes)
- ✅ `frontend/frontend/src/components/ChatWindow.jsx` : Composant chat
- ✅ `frontend/frontend/src/components/ChatList.jsx` : Liste conversations

**Fonctionnalités Frontend** :
- ✅ Connexion WebSocket avec token JWT
- ✅ Reconnexion automatique (MAX_RECONNECT_ATTEMPTS = 5)
- ✅ Heartbeat ping/pong (30s)
- ✅ Gestion erreurs
- ✅ Typing indicator
- ✅ Messages temps réel

---

## 4️⃣ CMS WORKFLOW

### A) Backend - Modules Existants

**Fichiers** :
- ✅ `backend/core/api/content_views.py` : `EducationalContentViewSet` (ligne 19-600+)
- ✅ `backend/core/models/content.py` : Modèle `EducationalContent` (ligne 10+)
- ✅ `backend/core/tests/cms/test_content_permissions.py` : Tests permissions
- ✅ `backend/core/tests/cms/test_content_workflow_transitions.py` : Tests workflow

**Endpoints Existants** :
- ✅ `GET /api/contents/` : Liste contenus (public, cache 10min)
- ✅ `POST /api/contents/` : Créer contenu (status=pending, IsAuthenticated)
- ✅ `POST /api/contents/{id}/publish/` : Publier (status=published, CanPublishContent)
- ✅ `POST /api/contents/{id}/reject/` : Rejeter (status=rejected, CanRejectContent)
- ✅ `POST /api/contents/{id}/archive/` : Archiver (status=archived, CanArchiveContent)
- ✅ `POST /api/contents/{id}/unpublish/` : Dépublication (status=draft, CanUnpublishContent)
- ✅ `POST /api/contents/{id}/mark-consumed/` : Marquer consommé (récolte SAKA)

**Workflow Statuts** :
- ✅ `draft` : Brouillon
- ✅ `pending` : En attente de validation
- ✅ `published` : Publié
- ✅ `rejected` : Rejeté
- ✅ `archived` : Archivé

**Rôles & Permissions** :
- ✅ `CanPublishContent` : Editor/Admin uniquement
- ✅ `CanRejectContent` : Editor/Admin uniquement
- ✅ `CanArchiveContent` : Editor/Admin uniquement
- ✅ `CanUnpublishContent` : Editor/Admin uniquement
- ✅ `CanCreateContent` : IsAuthenticated (Contributor, Editor, Admin)

**Rôles Définis** :
- ⚠️ **Contributor** : Peut créer, ne peut pas publish/reject/archive (testé ligne 6 `test_content_permissions.py`)
- ⚠️ **Editor** : Peut créer, publish, reject, archive (testé ligne 7)
- ⚠️ **Reviewer** : **MANQUE** (pas de rôle Reviewer explicite, Editor fait office de Reviewer)
- ✅ **Admin** : Override + archive (testé)

**Versioning Minimal** :
- ✅ `created_by` : Auteur (ForeignKey User, nullable)
- ✅ `modified_by` : Dernier modificateur (ForeignKey User, nullable, ligne 142-149)
- ✅ `published_by` : Publieur (ForeignKey User, nullable, ligne 129-136)
- ✅ `created_at` : Date création (auto_now_add)
- ✅ `updated_at` : Date modification (auto_now)
- ✅ `published_at` : Date publication (DateTimeField, nullable, ligne 137-141)

**Audit Log** :
- ⚠️ **PARTIEL** : `AuditLog` existe (modèle), mais pas de log obligatoire sur toutes transitions
- ⚠️ **Logging** : Logging présent dans `content_views.py` (ligne 420+), mais pas de modèle `AuditLog` pour CMS spécifiquement

**Export** :
- ❌ **JSON** : **MANQUE** (pas d'endpoint export JSON)
- ❌ **CSV** : **MANQUE** (pas d'endpoint export CSV)

**Fonctionnalités Manquantes** :
- ⚠️ **Rôle Reviewer** : Pas de rôle Reviewer explicite (Editor fait office)
- ❌ **Export JSON/CSV** : Pas d'endpoints export
- ⚠️ **Audit log complet** : Pas de log obligatoire toutes transitions (create/update/publish/reject/archive/delete)
- ❌ **XSS sanitization** : Pas de tests sanitization description/content (si rendu HTML)
- ❌ **Pagination obligatoire** : Pas de tests pagination (ne doit pas charger "tout")

### B) Tests Existants

**Fichiers** :
- ✅ `backend/core/tests/cms/test_content_permissions.py` : Tests permissions (6 tests, ligne 103-342)
- ✅ `backend/core/tests/cms/test_content_workflow_transitions.py` : Tests workflow

**Tests Inclus** :
- ✅ `test_content_permissions.py` :
  - `test_anonymous_cannot_publish` : Anonyme ne peut pas publier
  - `test_contributor_cannot_publish` : Contributor ne peut pas publier
  - `test_editor_can_publish` : Editor peut publier
  - `test_admin_can_publish` : Admin peut publier
  - `test_anonymous_cannot_reject` : Anonyme ne peut pas rejeter
  - `test_contributor_cannot_reject` : Contributor ne peut pas rejeter
  - `test_editor_can_reject` : Editor peut rejeter
  - `test_admin_can_reject` : Admin peut rejeter
  - `test_anonymous_cannot_archive` : Anonyme ne peut pas archiver
  - `test_contributor_cannot_archive` : Contributor ne peut pas archiver
  - `test_editor_can_archive` : Editor peut archiver
  - `test_admin_can_archive` : Admin peut archiver
  - `test_anonymous_cannot_unpublish` : Anonyme ne peut pas dépublication
  - `test_contributor_cannot_unpublish` : Contributor ne peut pas dépublication
  - `test_editor_can_unpublish` : Editor peut dépublication
  - `test_admin_can_unpublish` : Admin peut dépublication

- ✅ `test_content_workflow_transitions.py` : Tests transitions workflow

**Gaps Tests** :
- ❌ **E2E complet** : Pas de tests E2E workflow complet (Contributor crée -> Editor soumet -> Reviewer publish -> Archive -> Export)
- ❌ **XSS tests** : Pas de tests sanitization description/content
- ❌ **Pagination tests** : Pas de tests pagination (ne doit pas charger "tout")
- ❌ **Export tests** : Pas de tests export JSON/CSV
- ❌ **Audit log tests** : Pas de tests audit log obligatoire toutes transitions
- ❌ **Versioning tests** : Pas de tests versioning (modified_by/published_by timestamps)

---

## 📊 TABLEAU RÉCAPITULATIF

| Feature | État | Fichiers Existants | Tests Existants | Gaps P0 | Gaps P1 |
|---------|------|-------------------|-----------------|---------|---------|
| **Stripe Webhook** | ✅ EXISTE | `finance/views.py`, `ledger_services/ledger.py` | `test_stripe_segregation.py`, `test_ledger_fee_allocation.py` | E2E réel, Contract, Signature, Idempotence | Checkout session endpoint |
| **Stripe Checkout** | ❌ MANQUE | Aucun | Aucun | Endpoint création checkout session | - |
| **HelloAsso** | ❌ MANQUE | Aucun | Aucun | Tout (client, webhook, tests) | - |
| **WebSocket Chat** | ✅ EXISTE | `consumers.py`, `routing.py`, `asgi.py` | Tests unitaires frontend (mocks) | E2E réel, Integration backend | Modération, anti-abus |
| **CMS Workflow** | ✅ EXISTE | `content_views.py`, `content.py` | `test_content_permissions.py`, `test_content_workflow_transitions.py` | E2E complet, Export, XSS, Pagination | Audit log complet, Versioning tests |
| **CMS Rôles** | ⚠️ PARTIEL | Permissions définies | Tests permissions | Rôle Reviewer explicite | - |
| **CMS Export** | ❌ MANQUE | Aucun | Aucun | Endpoints export JSON/CSV | - |

---

## ✅ PROCHAINES ÉTAPES

1. **PHASE 1** : Stripe Payments (mode test) - E2E réel + Contract + Signature
2. **PHASE 2** : HelloAsso (sandbox ou contractuel simulé)
3. **PHASE 3** : WebSocket Chat - E2E réel + Integration backend
4. **PHASE 4** : CMS Complet - E2E complet + Export + XSS + Pagination
5. **PHASE 5** : Wiring CI + Docs

---

## 📝 NOTES

- **Stripe** : Webhook existe mais manque endpoint création checkout session + vérification signature
- **HelloAsso** : À vérifier si sandbox public disponible, sinon mode contractuel simulé
- **WebSocket** : Backend existe, manque tests E2E réel + integration backend
- **CMS** : Workflow existe, manque E2E complet + export + tests XSS/pagination

