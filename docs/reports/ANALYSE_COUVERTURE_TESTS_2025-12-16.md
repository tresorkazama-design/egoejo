# 🔍 Analyse Couverture Tests - EGOEJO

**Date** : 2025-12-16  
**Objectif** : Comprendre comment le projet est réellement testé (backend + frontend)

---

## 🔧 Configuration Tests

### Backend

**Fichier** : `backend/pytest.ini`

**Configuration** :
- Framework : pytest avec Django
- Coverage : `--cov=core` avec rapports `term-missing` et `html`
- Fichiers de tests : `tests.py`, `test_*.py`, `*_tests.py`
- Classes : `Test*`
- Fonctions : `test_*`

**Fichiers de Tests Identifiés** :
- `backend/core/tests.py` : Tests principaux (26 tests)
- `backend/core/tests_saka.py` : Tests SAKA (27 tests)
- `backend/investment/tests.py` : Vide (pas de tests)
- `backend/scripts/test_audio_generation.py` : Script utilitaire
- `backend/TEST_SECURITE.py` : Script de sécurité

**Total Backend** : **~53 tests** (26 + 27)

---

### Frontend

**Fichier** : `frontend/frontend/package.json`

**Scripts de Tests** :
- `npm test` : Vitest (watch mode)
- `npm run test:run` : Vitest (one-shot)
- `npm run test:coverage` : Couverture de code
- `npm run test:e2e` : Playwright E2E
- `npm run test:e2e:ui` : Playwright UI
- `npm run test:a11y` : Tests accessibilité
- `npm run test:integration` : Tests intégration backend
- `npm run test:performance` : Tests performance
- `npm run test:lighthouse` : Audit Lighthouse

**Fichiers de Tests Identifiés** :
- **Vitest** : 51 fichiers de tests dans `src/`
- **Playwright E2E** : 6 fichiers dans `e2e/`

**Total Frontend** : **~53 tests Vitest** + **~6 suites E2E Playwright**

---

## 📊 Backend - Détail des Tests

### `backend/core/tests.py` (26 tests)

#### 1. **IntentTestCase** (16 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_create_intent_success` : Création intention réussie
- `test_create_intent_missing_fields` : Validation champs requis
- `test_create_intent_invalid_email` : Validation email
- `test_create_intent_message_too_long` : Limite longueur message
- `test_create_intent_honeypot` : Protection anti-spam
- `test_admin_data_without_token` : Accès admin sans token
- `test_admin_data_with_invalid_token` : Token invalide
- `test_admin_data_with_valid_token` : Accès admin avec token
- `test_admin_data_with_filters` : Filtres admin (profil, dates)
- `test_admin_data_with_search` : Recherche admin
- `test_delete_intent_without_token` : Suppression sans token
- `test_delete_intent_with_valid_token` : Suppression avec token
- `test_delete_intent_not_found` : Suppression intention inexistante
- `test_export_intents_without_token` : Export sans token
- `test_export_intents_with_valid_token` : Export avec token

**Modules Testés** :
- ✅ `core/models/intents.py` (Intent)
- ✅ `core/api/intents.py` (rejoindre, admin_data, delete, export)

---

#### 2. **ProjetCagnotteTestCase** (2 tests)
**Couverture** : ⚠️ **Peu couvert**

**Tests** :
- `test_create_projet` : Création projet
- `test_create_cagnotte` : Création cagnotte

**Modules Testés** :
- ✅ `core/models/projects.py` (Projet)
- ✅ `core/models/fundraising.py` (Cagnotte)

**Manque** :
- ❌ API projets (`core/api/projects.py`) : Pas de tests pour `POST /api/projets/`, `GET /api/projets/`, `POST /api/projets/<id>/boost/`
- ❌ Relations Projet ↔ Cagnotte ↔ Contribution
- ❌ Propriétés calculées (`donation_current`, `investment_current`)

---

