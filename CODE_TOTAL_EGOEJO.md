# 📦 Code Total du Projet EGOEJO

**Version**: 2.0 (Hybride V1.6 + V2.0)  
**Date**: 2025-12-10  
**Statut**: Production Ready ✅  
**Tests**: 100% de réussite (409/409 tests) ✅

---

## 📋 Table des Matières

1. [Architecture Globale](#architecture-globale)
2. [Backend - Structure Complète](#backend-structure-complète)
3. [Frontend - Structure Complète](#frontend-structure-complète)
4. [Configuration & Déploiement](#configuration--déploiement)
5. [Fichiers Clés avec Contenu](#fichiers-clés-avec-contenu)

---

## 🏗️ Architecture Globale

```
egoejo/
├── backend/              # API Django REST Framework
│   ├── config/          # Configuration Django
│   ├── core/            # Application principale
│   ├── finance/         # Système financier unifié (V1.6 + V2.0)
│   ├── investment/      # Investissement (V2.0 dormant)
│   └── manage.py
│
├── frontend/            # Application React (sous-module Git)
│   └── frontend/        # Code source React
│       ├── src/
│       │   ├── app/     # Pages et router
│       │   ├── components/  # Composants React
│       │   ├── contexts/   # Contextes React
│       │   └── locales/    # Traductions i18n
│       └── package.json
│
├── docker-compose.yml   # Orchestration Docker
├── README.md            # Documentation principale
└── FICHE_GLOBALE_EGOEJO.md  # Fiche technique complète
```

---

## 🔧 Backend - Structure Complète

### Application Core (`backend/core/`)

#### Configuration App (`core/apps.py`)
- **Signature de démarrage** : Logo ASCII coloré affiché au démarrage du serveur
  - Détection automatique du mode (V1.6 ou V2.0)
  - Codes couleurs ANSI (Vert pour le vivant, Cyan pour la tech)
  - Affichage uniquement lors de `runserver` (pas lors des migrations ou tâches Celery)
  - Informations affichées : Mode, System, Admin group

### Configuration Django (`backend/config/`)

#### `settings.py` - Configuration Principale
- **Feature Flags** : `ENABLE_INVESTMENT_FEATURES`, `EGOEJO_COMMISSION_RATE`, `STRIPE_FEE_ESTIMATE`, `FOUNDER_GROUP_NAME`
- **Base de données** : PostgreSQL (production) / SQLite (dev)
- **Redis** : Cache & WebSockets
- **Stockage** : R2/S3 (production) / Local (dev)
- **Sécurité** : CORS, CSRF, Headers sécurité, Rate limiting
- **JWT** : Authentification avec rotation tokens
- **Celery** : Tâches asynchrones
- **Logging** : Configuration complète

#### `urls.py` - Routes Principales
- `/api/` : Routes API
- `/admin/` : Interface Django Admin
- `/api/health/` : Healthcheck
- `/api/schema/` : OpenAPI Schema
- `/api/docs/` : Swagger UI

#### `asgi.py` - ASGI pour WebSockets
- Configuration Channels pour chat temps réel
- Routing WebSocket : `/ws/chat/<thread_id>/`, `/ws/polls/<poll_id>/`

#### `wsgi.py` - WSGI pour Production
- Configuration Gunicorn

#### `celery.py` - Configuration Celery
- Broker : Redis
- Tâches asynchrones : emails, embeddings, TTS, scan antivirus

---

### Application Core (`backend/core/`)

#### Modèles (`core/models/`)

**`projects.py`** - Modèle Projet Hybride
- `FundingType` : DONATION, EQUITY, HYBRID
- `Projet` : Champs `funding_type`, `donation_goal`, `investment_goal`, `share_price`, `total_shares`, `valuation_pre_money`
- Propriétés : `is_investment_open`, `donation_current`, `investment_current`
- `ProjetQuerySet.search()` : Recherche full-text avec pg_trgm

**`polls.py`** - Système de Votes
- `Poll` : Sondages avec méthodes avancées (binary, quadratic, majority)
- `PollBallot` : Votes avec points (quadratique) ou ranking (majoritaire)
- `get_vote_weight()` : Vote pondéré V1.6/V2.0 (1 voix ou 1 action = 1 voix, x100 fondateurs)

**`content.py`** - Contenus Éducatifs
- `EducationalContent` : Champs `category`, `tags`, `embedding`, `audio_file`, `audio_source_hash`, `embedding_source_hash`
- Hash-based caching pour éviter régénération TTS/embeddings

**`chat.py`** - Messagerie Temps Réel
- `ChatThread` : Threads de conversation
- `ChatMessage` : Messages avec WebSockets

**`fundraising.py`** - Cagnottes
- `Cagnotte` : Collectes de fonds
- `Contribution` : Contributions aux cagnottes

**`intents.py`** - Intentions de Rejoindre
- `Intent` : Formulaire avec protection anti-spam (honeypot)

**`impact.py`** - Gamification
- `ImpactDashboard` : Tableau de bord d'impact utilisateur

**`monitoring.py`** - Monitoring
- `PerformanceMetric` : Métriques Core Web Vitals
- `MonitoringAlert` : Alertes système

**`moderation.py`** - Modération
- `ModerationReport` : Signalements
- `AuditLog` : Logs d'actions admin

#### API Views (`core/api/`)

**`projects.py`** - API Projets
- `ProjetListCreate` : Liste et création projets
- Cache Redis 5min sur GET

**`search_views.py`** - Recherche Full-Text
- `ProjetSearchView` : Recherche avec pg_trgm

**`semantic_search_views.py`** - Recherche Sémantique
- `SemanticSearchView` : Recherche conceptuelle avec embeddings
- `SemanticSuggestionsView` : Suggestions liées

**`polls.py`** - API Sondages
- `PollViewSet` : CRUD sondages
- Support vote quadratique et jugement majoritaire

**`content_views.py`** - API Contenus
- `EducationalContentViewSet` : CRUD contenus
- Génération automatique audio (TTS) et embeddings
- Hash-based caching

**`chat.py`** - API Chat
- `ChatThreadViewSet` : Gestion threads
- `ChatMessageViewSet` : Gestion messages

**`config_views.py`** - Configuration Features
- `FeaturesConfigView` : Endpoint pour récupérer feature flags (V1.6/V2.0)

**`mycelium_views.py`** - Mycélium Numérique
- `MyceliumDataView` : Coordonnées 3D pour visualisation
- `MyceliumReduceView` : Lancer réduction dimensionnalité (UMAP/t-SNE)

**`impact_views.py`** - Impact
- `ImpactDashboardView` : Tableau de bord d'impact
- `GlobalAssetsView` : Patrimoine global utilisateur (NOUVEAU)
  - Retourne : `cash_balance`, `pockets`, `donations`, `equity_portfolio`, `social_dividend`
  - **Agrégations ORM** : Utilise `Sum()`, `F()`, `annotate()` (pas de boucles Python)
  - **Feature flag** : `equity_portfolio` conditionnel sur `ENABLE_INVESTMENT_FEATURES`
  - **Précision** : Tous les montants en Decimal, sérialisés en strings

**`monitoring_views.py`** - Monitoring
- `MetricsView` : Envoyer métriques
- `AlertsView` : Envoyer alertes
- `MetricsStatsView` : Statistiques (admin)
- `AlertsListView` : Liste alertes (admin)

**`security_views.py`** - Sécurité
- `SecurityAuditView` : Audit sécurité (admin)
- `SecurityMetricsView` : Métriques sécurité (admin)

**`gdpr_views.py`** - GDPR/RGPD
- `DataExportView` : Export données utilisateur
- `DataDeleteView` : Suppression données utilisateur

**`auth_views.py`** - Authentification
- `RegisterView` : Inscription
- `CurrentUserView` : Profil utilisateur

**`token_views.py`** - Tokens JWT
- `RefreshTokenView` : Rotation tokens avec blacklist

#### Tâches Celery (`core/tasks*.py`)

**`tasks.py`** - Tâches Générales
- `notify_project_success_task` : Notifications asynchrones projet réussi
- `send_email_task` : Envoi emails
- `generate_impact_dashboard_task` : Génération tableau de bord impact

**`tasks_embeddings.py`** - Génération Embeddings
- `generate_embedding_task` : Génération embeddings (OpenAI ou Sentence Transformers)
- Hash-based caching avec `embedding_source_hash`

**`tasks_audio.py`** - Génération Audio TTS
- `generate_audio_content` : Génération audio (OpenAI TTS ou ElevenLabs)
- Hash-based caching avec `audio_source_hash`

**`tasks_mycelium.py`** - Réduction Dimensionnalité
- `reduce_dimensions_task` : Réduction UMAP/t-SNE pour coordonnées 3D

**`tasks_security.py`** - Sécurité
- `scan_file_antivirus_task` : Scan ClamAV asynchrone
- `validate_file_type_task` : Validation type MIME

#### Permissions (`core/permissions.py`)
- `IsInvestmentFeatureEnabled` : Pare-feu V2.0 (bloque si feature désactivée)
- `IsFounderOrReadOnly` : Protection fondateur (groupe `FOUNDER_GROUP_NAME`)

#### URLs (`core/urls.py`)
- Routes API complètes avec router DRF
- Endpoints : auth, projets, cagnottes, chat, polls, contents, impact, monitoring, security, gdpr, config, investment

---

### Application Finance (`backend/finance/`)

#### Modèles (`finance/models.py`)
- `UserWallet` : Portefeuille utilisateur avec solde
- `WalletTransaction` : Transactions (DEPOSIT, PLEDGE_DONATION, PLEDGE_EQUITY, REFUND, RELEASE, COMMISSION, POCKET_TRANSFER, POCKET_ALLOCATION)
  - **Idempotence** : `idempotency_key` (UUIDField unique)
- `EscrowContract` : Contrats d'escrow (cantonnement)
- `WalletPocket` : Sous-comptes (pockets) pour segmenter les fonds par objectif
  - Champs : `wallet`, `name`, `pocket_type` (DONATION, INVESTMENT_RESERVE), `allocation_percentage`, `target_amount`, `current_amount`
  - Contrainte : `unique_together` sur `(wallet, name)`
  - Validation : `allocation_percentage` <= 100%

#### Services (`finance/services.py`)
- `pledge_funds()` : Engagement unifié (Don ou Investissement)
  - **Race condition corrigée** : `select_for_update()` verrouille wallet
  - **Idempotence** : Vérification `idempotency_key`
  - **Arrondis précis** : `quantize()` avec `ROUND_HALF_UP`
- `release_escrow()` : Libération escrow avec commission
  - **Arrondis précis** : Calculs avec `quantize()`
- `close_project_success()` : Clôture projet avec notifications asynchrones
  - **Asynchronisme** : Délégué à Celery (`notify_project_success_task`)
- `transfer_to_pocket(user, pocket_id, amount)` : Transfert de fonds vers une pocket
  - **Verrouillage** : `select_for_update()` sur wallet et pocket
  - **Vérification solde** : `InsufficientBalanceError` si solde insuffisant
  - **Transaction** : Crée `WalletTransaction` de type `POCKET_TRANSFER`
  - **Arrondis précis** : `quantize()` avec `ROUND_HALF_UP`
- `allocate_deposit_across_pockets(user, amount)` : Allocation automatique d'un dépôt
  - **Logique** : Répartit selon `allocation_percentage` de chaque pocket
  - **Réutilisation** : Utilise `transfer_to_pocket()` pour chaque allocation
  - **Reliquat** : Le reste reste dans le solde principal

#### Admin (`finance/admin.py`)
- Interface Django Admin pour Wallet, Transactions, Escrow

---

### Application Investment (`backend/investment/`)

#### Modèles (`investment/models.py`)
- `ShareholderRegister` : Registre actionnaires (V2.0 dormant)
  - Champs : `number_of_shares`, `amount_invested`, `subscription_bulletin`, `is_signed`

#### Views (`investment/views.py`)
- `ShareholderRegisterViewSet` : ViewSet lecture seule
  - **Protection** : `IsInvestmentFeatureEnabled` (403 si feature désactivée)

#### Admin (`investment/admin.py`)
- Interface Django Admin pour ShareholderRegister

---

## 🎨 Frontend - Structure Complète

### Configuration (`frontend/frontend/`)

#### `package.json`
- **Dependencies** : React 19.2.0, Vite 7.1.11, React Router 7.9.4, Three.js 0.180.0, GSAP 3.13.0
- **DevDependencies** : Vitest 4.0.15, Playwright 1.48.0, ESLint, TypeScript, Husky, lint-staged
- **Scripts** : `dev`, `build`, `test`, `test:e2e`, `lint`, `type-check`
- **Note** : Vitest mis à jour de 2.1.9 à 4.0.15 (correction de 7 vulnérabilités npm)

#### `vite.config.js`
- Configuration Vite avec plugins React, PWA
- Code splitting : vendor, react, gsap, three

#### `tsconfig.json` & `tsconfig.node.json`
- TypeScript Strict Mode configuré
- ESLint interdit nouveaux fichiers `.jsx` (force `.tsx`)

#### `.lintstagedrc.js`
- Configuration lint-staged : ESLint et TypeScript sur fichiers modifiés

#### `.husky/pre-commit`
- Hook Git pour exécuter lint-staged avant commit

---

### Pages (`frontend/frontend/src/app/pages/`)

- **`Home.jsx`** : Page d'accueil avec HeroSorgho 3D
- **`Univers.jsx`** : Exploration du vivant
- **`Vision.jsx`** : Vision du collectif
- **`Alliances.jsx`** : Partenariats
- **`Projets.jsx`** : Liste des projets (avec recherche sémantique)
- **`Contenus.jsx`** : Bibliothèque de contenus
- **`Communaute.jsx`** : Communauté
- **`Citations.jsx`** : Citations inspirantes
- **`Votes.jsx`** : Sondages et votes (avec vote quadratique)
- **`Chat.jsx`** : Messagerie temps réel
- **`Rejoindre.jsx`** : Formulaire d'adhésion
- **`Admin.jsx`** : Interface admin
- **`Login.jsx`** : Connexion
- **`Register.jsx`** : Inscription
- **`Impact.jsx`** : Tableau de bord d'impact utilisateur
- **`RacinesPhilosophie.jsx`** : Section Racines & Philosophie
- **`Mycelium.jsx`** : Visualisation 3D "Mycélium Numérique" (lazy loaded)
- **`Podcast.jsx`** : Liste des contenus avec versions audio
- **`NotFound.jsx`** : Page 404

---

### Composants (`frontend/frontend/src/components/`)

#### UI Components
- **`Button.jsx`** : Boutons avec variants
- **`Input.jsx`** : Champs de formulaire avec validation
- **`CardTilt.jsx`** : Cartes avec effet 3D tilt
- **`Loader.jsx`** : Indicateurs de chargement
- **`Notification.jsx`** : Notifications
- **`ErrorBoundary.jsx`** : Gestion d'erreurs React

#### Layout Components
- **`Layout.jsx`** : Layout principal avec navigation
- **`Navbar.jsx`** : Barre de navigation
- **`FullscreenMenu.jsx`** : Menu plein écran
- **`LanguageSelector.jsx`** : Sélecteur de langue

#### 3D & Animations
- **`HeroSorgho.jsx`** : Hero section avec Three.js
- **`Logo3D.jsx`** : Logo 3D interactif
- **`MenuCube3D.jsx`** : Menu cube 3D
- **`CustomCursor.jsx`** : Curseur personnalisé
- **`CursorSpotlight.jsx`** : Effet spotlight
- **`PageTransition.jsx`** : Transitions entre pages
- **`ScrollProgress.jsx`** : Barre de progression scroll

#### Features
- **`ChatWindow.jsx`** : Interface de chat
- **`ChatList.jsx`** : Liste des conversations
- **`SEO.jsx`** : Gestion SEO dynamique
- **`OptimizedImage.jsx`** : Images optimisées
- **`PageViewTracker.jsx`** : Tracking des vues
- **`EcoModeToggle.jsx`** : Toggle mode éco-responsable
- **`OfflineIndicator.jsx`** : Indicateur statut hors-ligne (PWA)
- **`QuadraticVote.jsx`** : Composant vote quadratique
- **`SemanticSuggestions.jsx`** : Suggestions sémantiques liées
- **`SemanticSearch.jsx`** : Recherche sémantique conceptuelle
- **`MyceliumVisualization.jsx`** : Visualisation 3D constellation (Three.js)
- **`AudioPlayer.jsx`** : Lecteur audio pour contenus TTS

---

### Contextes (`frontend/frontend/src/contexts/`)

- **`AuthContext.jsx`** : Authentification utilisateur
- **`LanguageContext.jsx`** : Gestion i18n (FR, EN, ES, DE, AR, SW)
- **`NotificationContext.jsx`** : Notifications globales
- **`EcoModeContext.jsx`** : Mode éco-responsable

---

### Router (`frontend/frontend/src/app/router.jsx`)

- Configuration React Router avec lazy loading
- Route `/mycelium` : Lazy loaded avec `React.lazy` et `Suspense`
- Toutes les routes configurées

---

### Utilitaires (`frontend/frontend/src/utils/`)

- **`api.js`** : Client API
- **`monitoring.js`** : Monitoring
- **`sentry.js`** : Sentry

---

### Tests (`frontend/frontend/src/`)

#### Tests Unitaires (Vitest 4.0.15)
- **`test-utils.jsx`** : Helper pour tests (fournit tous les contextes : `EcoModeProvider`, `LanguageProvider`, `AuthProvider`, `NotificationProvider`)
- **Tests** : 390 tests (100% de réussite) ✅
- Tests composants, hooks, pages, accessibilité
- Configuration : `vitest.config.js`, `src/test/setup.js`, `src/test/mocks/server.js`

#### Tests E2E (Playwright)
- **`e2e/`** : Tests end-to-end complets
- Configuration : `playwright.config.js`

#### Corrections Récentes (2025-12-10)
- ✅ **Frontend** : Ajout de `EcoModeProvider` dans tous les helpers de test (45 tests corrigés)
- ✅ **Frontend** : Correction du test `backend-connection` (mock de `getTokenSecurely` et `isTokenValid`) (1 test corrigé)
- ✅ **Frontend** : 100% de réussite (390/390 tests) ✅
- ✅ **Backend** : Création de la fonction `grant_founder_permissions()` pour attribuer les permissions fondateur
- ✅ **Backend** : Authentification des utilisateurs admin avec les permissions fondateur dans les tests (7 tests corrigés)
- ✅ **Backend** : 100% de réussite (19/19 tests) ✅
- ✅ **Global** : 100% de réussite (409/409 tests) ✅

---

## ⚙️ Configuration & Déploiement

### Variables d'Environnement Backend

```env
# Django
DJANGO_SECRET_KEY=...
DEBUG=0
ALLOWED_HOSTS=egoejo.org,www.egoejo.org

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# Storage (R2/S3)
USE_S3_STORAGE=true
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=egoejo-media
R2_ENDPOINT_URL=https://xxx.r2.cloudflarestorage.com

# Feature Flags (V1.6/V2.0)
ENABLE_INVESTMENT_FEATURES=False
EGOEJO_COMMISSION_RATE=0.05
STRIPE_FEE_ESTIMATE=0.03
FOUNDER_GROUP_NAME=Founders_V1_Protection

# Intelligence Sémantique
OPENAI_API_KEY=...  # Optionnel

# TTS Audio
TTS_PROVIDER=openai
TTS_VOICE=alloy

# Sécurité
ADMIN_TOKEN=...
ENCRYPTION_KEY=...

# Email
RESEND_API_KEY=...
NOTIFY_EMAIL=...
```

### Variables d'Environnement Frontend

```env
VITE_API_URL=https://egoejo-production.up.railway.app
VITE_SENTRY_DSN=https://...  # Optionnel
```

---

## 📁 Fichiers Clés avec Contenu

### Backend

#### `backend/config/settings.py`
- Configuration complète Django avec feature flags V1.6/V2.0
- Sécurité renforcée, CORS, CSRF, Rate limiting
- Configuration Celery, Redis, R2/S3, JWT

#### `backend/core/models/projects.py`
- Modèle `Projet` hybride avec support V1.6/V2.0
- `ProjetQuerySet.search()` pour recherche full-text

#### `backend/core/models/polls.py`
- Modèle `Poll` avec vote pondéré V1.6/V2.0
- `get_vote_weight()` pour protection fondateur

#### `backend/finance/models.py`
- `UserWallet`, `WalletTransaction` (avec `idempotency_key`), `EscrowContract`

#### `backend/finance/services.py`
- `pledge_funds()` : Race condition corrigée, idempotence, arrondis précis
- `release_escrow()` : Arrondis précis
- `close_project_success()` : Notifications asynchrones

#### `backend/investment/models.py`
- `ShareholderRegister` : Registre actionnaires (V2.0 dormant)

#### `backend/investment/views.py`
- `ShareholderRegisterViewSet` : Protégé par `IsInvestmentFeatureEnabled`

#### `backend/core/permissions.py`
- `IsInvestmentFeatureEnabled` : Pare-feu V2.0
- `IsFounderOrReadOnly` : Protection fondateur

#### `backend/core/api/config_views.py`
- `FeaturesConfigView` : Endpoint pour feature flags

#### `backend/core/tasks.py`
- `notify_project_success_task` : Notifications asynchrones

#### `backend/core/tasks_embeddings.py`
- Génération embeddings avec hash-based caching

#### `backend/core/tasks_audio.py`
- Génération audio TTS avec hash-based caching

#### `backend/core/urls.py`
- Routes API complètes avec router DRF

---

### Frontend

#### `frontend/frontend/src/app/router.jsx`
- Configuration React Router avec lazy loading `/mycelium`

#### `frontend/frontend/src/main.jsx`
- Point d'entrée avec `EcoModeProvider`

#### `frontend/frontend/src/test/test-utils.jsx`
- Helper pour tests (fournit tous les contextes : `EcoModeProvider`, `LanguageProvider`, `AuthProvider`, `NotificationProvider`)
- Helper `renderWithProviders` pour wrapper les composants dans les tests

#### `frontend/frontend/package.json`
- Dependencies et scripts complets

#### `frontend/frontend/.lintstagedrc.js`
- Configuration lint-staged

#### `frontend/frontend/.husky/pre-commit`
- Hook Git pre-commit

---

## 🚀 Déploiement

### Backend (Railway)
- **Start Command** : `python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application`
- **Database** : PostgreSQL (Railway)
- **Variables d'environnement** : Voir section Configuration

### Frontend (Vercel)
- **Root Directory** : `frontend/frontend`
- **Build Command** : `npm install && npm run build`
- **Output Directory** : `dist`
- **Variables d'environnement** : `VITE_API_URL`, `VITE_SENTRY_DSN`

---

## ✅ Checklist Production

- [x] Tests frontend passent (100% - 390/390 tests) ✅
- [x] Tests backend passent (100% - 19/19 tests) ✅
- [x] Taux de réussite global : 100% (409/409 tests) ✅
- [x] Sécurité renforcée (race condition, arrondis, idempotence, asynchronisme)
- [x] Monitoring configuré (Sentry)
- [x] Documentation complète
- [x] Déploiement automatique
- [x] HTTPS activé
- [x] Variables d'environnement configurées
- [x] Base de données migrée
- [x] Fichiers statiques servis
- [x] CORS configuré
- [x] Rate limiting activé
- [x] Logs configurés
- [x] Backups planifiés
- [x] Stockage objet R2/S3 configuré
- [x] Recherche full-text implémentée
- [x] Intelligence sémantique implémentée
- [x] Vote quadratique implémenté
- [x] Scan antivirus intégré
- [x] TypeScript Strict configuré
- [x] Mycélium Numérique implémenté
- [x] TTS Audio-First implémenté
- [x] Architecture "The Sleeping Giant" implémentée
- [x] Système financier unifié (Wallet, Escrow)
- [x] Investissement dormant (V2.0 activable)
- [x] Feature flags (ENABLE_INVESTMENT_FEATURES)
- [x] CI Matrix Testing (GitHub Actions)
- [x] Husky + lint-staged configuré
- [x] Signature de démarrage backend (logo ASCII coloré)
- [x] Easter egg frontend "vivant"

---

## 🎨 Touches Finales - Identité Visuelle

### Backend - Signature de Démarrage

Lors du démarrage du serveur Django (`python manage.py runserver`), un logo ASCII coloré s'affiche dans le terminal :

```
      ______ _____  ____  ______      _  ____  
     |  ____/ ____|/ __ \|  ____|    | |/ __ \ 
     | |__ | |  __| |  | | |__       | | |  | |
     |  __|| | |_ | |  | |  __|  _   | | |  | |
     | |___| |__| | |__| | |____| |__| | |__| |
     |______\_____|\____/|______|\____/ \____/ 

      🌱 Dedicated to the Living / Dédié au Vivant
      🤖 System: The Sleeping Giant Protocol
      ⚙️  Mode:   V1.6 (Donation Only)
      🛡️  Admin:  Founders_V1_Protection
```

**Fichier** : `backend/core/apps.py`
- Détection automatique du mode (V1.6/V2.0)
- Codes couleurs ANSI (Vert, Cyan, Jaune)
- Affichage uniquement lors de `runserver`

### Frontend - Easter Egg "Vivant"

Si un utilisateur tape "vivant" sur son clavier (hors champs de saisie), une animation se déclenche :

1. **Effet visuel** : Filtre "Terre/Vert" appliqué au body (sepia + hue-rotate)
2. **Notification** : Message de confirmation après 2 secondes
3. **Console** : Message "🌱 La nature reprend ses droits..."

**Fichier** : `frontend/frontend/src/hooks/useEasterEgg.js`
- Intégré dans `main.jsx` via `AppWrapper`
- Ignore les champs de saisie (input/textarea)
- Utilise les notifications du navigateur si disponibles

---

## 🧪 Tests & Qualité

### Résultats des Tests (2025-12-10)

#### Frontend (React/Vitest 4.0.15)
- **Test Files** : 47 passed (0 failed) ✅
- **Tests** : 390 passed (0 failed) ✅
- **Taux de réussite** : **100%** ✅
- **Durée** : ~18s
- **Framework** : Vitest 4.0.15, Testing Library, Playwright

#### Backend (Django/Pytest)
- **Tests** : 19 passed (0 failed) ✅
- **Taux de réussite** : **100%** ✅
- **Durée** : ~7.5s
- **Couverture** : 52% (1450 lignes non couvertes sur 3041)
- **Framework** : Pytest, Django TestCase

#### Résultats Globaux
- **Total Tests** : 409 tests (390 frontend + 19 backend)
- **Tests Réussis** : **409 tests** (390 frontend + 19 backend) ✅
- **Tests Échoués** : **0 tests** ✅
- **Taux de réussite global** : **100%** ✅

### Corrections Appliquées (2025-12-10)

#### Frontend
1. ✅ **Ajout de `EcoModeProvider` dans les tests** (45 tests corrigés)
   - `test-utils.jsx` : Helper `renderWithProviders` mis à jour
   - `router.test.jsx` : Ajout de `EcoModeProvider`
   - `navigation.test.jsx` : Ajout de `EcoModeProvider`
   - `chat-integration.test.jsx` : Ajout de `EcoModeProvider`

2. ✅ **Correction du test `backend-connection`** (1 test corrigé)
   - Mock de `getTokenSecurely` et `isTokenValid` dans `security.js`
   - Vérification du header `Authorization` dans les appels API

#### Backend
1. ✅ **Tests d'administration** (7 tests corrigés)
   - Problème : 403 Forbidden au lieu de 200 OK
   - Cause : Les endpoints admin nécessitent que l'utilisateur appartienne au groupe `Founders_V1_Protection` pour passer la permission `IsFounderOrReadOnly`
   - Solution appliquée :
     - Création de la fonction `grant_founder_permissions()` pour attribuer les permissions fondateur
     - Création d'un utilisateur admin dans le `setUp` avec les permissions fondateur
     - Authentification de cet utilisateur dans tous les tests d'administration avec `self.client.force_login(self.admin_user)`
   - Résultat : **Tous les tests passent** ✅

### Configuration des Tests

#### Frontend
- **Vitest** : 4.0.15 (mise à jour depuis 2.1.9)
- **Setup** : `src/test/setup.js` (mocks, MSW, localStorage)
- **Helpers** : `src/test/test-utils.jsx` (providers complets)
- **Mocks** : `src/test/mocks/server.js` (MSW)

#### Backend
- **Pytest** : Configuration dans `pytest.ini`
- **Conftest** : `conftest.py` (désactivation throttling, `ADMIN_TOKEN`)
- **Tests** : `core/tests.py` (IntentTestCase, ProjetCagnotteTestCase, MessagingVoteTestCase)

---

## 📚 Documentation Complémentaire

- **`FICHE_GLOBALE_EGOEJO.md`** : Fiche technique complète
- **`RESUME_TESTS_COMPLETS.md`** : Résumé détaillé des tests (2025-12-10)
- **`ARCHITECTURE_SLEEPING_GIANT_V1.6_V2.0.md`** : Architecture V1.6/V2.0
- **`AUDIT_CORRECTIONS_CRITIQUES_V2.0.md`** : Corrections sécurité
- **`README.md`** : Documentation principale

---

**Dernière mise à jour** : 2025-12-10  
**Version** : 2.0 (Hybride V1.6 + V2.0)  
**Statut** : ✅ Production Ready ✅ Scale Ready ✅ Async Ready ✅ Intelligence Ready ✅ Connected Ready ✅ Visual Ready ✅ Financial Ready ✅ Investment Ready (Dormant) 💤 Security Hardened 🔒  
**Tests** : ✅ Frontend 100% ✅ Backend 100% ✅ Global 100% (409/409 tests) 🎉

