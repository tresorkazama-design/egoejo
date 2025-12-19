# 📦 Vue d'Ensemble du Code EGOEJO

[![EGOEJO Compliant](https://github.com/YOUR_OWNER/YOUR_REPO/actions/workflows/egoejo-guardian.yml/badge.svg)](https://github.com/YOUR_OWNER/YOUR_REPO/actions/workflows/egoejo-guardian.yml)

> **Ce badge atteste du respect des règles EGOEJO. Il n'atteste ni d'un rendement financier, ni d'une performance économique.**

[Documentation du badge](../compliance/EGOEJO_COMPLIANT.md)

**Version** : 2.1 (Hybride V1.6 + V2.0)  
**Date** : 2025-01-16  
**Statut** : Production Ready ✅  
**Architecture** : Monolithe Modulaire (Backend Django + Frontend React)

---

## 🏗️ Architecture Globale

```
egoejo/
├── backend/                    # API Django REST Framework
│   ├── config/                 # Configuration Django (settings, urls, asgi, celery)
│   ├── core/                   # Application principale (modèles, API, services, tests)
│   ├── finance/                # Système financier (Escrow, Wallets, Transactions)
│   ├── investment/             # Investissement (V2.0 dormant, activable via feature flag)
│   ├── manage.py               # CLI Django
│   ├── requirements.txt        # Dépendances Python
│   └── pytest.ini              # Configuration pytest
│
├── frontend/                   # Application React (sous-module Git)
│   └── frontend/               # Code source React
│       ├── src/                # Code source
│       │   ├── app/            # Pages et router
│       │   ├── components/     # Composants React réutilisables
│       │   ├── contexts/       # Contextes React (Auth, Language, Notifications)
│       │   ├── hooks/          # Hooks personnalisés
│       │   ├── utils/          # Utilitaires (API, i18n, logger)
│       │   ├── locales/        # Traductions i18n (fr, en, es, de, ar, sw)
│       │   └── styles/         # Styles globaux
│       ├── e2e/                # Tests E2E Playwright
│       ├── package.json        # Dépendances npm
│       └── vite.config.js      # Configuration Vite
│
├── docs/                       # Documentation complète
│   ├── architecture/           # Documentation architecture
│   ├── guides/                 # Guides techniques
│   ├── reports/                 # Rapports d'audit
│   ├── tests/                  # Documentation tests
│   └── security/               # Documentation sécurité
│
├── docker-compose.yml          # Orchestration Docker (dev local)
├── Makefile                    # Scripts d'automatisation
├── README.md                   # Documentation principale
└── CODE_TOTAL_EGOEJO.md       # Vue détaillée du code
```

---

## 🔧 Backend - Structure Détaillée

### Configuration Django (`backend/config/`)

#### `settings.py` - Configuration Principale
- **Feature Flags** :
  - `ENABLE_INVESTMENT_FEATURES` : Active le mode V2.0 (investissement)
  - `ENABLE_SAKA` : Active le protocole SAKA
  - `SAKA_VOTE_ENABLED` : Active le vote avec SAKA
  - `SAKA_PROJECT_BOOST_ENABLED` : Active le boost de projets avec SAKA
  - `SAKA_COMPOST_ENABLED` : Active le compostage SAKA
  - `SAKA_SILO_REDIS_ENABLED` : Active la redistribution du Silo
- **Base de données** : PostgreSQL (production) / SQLite (dev/tests)
- **Cache & WebSockets** : Redis
- **Stockage média** : R2/S3 (production) / Local (dev)
- **Sécurité** : CORS, CSRF, CSP, Headers sécurité, Rate limiting
- **JWT** : Authentification avec rotation tokens et blacklist
- **Celery** : Tâches asynchrones (emails, embeddings, TTS, compostage SAKA)

#### `urls.py` - Routes Principales
- `/api/` : Routes API REST
- `/admin/` : Interface Django Admin (Jazzmin)
- `/api/health/` : Healthcheck
- `/api/schema/` : OpenAPI Schema (drf-spectacular)
- `/api/docs/` : Swagger UI

#### `asgi.py` - ASGI pour WebSockets
- Configuration Django Channels pour chat temps réel
- Routing WebSocket :
  - `/ws/chat/<thread_id>/` : Chat en temps réel
  - `/ws/polls/<poll_id>/` : Votes en temps réel

#### `celery.py` - Configuration Celery
- Broker : Redis
- Tâches asynchrones :
  - Emails (Resend)
  - Génération embeddings (sentence-transformers)
  - Génération audio TTS
  - Compostage SAKA (cycles automatiques)
  - Redistribution Silo SAKA (Beat schedule)

---

### Application Core (`backend/core/`)

#### Modèles (`core/models/`)

**`projects.py`** - Projets & Cagnottes
- `Projet` : Projets avec support DONATION (V1.6) et EQUITY (V2.0 dormant)
- `Cagnotte` : Collectes de fonds
- `Contribution` : Contributions aux cagnottes
- `Community` : Communautés (subsidiarité, V1)

**`saka.py`** - Protocole SAKA (V2.1)
- `SakaWallet` : Portefeuille SAKA utilisateur
- `SakaTransaction` : Transactions SAKA (HARVEST, SPEND, COMPOST, REDISTRIBUTION)
- `SakaSilo` : Silo Commun (compteur unique)
- `SakaCycle` : Cycles SAKA (saisons)
- `SakaCompostLog` : Logs de compostage
- **Règle d'or** : Tous les mouvements critiques utilisent `select_for_update()` et `@transaction.atomic()`

**`impact.py`** - Impact 4P
- `ProjectImpact4P` : Scores 4P par projet
  - P1 : Performance financière (euros mobilisés) - **Réel**
  - P2 : Performance vivante (SAKA mobilisé) - **Réel**
  - P3 : Signal social (proxy V1 interne) - **Non académique**
  - P4 : Signal de sens (proxy V1 interne) - **Non académique**

**`polls.py`** - Système de Votes
- `Poll` : Sondages avec méthodes (binary, quadratic, majority)
- `PollBallot` : Votes avec points (quadratique) ou ranking (majoritaire)
- Support vote quadratique avec boost SAKA (intensité)

**`content.py`** - Contenus Éducatifs
- `EducationalContent` : Contenus avec embeddings et audio TTS
- Hash-based caching pour éviter régénération

**`chat.py`** - Messagerie Temps Réel
- `ChatThread` : Threads de conversation
- `ChatMessage` : Messages avec WebSockets

**`fundraising.py`** - Cagnottes
- `Cagnotte` : Collectes de fonds
- `Contribution` : Contributions

**`intents.py`** - Intentions
- `Intent` : Formulaire "Rejoindre" avec protection anti-spam (honeypot)

**`engagement.py`** - Engagements
- `Engagement` : Offres d'aide

**`help.py`** - Aide
- `HelpRequest` : Demandes d'aide

**`communities.py`** - Communautés
- `Community` : Communautés (subsidiarité)

**`monitoring.py`** - Monitoring
- `PerformanceMetric` : Métriques Core Web Vitals
- `MonitoringAlert` : Alertes système

**`moderation.py`** - Modération
- `ModerationReport` : Signalements
- `AuditLog` : Logs d'actions admin

#### API Views (`core/api/`)

**`projects.py`** - API Projets
- `ProjetListCreate` : Liste et création projets
- `ProjetRetrieveUpdateDestroy` : Détail, mise à jour, suppression
- `boost_project` : Boost SAKA d'un projet
- Cache Redis 5min sur GET

**`saka_views.py`** - API SAKA
- `GET /api/saka/wallet/` : Wallet SAKA utilisateur
- `GET /api/saka/cycles/` : Cycles SAKA (saisons)
- `GET /api/saka/silo/` : Silo Commun
- `POST /api/saka/redistribute/` : Redistribution Silo (admin)

**`polls.py`** - API Sondages
- `PollViewSet` : CRUD sondages
- `POST /api/polls/<id>/vote/` : Vote avec support SAKA (intensité)

**`content_views.py`** - API Contenus
- `EducationalContentViewSet` : CRUD contenus
- Génération automatique audio (TTS) et embeddings

**`engagement_views.py`** - API Engagements
- `EngagementViewSet` : CRUD engagements

**`chat.py`** - API Chat
- `ChatThreadViewSet` : Gestion threads
- `ChatMessageViewSet` : Gestion messages

**`impact_views.py`** - API Impact
- `GlobalAssetsView` : Patrimoine global utilisateur (cash, SAKA, impact)
- `ImpactDashboardView` : Tableau de bord d'impact

**`auth_views.py`** - Authentification
- `RegisterView` : Inscription
- `CurrentUserView` : Profil utilisateur

**`token_views.py`** - Tokens JWT
- `RefreshTokenView` : Rotation tokens avec blacklist

**`config_views.py`** - Configuration
- `FeaturesConfigView` : Feature flags (V1.6/V2.0)

**`monitoring_views.py`** - Monitoring
- `MetricsView` : Envoyer métriques
- `AlertsView` : Envoyer alertes

**`security_views.py`** - Sécurité
- `SecurityAuditView` : Audit sécurité (admin)
- `SecurityMetricsView` : Métriques sécurité (admin)

**`gdpr_views.py`** - GDPR/RGPD
- `DataExportView` : Export données utilisateur
- `DataDeleteView` : Suppression données utilisateur

#### Services (`core/services/`)

**`saka.py`** - Services SAKA
- `harvest_saka()` : Récolte SAKA (content_read, vote, etc.)
- `spend_saka()` : Dépense SAKA (vote, boost)
- `run_saka_compost_cycle()` : Compostage SAKA (wallets inactifs → Silo)
- `redistribute_saka_silo()` : Redistribution Silo → wallets actifs
- **Règle d'or** : Tous les services critiques utilisent `select_for_update()` et `@transaction.atomic()`

**`impact_4p.py`** - Services Impact 4P
- `update_project_4p()` : Calcul et mise à jour des scores 4P

**`saka_stats.py`** - Statistiques SAKA
- `get_cycle_stats()` : Statistiques par cycle SAKA

**`concierge.py`** - Concierge
- Support utilisateur automatisé

#### Tâches Celery (`core/tasks*.py`)

**`tasks.py`** - Tâches Générales
- `saka_run_compost_cycle` : Compostage SAKA (appelé par Beat)
- `saka_silo_redistribution_task` : Redistribution Silo (appelé par Beat)
- `notify_project_success_task` : Notifications asynchrones
- `send_email_task` : Envoi emails

**`tasks_embeddings.py`** - Génération Embeddings
- `generate_embedding_task` : Génération embeddings (sentence-transformers)

**`tasks_audio.py`** - Génération Audio
- `generate_audio_task` : Génération TTS

**`tasks_security.py`** - Sécurité
- `scan_file_antivirus_task` : Scan antivirus (ClamAV)

**`tasks_mycelium.py`** - Mycélium
- `reduce_mycelium_dimensions_task` : Réduction dimensionnalité (UMAP/t-SNE)

#### Tests (`core/tests*.py`)

**`tests.py`** - Tests Généraux
- Intentions, Projets, Impact 4P, Chat, Votes

**`tests_saka.py`** - Tests SAKA
- Wallets, Récolte, Dépense, Vote quadratique, Boost projets, Concurrence

**`tests_saka_celery.py`** - Tests Celery SAKA
- Compostage SAKA via Celery

**`tests_saka_redistribution.py`** - Tests Redistribution
- Redistribution Silo SAKA

**`tests_saka_public.py`** - Tests API Publiques SAKA
- Endpoints publics (cycles, silo)

**`tests_auth.py`** - Tests Authentification
- Login, Register, Refresh token

**`tests_auth_api.py`** - Tests API Auth
- Tests API complètes (register, login, refresh)

**`tests_content.py`** - Tests Content
- Contenus éducatifs

**`tests_engagement.py`** - Tests Engagement
- Engagements

**`tests_communities.py`** - Tests Communities
- Communautés

#### Sécurité (`core/security/`)

**`middleware.py`** - Middleware Sécurité
- Headers de sécurité renforcés
- Protection des données sensibles

**`encryption.py`** - Chiffrement
- Chiffrement de données sensibles

**`sanitization.py`** - Sanitization
- Nettoyage des entrées utilisateur

**`logging.py`** - Logging Sécurité
- Logs d'audit sécurité

---

### Application Finance (`backend/finance/`)

#### Modèles (`finance/models.py`)
- `UserWallet` : Portefeuille utilisateur (euros)
- `WalletTransaction` : Transactions wallet (PLEDGE, RELEASE, REFUND, COMMISSION)
- `EscrowContract` : Contrats d'escrow (LOCKED, RELEASED, REFUNDED)

#### Services (`finance/services.py`)
- `pledge_funds()` : Création escrow (verrouillage fonds)
- `release_escrow()` : Libération escrow (vers projet + commission système)
- `refund_escrow()` : Remboursement escrow (vers utilisateur)

#### Tests (`finance/tests*.py`)
- `tests_finance.py` : Tests généraux finance
- `tests_finance_escrow.py` : Tests escrow (intégrité financière)

---

### Application Investment (`backend/investment/`)

#### Modèles (`investment/models.py`)
- `ShareholderRegister` : Registre des actionnaires (V2.0 dormant)

#### Activation
- Activé via feature flag `ENABLE_INVESTMENT_FEATURES`
- Actuellement dormant (V1.6 actif)

---

## 🎨 Frontend - Structure Détaillée

### Pages (`frontend/frontend/src/app/pages/`)

**Pages Principales** :
- `Home.jsx` : Page d'accueil
- `Projets.jsx` : Liste des projets
- `Dashboard.jsx` : Tableau de bord utilisateur (FourPStrip, UserImpact4P)
- `Votes.jsx` : Page votes (statique, composant QuadraticVote à intégrer)
- `Contenus.jsx` : Contenus éducatifs
- `Chat.jsx` : Chat temps réel
- `Rejoindre.jsx` : Formulaire "Rejoindre"
- `Login.jsx` / `Register.jsx` : Authentification
- `Admin.jsx` : Interface admin

**Pages SAKA** :
- `SakaSeasons.tsx` : Saisons SAKA (cycles)
- `SakaSilo.jsx` : Silo Commun
- `SakaMonitor.jsx` : Monitoring SAKA (admin)

**Pages Autres** :
- `Univers.jsx`, `Vision.jsx`, `Citations.jsx`, `Alliances.jsx`, `Communaute.jsx`
- `Impact.jsx`, `MyCard.jsx`, `Mycelium.jsx`, `Podcast.jsx`, `RacinesPhilosophie.jsx`
- `NotFound.jsx`

### Composants (`frontend/frontend/src/components/`)

**Composants Dashboard** :
- `dashboard/FourPStrip.jsx` : Bandeau 4P (Capital financier, SAKA, Impact)
- `dashboard/UserImpact4P.jsx` : Impact 4P utilisateur

**Composants SAKA** :
- `saka/SakaSeasonBadge.jsx` : Badge saison SAKA (selon solde)
- `QuadraticVote.jsx` : Vote quadratique avec boost SAKA

**Composants Projets** :
- `projects/Impact4PCard.jsx` : Carte Impact 4P projet

**Composants UI** :
- `Button.jsx`, `Input.jsx`, `Loader.jsx`
- `Navbar.jsx`, `Layout.jsx`, `FullscreenMenu.jsx`
- `Notification.jsx`, `NotificationContainer.jsx`
- `ErrorBoundary.jsx`, `PageTransition.jsx`
- `SEO.jsx`, `LanguageSelector.jsx`
- `EcoModeToggle.jsx`, `OfflineIndicator.jsx`

**Composants 3D/Animations** :
- `Logo3D.jsx`, `HeroSorgho.jsx`, `MenuCube3D.jsx`
- `MyceliumVisualization.jsx`, `CardTilt.jsx`
- `CursorSpotlight.jsx`, `CustomCursor.jsx`

**Composants Chat** :
- `ChatWindow.jsx`, `ChatList.jsx`
- `chat/SupportBubble.jsx`

**Composants Autres** :
- `SemanticSearch.jsx`, `SemanticSuggestions.jsx`
- `AudioPlayer.jsx`, `ScrollProgress.jsx`
- `OptimizedImage.jsx`, `PageViewTracker.jsx`

### Contextes (`frontend/frontend/src/contexts/`)

- `AuthContext.jsx` : Authentification (user, login, logout)
- `LanguageContext.jsx` : Internationalisation (fr, en, es, de, ar, sw)
- `NotificationContext.jsx` : Notifications (toasts)
- `EcoModeContext.jsx` : Mode éco (réduction consommation)

### Hooks (`frontend/frontend/src/hooks/`)

**Hooks API** :
- `useGlobalAssets.js` : Patrimoine global (cash, SAKA, impact)
- `useSaka.js` : Gestion SAKA
- `useSakaSilo.ts` : Silo Commun
- `useSakaCycles.ts` : Cycles SAKA

**Hooks Utilitaires** :
- `useFetch.js` : Requêtes API
- `useLocalStorage.js` : LocalStorage
- `useDebounce.js` : Debounce
- `useToggle.js` : Toggle
- `useMediaQuery.js` : Media queries
- `useClickOutside.js` : Détection clic extérieur
- `useNotification.js` : Notifications
- `useSEO.js` : SEO
- `useWebSocket.js` : WebSockets

**Hooks Autres** :
- `useEasterEgg.js`, `useLowPowerMode.js`

### Utilitaires (`frontend/frontend/src/utils/`)

- `api.js` : Client API (fetchAPI, gestion erreurs)
- `i18n.js` : Internationalisation
- `logger.js` : Logging
- `analytics.js` : Analytics (Vercel)
- `monitoring.js` : Monitoring (Sentry)
- `performance.js` : Métriques performance
- `money.js` : Formatage monétaire
- `format.js` : Formatage général
- `validation.js` : Validation formulaires
- `security.js` : Sécurité frontend
- `gdpr.js` : GDPR
- `sentry.js` : Configuration Sentry
- `scrollAnimations.js` : Animations scroll

### Tests (`frontend/frontend/src/__tests__/`)

**Tests Unitaires (Vitest)** :
- Pages : `app/pages/__tests__/*.test.jsx`
- Composants : `components/__tests__/*.test.jsx`
- Hooks : `hooks/__tests__/*.test.js`
- Contextes : `contexts/__tests__/*.test.jsx`
- Utilitaires : `utils/__tests__/*.test.js`

**Tests E2E (Playwright)** :
- `e2e/backend-connection.spec.js` : Connexion backend-frontend
- `e2e/votes-quadratic.spec.js` : Vote quadratique (existant)
- `e2e/votes.spec.js` : Vote quadratique complet (nouveau)
- `e2e/projects-saka-boost.spec.js` : Boost SAKA projet
- `e2e/auth.spec.js`, `e2e/home.spec.js`, `e2e/navigation.spec.js`, etc.

**Tests Accessibilité** :
- `__tests__/accessibility/*.test.jsx` : ARIA, contraste, clavier

**Tests Performance** :
- `__tests__/performance/*.test.js` : Métriques, Lighthouse

---

## 🔄 Flux de Données

### Backend → Frontend

```
User Action
    ↓
React Component
    ↓
Hook (useGlobalAssets, useSaka, etc.)
    ↓
API Client (utils/api.js)
    ↓
HTTP Request (fetch)
    ↓
Django REST Framework View
    ↓
Service Layer (core/services/)
    ↓
Model (core/models/)
    ↓
Database (PostgreSQL)
    ↓
Response JSON
    ↓
Hook Update State
    ↓
Component Re-render
```

### Temps Réel (WebSockets)

```
User Action (Chat/Vote)
    ↓
WebSocket (useWebSocket)
    ↓
Django Channels Consumer
    ↓
Broadcast to Group
    ↓
All Connected Clients Update
```

---

## 🧪 Tests

### Backend (Pytest)

**Structure** :
- `core/tests.py` : Tests généraux (41 tests)
- `core/tests_saka.py` : Tests SAKA (27 tests)
- `core/tests_auth_api.py` : Tests Auth API (12 tests)
- `finance/tests_finance_escrow.py` : Tests Escrow (8 tests)
- `core/tests_saka_celery.py` : Tests Celery SAKA (6 tests)
- **Total** : ~100+ tests backend

**Commandes** :
```bash
cd backend
python -m pytest                    # Tous les tests
python -m pytest core/tests_saka.py # Tests SAKA uniquement
python -m pytest --cov=core         # Avec couverture
```

### Frontend (Vitest + Playwright)

**Structure** :
- Tests unitaires : `src/**/__tests__/*.test.{js,jsx,tsx}` (414 tests)
- Tests E2E : `e2e/*.spec.js` (10+ fichiers)

**Commandes** :
```bash
cd frontend/frontend
npm test                    # Vitest (watch mode)
npm run test:run            # Vitest (une fois)
npm run test:e2e            # Playwright
npm run test:coverage       # Couverture
```

---

## 🔐 Sécurité

### Backend

- **Authentification** : JWT avec rotation tokens
- **Rate Limiting** : DRF throttling (AnonRateThrottle, UserRateThrottle)
- **CORS** : Configuration stricte
- **CSRF** : Protection activée
- **CSP** : Content Security Policy
- **Headers Sécurité** : HSTS, X-Frame-Options, etc.
- **Validation** : Sanitization des entrées
- **Chiffrement** : Données sensibles chiffrées
- **Audit** : Logs d'audit sécurité

### Frontend

- **CSP** : Content Security Policy
- **Validation** : Validation formulaires
- **Sanitization** : Nettoyage des entrées
- **HTTPS** : Forcé en production
- **Tokens** : Stockage sécurisé (localStorage, rotation)

---

## 📊 Métriques & Monitoring

### Backend

- **Sentry** : Monitoring erreurs
- **Logging** : Logs structurés
- **Métriques** : Performance, sécurité
- **Healthcheck** : `/api/health/`

### Frontend

- **Sentry** : Monitoring erreurs
- **Vercel Analytics** : Analytics
- **Performance** : Core Web Vitals
- **Lighthouse** : Tests performance

---

## 🚀 Déploiement

### Backend (Railway)

- **Base de données** : PostgreSQL (Railway)
- **Cache** : Redis (Railway)
- **Stockage** : Cloudflare R2 (S3-compatible)
- **Serveur** : Gunicorn + Daphne (ASGI)

### Frontend (Vercel)

- **Build** : Vite (production bundle dans `dist/`)
- **CDN** : Vercel Edge Network
- **PWA** : Service Worker (Workbox)

---

## 📝 Principes d'Architecture

### Backend

1. **Service Layer** : Logique métier dans `core/services/`, pas dans les views
2. **Atomicité** : Transactions atomiques pour opérations critiques (SAKA, Finance)
3. **Concurrence** : `select_for_update()` pour éviter race conditions
4. **Feature Flags** : Activation/désactivation de fonctionnalités
5. **Tests** : Tests de concurrence pour SAKA et Finance

### Frontend

1. **Lazy Loading** : Toutes les pages sont lazy-loaded
2. **Code Splitting** : Chunks séparés (react, three, gsap, vendor)
3. **Context API** : État global (auth, language, notifications)
4. **Custom Hooks** : Logique réutilisable
5. **Error Boundaries** : Gestion erreurs React

---

## 🎯 Domaines Métier

### 1. Finance (V1.6)

- **Cagnottes** : Collectes de fonds
- **Escrow** : Verrouillage fonds (pledge → release → commission)
- **Wallets** : Portefeuilles utilisateurs

### 2. SAKA (V2.1)

- **Récolte** : Gagner SAKA (content_read, vote, etc.)
- **Dépense** : Dépenser SAKA (vote quadratique, boost projet)
- **Compostage** : Wallets inactifs → Silo Commun
- **Redistribution** : Silo Commun → Wallets actifs
- **Cycles** : Saisons SAKA (agrégation statistiques)

### 3. Impact 4P

- **P1** : Performance financière (euros mobilisés)
- **P2** : Performance vivante (SAKA mobilisé)
- **P3** : Signal social (proxy V1 interne)
- **P4** : Signal de sens (proxy V1 interne)

### 4. Votes

- **Quadratique** : Distribution de points avec boost SAKA (intensité)
- **Majoritaire** : Jugement majoritaire
- **Binaire** : Oui/Non

### 5. Contenus

- **Éducatifs** : Contenus avec embeddings et audio TTS
- **Engagements** : Offres d'aide
- **Aide** : Demandes d'aide

### 6. Communautés

- **Communautés** : Groupes (subsidiarité, V1)

---

## 📚 Documentation

- **Architecture** : `docs/architecture/`
- **Guides** : `docs/guides/`
- **Tests** : `docs/tests/`
- **Sécurité** : `docs/security/`
- **Rapports** : `docs/reports/`

---

## ✅ État Actuel

- **Backend** : ✅ 41 tests passent (100%)
- **Frontend** : ✅ 414 tests passent (100%)
- **E2E** : ✅ 10+ scénarios couverts
- **Build** : ✅ Réussi (sans warnings)
- **Linter** : ✅ Aucune erreur
- **Production** : ✅ Déployé (Railway + Vercel)

---

**Dernière mise à jour** : 2025-01-16  
**Version** : 2.1 (Hybride V1.6 + V2.0)