#### 3. **ProjectImpact4PTestCase** (6 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_create_project_impact_4p` : Création ProjectImpact4P
- `test_update_project_4p_service` : Service update_project_4p
- `test_update_project_4p_with_contributions` : Calcul avec contributions
- `test_update_project_4p_with_saka` : Calcul avec SAKA
- `test_api_projet_returns_impact_4p` : API retourne impact_4p
- `test_api_projet_returns_default_impact_4p_if_not_calculated` : Valeurs par défaut

**Modules Testés** :
- ✅ `core/models/impact.py` (ProjectImpact4P)
- ✅ `core/services/impact_4p.py` (update_project_4p)
- ✅ `core/api/projects.py` (exposition API)

---

#### 4. **MessagingVoteTestCase** (2 tests)
**Couverture** : ⚠️ **Peu couvert**

**Tests** :
- `test_chat_thread_creation_and_message_flow` : Création thread + messages
- `test_poll_lifecycle_and_votes` : Cycle de vie sondage + votes

**Modules Testés** :
- ✅ `core/models/chat.py` (ChatThread, ChatMessage)
- ✅ `core/api/chat.py` (API chat)
- ✅ `core/models/polls.py` (Poll, PollOption, PollBallot)
- ✅ `core/api/polls.py` (API polls)

**Manque** :
- ❌ Vote quadratique avec boost SAKA (testé dans `tests_saka.py` mais pas ici)
- ❌ Vote jugement majoritaire
- ❌ Vote actionnaire (V2.0)
- ❌ WebSocket pour votes temps réel

---

#### 5. **GlobalAssetsTestCase** (1 test)
**Couverture** : ⚠️ **Peu couvert**

**Tests** :
- `test_global_assets_endpoint` : Endpoint `/api/impact/global-assets/`

**Modules Testés** :
- ✅ `core/api/impact_views.py` (GlobalAssetsView)

**Manque** :
- ❌ ImpactDashboard (métriques utilisateur)
- ❌ Calculs de patrimoine (liquidités, pockets, equity)
- ❌ Intégration avec SAKA (testé dans `tests_saka.py`)

---

### `backend/core/tests_saka.py` (27 tests)

#### 1. **SakaWalletTestCase** (2 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_wallet_created_automatically` : Création automatique wallet
- `test_wallet_get_or_create` : Get or create wallet

**Modules Testés** :
- ✅ `core/models/saka.py` (SakaWallet)
- ✅ `core/services/saka.py` (get_or_create_wallet)

---

#### 2. **SakaHarvestTestCase** (5 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_harvest_content_read` : Récolte lecture contenu
- `test_harvest_poll_vote` : Récolte vote sondage
- `test_harvest_daily_limit` : Limite quotidienne anti-farming
- `test_harvest_disabled` : SAKA désactivé

**Modules Testés** :
- ✅ `core/services/saka.py` (harvest_saka)
- ✅ `core/models/saka.py` (SakaTransaction, SakaWallet)

---

#### 3. **SakaSpendTestCase** (3 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_spend_saka_success` : Dépense SAKA réussie
- `test_spend_insufficient_balance` : Solde insuffisant
- `test_spend_disabled` : SAKA désactivé

**Modules Testés** :
- ✅ `core/services/saka.py` (spend_saka)
- ✅ `core/models/saka.py` (SakaTransaction, SakaWallet)

---

#### 4. **SakaVoteQuadraticTestCase** (2 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_vote_with_saka_boost` : Vote quadratique avec boost SAKA
- `test_vote_without_saka` : Vote quadratique sans SAKA

**Modules Testés** :
- ✅ `core/api/polls.py` (vote avec SAKA)
- ✅ `core/models/polls.py` (PollBallot avec saka_spent, weight)
- ✅ `core/services/saka.py` (spend_saka)

---

#### 5. **SakaProjectBoostTestCase** (3 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_boost_project_success` : Boost projet réussi
- `test_boost_project_insufficient_balance` : Solde insuffisant
- `test_boost_project_disabled` : SAKA désactivé

**Modules Testés** :
- ✅ `core/api/projects.py` (boost_project)
- ✅ `core/models/saka.py` (SakaProjectSupport)
- ✅ `core/models/projects.py` (Projet.saka_score)

---

#### 6. **SakaGlobalAssetsTestCase** (2 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_global_assets_includes_saka` : Assets globaux incluent SAKA
- `test_global_assets_saka_disabled` : SAKA désactivé

**Modules Testés** :
- ✅ `core/api/impact_views.py` (GlobalAssetsView avec SAKA)

---

#### 7. **SakaRaceConditionTestCase** (3 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_concurrent_spend_saka_no_negative_balance` : Concurrence dépense SAKA
- `test_concurrent_boost_project_consistent_score` : Concurrence boost projet
- `test_daily_limit_respected_under_load` : Limite quotidienne sous charge

**Modules Testés** :
- ✅ `core/services/saka.py` (sécurité concurrence)
- ✅ `core/api/projects.py` (sécurité boost)

---

#### 8. **SakaConcurrencyTestCase** (1 test)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_concurrent_boost_double_spend_prevention` : Prévention double dépense (TransactionTestCase)

**Modules Testés** :
- ✅ `core/api/projects.py` (sécurité concurrence boost)
- ✅ `core/services/saka.py` (verrous pessimistes)

---

#### 9. **SakaCycleTestCase** (6 tests)
**Couverture** : ✅ **Bien couvert**

**Tests** :
- `test_create_saka_cycle` : Création cycle SAKA
- `test_get_cycle_stats_empty` : Stats cycle vide
- `test_get_cycle_stats_with_transactions` : Stats avec transactions
- `test_get_cycle_stats_with_compost_log` : Stats avec compost
- `test_api_saka_cycles_endpoint` : Endpoint `/api/saka/cycles/`
- `test_api_saka_cycles_with_transactions` : API avec transactions

**Modules Testés** :
- ✅ `core/models/saka.py` (SakaCycle, SakaCompostLog)
- ✅ `core/services/saka_stats.py` (get_cycle_stats)
- ✅ `core/api/saka_views.py` (saka_cycles_view)

---

### Modules Backend **NON Testés** ❌

**API Endpoints** :
- ❌ `core/api/auth_views.py` : Authentification (login, register, refresh)
- ❌ `core/api/content_views.py` : Contenus éducatifs
- ❌ `core/api/engagement_views.py` : Engagements
- ❌ `core/api/fundraising.py` : Cagnottes (endpoint désactivé mais pas testé)
- ❌ `core/api/help_views.py` : Aide
- ❌ `core/api/monitoring_views.py` : Monitoring
- ❌ `core/api/mycelium_views.py` : Mycelium 3D
- ❌ `core/api/search_views.py` : Recherche
- ❌ `core/api/semantic_search_views.py` : Recherche sémantique
- ❌ `core/api/security_views.py` : Sécurité
- ❌ `core/api/token_views.py` : Tokens
- ❌ `core/api/gdpr_views.py` : GDPR
- ❌ `core/api/moderation.py` : Modération
- ❌ `core/api/audit.py` : Audit
- ❌ `core/api/rate_limiting.py` : Rate limiting
- ❌ `core/api/chat_support.py` : Support concierge
- ❌ `core/api/config_views.py` : Configuration (feature flags)

**Services** :
- ❌ `core/services/concierge.py` : Support concierge
- ❌ `core/services/saka_stats.py` : Stats SAKA (partiellement testé via cycles)

**Modèles** :
- ❌ `core/models/accounts.py` : Profile
- ❌ `core/models/content.py` : EducationalContent
- ❌ `core/models/engagement.py` : Engagement
- ❌ `core/models/help.py` : HelpRequest
- ❌ `core/models/monitoring.py` : MonitoringAlert, PerformanceMetric
- ❌ `core/models/moderation.py` : Moderation
- ❌ `core/models/audit.py` : AuditLog
- ❌ `finance/models.py` : EscrowContract, WalletTransaction, etc.
- ❌ `investment/models.py` : ShareholderRegister, etc.

**Tâches Celery** :
- ❌ `core/tasks.py` : Tâches générales
- ❌ `core/tasks_audio.py` : Génération audio
- ❌ `core/tasks_embeddings.py` : Génération embeddings
- ❌ `core/tasks_mycelium.py` : Mycelium
- ❌ `core/tasks_security.py` : Scan antivirus

---

## 🎨 Frontend - Détail des Tests

### Tests Vitest (Unitaires) - 51 fichiers

#### Pages Testées ✅ (12/23 pages)

**Pages avec Tests** :
- ✅ `Home.test.jsx` : Page d'accueil
- ✅ `Projets.test.jsx` : Page projets
- ✅ `Votes.test.jsx` : Page votes
- ✅ `Admin.test.jsx` : Page admin
- ✅ `Rejoindre.test.jsx` : Formulaire rejoindre
- ✅ `Chat.test.jsx` : Page chat
- ✅ `Alliances.test.jsx` : Page alliances
- ✅ `Communaute.test.jsx` : Page communauté
- ✅ `Contenus.test.jsx` : Page contenus
- ✅ `Vision.test.jsx` : Page vision
- ✅ `Univers.test.jsx` : Page univers
- ✅ `NotFound.test.jsx` : Page 404

**Pages SANS Tests** ❌ (11/23 pages) :
- ❌ `Dashboard.jsx` : Dashboard utilisateur
- ❌ `Impact.jsx` : Impact utilisateur
- ❌ `MyCard.jsx` : Carte utilisateur
- ❌ `Login.jsx` : Connexion
- ❌ `Register.jsx` : Inscription
- ❌ `SakaMonitor.jsx` : Monitoring SAKA (admin)
- ❌ `SakaSilo.jsx` : Silo Commun SAKA
- ❌ `Mycelium.jsx` : Visualisation 3D
- ❌ `Podcast.jsx` : Podcasts
- ❌ `Citations.jsx` : Citations
- ❌ `RacinesPhilosophie.jsx` : Racines philosophie

---

#### Composants Testés ✅ (12 composants)

**Composants avec Tests** :
- ✅ `Button.test.jsx` : Bouton
- ✅ `Input.test.jsx` : Input
- ✅ `Layout.test.jsx` : Layout global
- ✅ `Navbar.test.jsx` : Navigation
- ✅ `Loader.test.jsx` : Indicateur chargement
- ✅ `ErrorBoundary.test.jsx` : Gestion erreurs
- ✅ `ChatWindow.test.jsx` : Fenêtre chat
- ✅ `ChatList.test.jsx` : Liste chat
- ✅ `CustomCursor.test.jsx` : Curseur personnalisé
- ✅ `FullscreenMenu.test.jsx` : Menu plein écran
- ✅ `FourPStrip.test.jsx` : Bandeau 4P
- ✅ `SakaSeasonBadge.test.jsx` : Badge saison SAKA

**Composants SANS Tests** ❌ :
- ❌ `AudioPlayer.jsx` : Lecteur audio
- ❌ `CardTilt.jsx` : Carte avec effet tilt
- ❌ `SupportBubble.jsx` : Support concierge
- ❌ `QuadraticVote.jsx` : Vote quadratique
- ❌ `SemanticSearch.jsx` : Recherche sémantique
- ❌ `SemanticSuggestions.jsx` : Suggestions sémantiques
- ❌ `MyceliumVisualization.jsx` : Visualisation 3D
- ❌ `Logo3D.jsx` : Logo 3D
- ❌ `MenuCube3D.jsx` : Menu cube 3D
- ❌ `HeroSorgho.jsx` : Hero sections
- ❌ `PageTransition.jsx` : Transitions pages
- ❌ `ScrollProgress.jsx` : Barre progression scroll
- ❌ `OptimizedImage.jsx` : Image optimisée
- ❌ `Notification.jsx` : Notifications
- ❌ `NotificationContainer.jsx` : Container notifications
- ❌ `EcoModeToggle.jsx` : Toggle mode éco
- ❌ `OfflineIndicator.jsx` : Indicateur offline
- ❌ `LanguageSelector.jsx` : Sélecteur langue
- ❌ `SEO.jsx` : SEO
- ❌ `PageViewTracker.jsx` : Tracking vues
- ❌ `CursorSpotlight.jsx` : Curseur spotlight
- ❌ `SwipeButton.jsx` : Bouton swipe

---

#### Hooks Testés ✅ (6 hooks)

**Hooks avec Tests** :
- ✅ `useFetch.test.js` : Hook fetch
- ✅ `useDebounce.test.js` : Debounce
- ✅ `useLocalStorage.test.js` : LocalStorage
- ✅ `useMediaQuery.test.js` : Media queries
- ✅ `useToggle.test.js` : Toggle
- ✅ `useClickOutside.test.jsx` : Clic extérieur

**Hooks SANS Tests** ❌ :
- ❌ `useGlobalAssets.js` : Assets globaux
- ❌ `useSaka.js` : Hooks SAKA (useSakaSilo, useSakaCompostPreview, etc.)
- ❌ `useWebSocket.js` : WebSocket
- ❌ `useEasterEgg.js` : Easter egg
- ❌ `useSEO.js` : SEO
- ❌ `useNotification.js` : Notifications
- ❌ `useLowPowerMode.js` : Mode faible consommation

---

#### Contextes Testés ✅ (1 contexte)

**Contextes avec Tests** :
- ✅ `AuthContext.test.jsx` : Authentification

**Contextes SANS Tests** ❌ :
- ❌ `LanguageContext.jsx` : Internationalisation
- ❌ `NotificationContext.jsx` : Notifications
- ❌ `EcoModeContext.jsx` : Mode éco

---

#### Utils Testés ✅ (6 utils)

**Utils avec Tests** :
- ✅ `api.test.js` : API fetch
- ✅ `format.test.js` : Formatage
- ✅ `validation.test.js` : Validation
- ✅ `backend-connection.test.js` : Connexion backend
- ✅ `integration-backend.test.js` : Intégration backend
- ✅ `performance.test.js` : Performance
- ✅ `security.test.js` : Sécurité

**Utils SANS Tests** ❌ :
- ❌ `analytics.js` : Analytics
- ❌ `logger.js` : Logger
- ❌ `monitoring.js` : Monitoring
- ❌ `performance-metrics.js` : Métriques performance
- ❌ `scrollAnimations.js` : Animations scroll
- ❌ `gdpr.js` : GDPR
- ❌ `i18n.js` : Internationalisation
- ❌ `money.js` : Formatage monétaire
- ❌ `sentry.js` : Sentry

---

#### Tests Spécialisés ✅

**Accessibilité** (5 tests) :
- ✅ `aria.test.jsx` : ARIA
- ✅ `contrast.test.jsx` : Contraste
- ✅ `keyboard.test.jsx` : Navigation clavier
- ✅ `enhanced.test.jsx` : Tests avancés
- ✅ `accessibility.test.jsx` : Tests généraux

**Performance** (3 tests) :
- ✅ `metrics.test.js` : Métriques
- ✅ `automated.test.js` : Tests automatisés
- ✅ `lighthouse.test.js` : Lighthouse

**Intégration** (2 tests) :
- ✅ `api.test.jsx` : API
- ✅ `chat-integration.test.jsx` : Chat
- ✅ `router.test.jsx` : Router
- ✅ `navigation.test.jsx` : Navigation

---

### Tests Playwright E2E (6 fichiers)

**Pages E2E Testées** ✅ :
- ✅ `home.spec.js` : Page d'accueil (chargement, navigation)
- ✅ `admin.spec.js` : Page admin (intentions, filtres, export)
- ✅ `contenus.spec.js` : Page contenus (chargement, contenu)
- ✅ `rejoindre.spec.js` : Formulaire rejoindre (validation, soumission)
- ✅ `navigation.spec.js` : Navigation entre pages
- ✅ `backend-connection.spec.js` : Connexion backend (API projets, chat)

**Pages E2E SANS Tests** ❌ :
- ❌ `Dashboard.spec.js` : Dashboard utilisateur
- ❌ `Projets.spec.js` : Page projets (liste, détail, boost SAKA)
- ❌ `Votes.spec.js` : Page votes (vote binaire, quadratique)
- ❌ `SakaMonitor.spec.js` : Monitoring SAKA
- ❌ `SakaSilo.spec.js` : Silo Commun SAKA
- ❌ `Chat.spec.js` : Chat temps réel
- ❌ `Login.spec.js` : Connexion
- ❌ `Register.spec.js` : Inscription
- ❌ `Impact.spec.js` : Impact utilisateur

---

## 📊 Matrice de Couverture

### Backend : Couvert / Peu Couvert / Pas Testé

| Module | Statut | Détails |
|--------|--------|---------|
| **Intent** | ✅ **Couvert** | 16 tests (création, admin, export, suppression) |
| **SAKA** | ✅ **Couvert** | 27 tests (wallet, récolte, dépense, boost, cycles, concurrence) |
| **ProjectImpact4P** | ✅ **Couvert** | 6 tests (création, service, API) |
| **Projet** | ⚠️ **Peu Couvert** | 2 tests (création seulement, pas d'API) |
| **Cagnotte** | ⚠️ **Peu Couvert** | 1 test (création seulement) |
| **Poll** | ⚠️ **Peu Couvert** | 1 test (cycle de vie basique, pas de vote quadratique/majoritaire) |
| **Chat** | ⚠️ **Peu Couvert** | 1 test (thread + messages basiques) |
| **GlobalAssets** | ⚠️ **Peu Couvert** | 1 test (endpoint basique) |
| **Auth** | ❌ **Pas Testé** | Login, register, refresh token |
| **Content** | ❌ **Pas Testé** | EducationalContent, API |
| **Engagement** | ❌ **Pas Testé** | Engagement, API |
| **Fundraising** | ❌ **Pas Testé** | Contribution, API (endpoint désactivé) |
| **Help** | ❌ **Pas Testé** | HelpRequest, API |
| **Monitoring** | ❌ **Pas Testé** | MonitoringAlert, PerformanceMetric, API |
| **Mycelium** | ❌ **Pas Testé** | API 3D |
| **Search** | ❌ **Pas Testé** | Recherche, recherche sémantique |
| **Security** | ❌ **Pas Testé** | API sécurité |
| **GDPR** | ❌ **Pas Testé** | API GDPR |
| **Moderation** | ❌ **Pas Testé** | Modération, API |
| **Audit** | ❌ **Pas Testé** | AuditLog, API |
| **Rate Limiting** | ❌ **Pas Testé** | Rate limiting |
| **Chat Support** | ❌ **Pas Testé** | Support concierge |
| **Config** | ❌ **Pas Testé** | Feature flags |
| **Finance** | ❌ **Pas Testé** | EscrowContract, WalletTransaction |
| **Investment** | ❌ **Pas Testé** | ShareholderRegister (V2.0) |
| **Celery Tasks** | ❌ **Pas Testé** | Tâches asynchrones |

---

### Frontend : Couvert / Peu Couvert / Pas Testé

| Module | Statut | Détails |
|--------|--------|---------|
| **Pages Publiques** | ✅ **Couvert** | 12/23 pages testées (Home, Projets, Votes, Admin, Rejoindre, Chat, etc.) |
| **Pages Utilisateur** | ❌ **Pas Testé** | Dashboard, Impact, MyCard, Login, Register |
| **Pages SAKA** | ❌ **Pas Testé** | SakaMonitor, SakaSilo |
| **Pages 3D** | ❌ **Pas Testé** | Mycelium |
| **Composants UI** | ✅ **Couvert** | 12/30+ composants testés (Button, Input, Layout, Navbar, etc.) |
| **Composants SAKA** | ✅ **Couvert** | FourPStrip, SakaSeasonBadge |
| **Composants 3D** | ❌ **Pas Testé** | Logo3D, MenuCube3D, MyceliumVisualization |
| **Composants Chat** | ✅ **Couvert** | ChatWindow, ChatList |
| **Hooks API** | ⚠️ **Peu Couvert** | 6/13 hooks testés (manque useGlobalAssets, useSaka, useWebSocket) |
| **Contextes** | ⚠️ **Peu Couvert** | 1/4 contextes testés (AuthContext seulement) |
| **Utils** | ✅ **Couvert** | 7/15 utils testés (api, format, validation, security, etc.) |
| **Accessibilité** | ✅ **Couvert** | 5 tests a11y |
| **Performance** | ✅ **Couvert** | 3 tests performance |
| **E2E Playwright** | ⚠️ **Peu Couvert** | 6/23 pages testées (manque Dashboard, Projets, Votes, SAKA, Chat) |

---

## 🎯 Conclusion

### Backend

**Points Forts** ✅ :
- **SAKA** : Très bien couvert (27 tests, tous les aspects)
- **Intent** : Bien couvert (16 tests, CRUD complet)
- **ProjectImpact4P** : Bien couvert (6 tests)
- **Sécurité concurrence** : Tests robustes (race conditions, double dépense)

**Points Faibles** ⚠️ :
- **API Projets** : Peu testé (création seulement, pas de boost SAKA dans tests.py)
- **API Polls** : Peu testé (cycle de vie basique, pas de vote quadratique/majoritaire dans tests.py)
- **API Chat** : Peu testé (thread + messages basiques)
- **API Auth** : Pas testé (login, register, refresh)
- **Services** : Concierge, saka_stats partiellement
- **Tâches Celery** : Aucune tâche testée
- **Finance/Investment** : Pas testé (EscrowContract, ShareholderRegister)

**Total** : **~53 tests** pour **~24 endpoints API** = **~2.2 tests/endpoint** (mais très concentré sur SAKA et Intent)

---

### Frontend

**Points Forts** ✅ :
- **Pages publiques** : Bien couvertes (12/23)
- **Composants UI de base** : Bien couverts (Button, Input, Layout, Navbar)
- **Accessibilité** : 5 tests a11y
- **Performance** : 3 tests performance
- **Intégration** : Tests router, navigation, API

**Points Faibles** ⚠️ :
- **Pages utilisateur** : Pas testées (Dashboard, Impact, MyCard, Login, Register)
- **Pages SAKA** : Pas testées (SakaMonitor, SakaSilo)
- **Hooks SAKA** : Pas testés (useSakaSilo, useSakaCompostPreview, etc.)
- **Hooks API** : Peu testés (useGlobalAssets, useWebSocket)
- **Contextes** : Peu testés (LanguageContext, NotificationContext, EcoModeContext)
- **E2E** : Peu couvert (6/23 pages, manque Dashboard, Projets, Votes, SAKA)

**Total** : **~53 tests Vitest** + **~6 suites E2E** pour **23 pages** + **30+ composants** = **Couverture partielle**

---

### "Promesse Tests OK" vs Réalité

**Réalité** :
- ✅ **SAKA** : Très bien testé (backend + frontend partiel)
- ✅ **Intent** : Bien testé (backend + frontend)
- ⚠️ **Projets** : Peu testé (backend API manquante, frontend E2E manquante)
- ⚠️ **Votes** : Peu testé (backend API partielle, frontend E2E manquante)
- ❌ **Auth** : Pas testé (backend + frontend)
- ❌ **Chat** : Peu testé (backend basique, frontend E2E manquante)
- ❌ **Dashboard/Impact** : Pas testé (frontend)
- ❌ **SAKA Monitoring** : Pas testé (frontend E2E)

**Verdict** : **Tests concentrés sur SAKA et Intent**, mais **beaucoup de modules non testés** (Auth, Content, Engagement, Finance, Investment, Celery, etc.)

---

**Dernière mise à jour** : 2025-12-16

