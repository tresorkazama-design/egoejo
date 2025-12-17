# 🗺️ Cartographie du Projet EGOEJO

**Date** : 2025-12-16  
**Objectif** : Vue d'ensemble complète du projet pour un nouveau développeur

---

## 📁 Arborescence Niveau 1-2

```
egoejo/
├── backend/          # Application Django (API REST + WebSockets)
├── frontend/         # Application React (Vite + TypeScript)
├── docs/             # Documentation technique et guides
├── scripts/          # Scripts utilitaires (init DB, etc.)
├── .github/          # GitHub Actions (CI/CD)
├── docker-compose.yml
├── railway.json      # Configuration Railway (déploiement backend)
├── railway.toml      # Configuration Railway
└── README.md
```

---

## 📂 Détail des Dossiers Principaux

### 🔵 `backend/` - Application Django

**Rôle** : API REST + WebSockets, logique métier, base de données

**Structure** :
```
backend/
├── config/              # Configuration Django (settings, urls, asgi, wsgi, celery)
├── core/                # App principale (modèles, API, services, tâches)
├── finance/             # App financière (wallets, transactions, poches)
├── investment/          # App investissement (V2.0 dormant - feature flag)
├── manage.py            # Point d'entrée Django
├── requirements.txt     # Dépendances Python
├── pytest.ini           # Configuration pytest
├── Dockerfile           # Image Docker pour production
├── Dockerfile.railway   # Image Docker spécifique Railway
├── conftest.py          # Configuration pytest globale
└── scripts/             # Scripts utilitaires (mycelium, audio)
```

**Apps Django** :
- **`core`** : App principale (projets, SAKA, chat, polls, contenus, etc.)
- **`finance`** : Système financier unifié (wallets, transactions, poches)
- **`investment`** : Investissement V2.0 (dormant, activable via feature flag)

---

### 🟢 `frontend/` - Application React

**Rôle** : Interface utilisateur, PWA, visualisations 3D

**Structure** :
```
frontend/
├── frontend/            # ⭐ VRAI PROJET FRONTEND (React + Vite)
│   ├── src/             # Code source React
│   ├── public/           # Assets statiques
│   ├── e2e/              # Tests E2E Playwright
│   ├── package.json      # Dépendances et scripts
│   ├── vite.config.js    # Configuration Vite
│   ├── vitest.config.js  # Configuration Vitest
│   └── playwright.config.js
├── admin-panel/         # Panel admin séparé (legacy)
└── [nombreux fichiers .md]  # Documentation frontend
```

**Technologies principales** :
- **React 19** : Framework UI
- **Vite 7** : Build tool
- **React Router 7** : Routing
- **Tailwind CSS 4** : Styling
- **Three.js** : Visualisations 3D (Mycelium)
- **Vitest** : Tests unitaires
- **Playwright** : Tests E2E

---

### 📚 `docs/` - Documentation

**Rôle** : Documentation technique, guides, rapports

**Structure** :
```
docs/
├── architecture/        # Documents d'architecture (SAKA, Scaling, etc.)
├── deployment/          # Guides de déploiement (Railway, Vercel)
├── guides/             # Guides utilisateur et techniques
├── reports/             # Rapports d'analyse et tests
├── security/            # Documentation sécurité
├── tests/               # Documentation tests
├── troubleshooting/      # Guides de dépannage
└── archive/              # Documents archivés
```

---

### ⚙️ `.github/` - CI/CD

**Rôle** : Pipelines GitHub Actions

**Fichiers** :
- `workflows/ci.yml` : Tests continus
- `workflows/cd.yml` : Déploiement continu
- `workflows/test.yml` : Tests automatisés
- `workflows/security-audit.yml` : Audit de sécurité

---

## 🔍 Backend - Détail

### Apps Django

#### 1. **`core`** (App principale)

**Fichiers clés** :
- **Settings** : `backend/config/settings.py`
- **URLs globales** : `backend/config/urls.py` → inclut `core.urls`
- **URLs API** : `backend/core/urls.py` (routes API principales)
- **Tâches Celery** :
  - `core/tasks.py` : Tâches principales (emails, dashboard, etc.)
  - `core/tasks_audio.py` : Génération audio (TTS)
  - `core/tasks_embeddings.py` : Génération embeddings (recherche sémantique)
  - `core/tasks_mycelium.py` : Réduction Mycelium 3D
  - `core/tasks_security.py` : Scan antivirus
- **Modèles** : `backend/core/models/*.py`
  - `projects.py` : Projets, médias
  - `saka.py` : Protocole SAKA (wallets, transactions, cycles, silo)
  - `fundraising.py` : Cagnottes, contributions
  - `polls.py` : Sondages, votes
  - `chat.py` : Chat, threads, messages
  - `content.py` : Contenus éducatifs
  - `impact.py` : Dashboard impact, scores 4P
  - `accounts.py` : Profils utilisateurs
  - `intents.py` : Intentions de rejoindre
  - `moderation.py` : Signalements
  - `audit.py` : Logs d'audit
  - `monitoring.py` : Métriques, alertes
  - `engagement.py` : Engagements
  - `help.py` : Demandes d'aide
  - `common.py` : Utilitaires communs

**Services** : `backend/core/services/`
- `saka.py` : Services SAKA (harvest, spend, compost)
- `saka_stats.py` : Statistiques SAKA (cycles, global, daily)
- `impact_4p.py` : Calcul scores 4P
- `concierge.py` : Support concierge

**API** : `backend/core/api/`
- `projects.py` : CRUD projets, boost SAKA
- `saka_views.py` : Endpoints SAKA (silo, compost, cycles, stats)
- `polls.py` : Sondages, votes quadratiques
- `chat.py` : Chat temps réel
- `impact_views.py` : Dashboard impact, global assets
- `auth_views.py` : Authentification (register, login, me)
- `config_views.py` : Feature flags (V1.6/V2.0/SAKA)
- `search_views.py` : Recherche full-text
- `semantic_search_views.py` : Recherche sémantique (pgvector)
- `mycelium_views.py` : Visualisation 3D Mycelium
- Et 15+ autres endpoints...

**Tests** :
- `core/tests.py` : Tests principaux (25 tests)
- `core/tests_saka.py` : Tests SAKA (concurrence, cycles, compost)

#### 2. **`finance`** (Système financier)

**Rôle** : Wallets, transactions, poches, passes Apple/Google Wallet

**Fichiers** :
- `finance/models.py` : UserWallet, WalletPocket, WalletTransaction
- `finance/services.py` : Services financiers (pledge, transfer)
- `finance/views.py` : API wallets, poches, passes

#### 3. **`investment`** (Investissement V2.0)

**Rôle** : Investissement, actions, KYC (dormant - activable via feature flag)

**Fichiers** :
- `investment/models.py` : ShareholderRegister
- `investment/views.py` : API investissement (protégé par `IsInvestmentFeatureEnabled`)

---

### Configuration Backend

**Settings** : `backend/config/settings.py`
- Feature flags : `ENABLE_INVESTMENT_FEATURES`, `ENABLE_SAKA`, etc.
- Base de données : PostgreSQL (prod) / SQLite (dev)
- Redis : Cache + Channels (WebSockets)
- Stockage : S3/R2 (prod) / Local (dev)
- Celery : Configuration broker Redis
- Sécurité : CORS, CSRF, headers, rate limiting
- JWT : Authentification avec rotation tokens

**URLs** :
- `config/urls.py` : Routes globales (`/api/`, `/admin/`, `/api/health/`)
- `core/urls.py` : Routes API détaillées (inclut router DRF)

**ASGI** : `config/asgi.py` (WebSockets via Channels)
**WSGI** : `config/wsgi.py` (Production)
**Celery** : `config/celery.py` (Configuration tâches asynchrones)

---

## 🎨 Frontend - Détail

### Projet Principal : `frontend/frontend/`

**Package.json - Scripts disponibles** :

**Développement** :
- `npm run dev` : Serveur de développement Vite
- `npm run start` : Alias pour `dev`
- `npm run preview` : Prévisualisation build production

**Build** :
- `npm run build` : Build production optimisé
- `npm run analyze` : Analyse du bundle
- `npm run build:analyze` : Build + analyse performance

**Tests** :
- `npm test` : Tests Vitest (watch mode)
- `npm run test:run` : Tests Vitest (one-shot)
- `npm run test:ui` : Interface UI Vitest
- `npm run test:coverage` : Couverture de code
- `npm run test:coverage:threshold` : Couverture avec seuils (80%)
- `npm run test:a11y` : Tests accessibilité
- `npm run test:integration` : Tests d'intégration backend
- `npm run test:backend` : Tests connexion backend
- `npm run test:e2e` : Tests E2E Playwright
- `npm run test:e2e:ui` : Interface UI Playwright
- `npm run test:e2e:headed` : Tests E2E avec navigateur visible
- `npm run test:e2e:production` : Tests E2E sur production
- `npm run test:performance` : Tests de performance
- `npm run test:lighthouse` : Audit Lighthouse CI
- `npm run test:security` : Audit sécurité npm

**Qualité** :
- `npm run lint` : Linter ESLint
- `npm run lint:fix` : Auto-fix ESLint
- `npm run type-check` : Vérification TypeScript (si configuré)

**Git Hooks** :
- `npm run prepare` : Setup Husky
- `npm run lint-staged` : Lint-staged (pre-commit)

**Dépendances principales** :

**Runtime** :
- `react` ^19.2.0
- `react-dom` ^19.2.0
- `react-router-dom` ^7.9.4
- `@react-three/fiber` ^9.4.0 : 3D (Mycelium)
- `@react-three/drei` ^10.7.6 : Helpers 3D
- `three` ^0.180.0 : Moteur 3D
- `framer-motion` ^12.23.26 : Animations
- `gsap` ^3.13.0 : Animations avancées
- `recharts` ^3.5.1 : Graphiques
- `decimal.js` ^10.6.0 : Calculs décimaux précis
- `qrcode.react` ^4.2.0 : Génération QR codes

**Dev** :
- `vite` ^7.1.11 : Build tool
- `@vitejs/plugin-react` ^5.0.4
- `vitest` ^4.0.15 : Framework de tests
- `@playwright/test` ^1.48.0 : Tests E2E
- `tailwindcss` ^4.1.15 : CSS framework
- `eslint` ^8.57.0 : Linter
- `husky` ^9.1.7 : Git hooks
- `lint-staged` ^15.2.0 : Pre-commit linting

---

## 📊 Résumé Synthétique

### Backend

**Stack** : Django 5 + DRF + Celery + Redis + Channels + PostgreSQL

**Architecture** :
- **Monolithe structuré** avec séparation claire (models/api/services)
- **Feature flags** : V1.6 (dons) / V2.0 (investissement) / SAKA (engagement)
- **Service Layer** : Logique métier isolée dans `core/services/`
- **Sécurité** : Verrous pessimistes, transactions atomiques, tests de concurrence
- **Tâches asynchrones** : Celery pour emails, embeddings, audio, scan antivirus
- **WebSockets** : Chat temps réel via Django Channels
- **Recherche** : Full-text (pg_trgm) + Sémantique (pgvector)

**Apps** :
- `core` : App principale (projets, SAKA, chat, polls, contenus)
- `finance` : Wallets, transactions, poches
- `investment` : Investissement V2.0 (dormant)

**Déploiement** : Railway (PostgreSQL, Redis, workers Celery)

---

### Frontend

**Stack** : React 19 + Vite 7 + Tailwind CSS 4 + Three.js + Vitest + Playwright

**Architecture** :
- **SPA** avec React Router 7
- **PWA** : Service Workers (vite-plugin-pwa)
- **3D** : Visualisations Mycelium avec Three.js
- **Tests** : Vitest (unitaires) + Playwright (E2E)
- **Qualité** : ESLint + Husky + lint-staged

**Scripts** : 30+ scripts (dev, build, test, lint, e2e, performance, security)

**Déploiement** : Vercel (CDN global, edge functions)

---

### Docs

**Organisation** :
- `architecture/` : Documents d'architecture (SAKA, Scaling, Sleeping Giant)
- `deployment/` : Guides Railway, Vercel
- `guides/` : Guides techniques et utilisateur
- `reports/` : Rapports d'analyse et tests
- `security/` : Documentation sécurité
- `tests/` : Documentation tests
- `troubleshooting/` : Guides de dépannage

**Volume** : 100+ fichiers markdown

---

### Pipelines

**GitHub Actions** :
- `ci.yml` : Tests continus (backend + frontend)
- `cd.yml` : Déploiement continu
- `test.yml` : Tests automatisés
- `security-audit.yml` : Audit de sécurité

**Déploiement** :
- **Backend** : Railway (automatique via GitHub)
- **Frontend** : Vercel (automatique via GitHub)

---

## 🎯 Points Clés à Retenir

1. **Architecture "Sleeping Giant"** : Code V2.0 présent mais dormant (feature flag)
2. **Protocole SAKA** : Monnaie d'engagement interne (récolte, plantation, compost)
3. **Service Layer** : Logique métier isolée dans `core/services/`
4. **Tests robustes** : Backend (pytest) + Frontend (Vitest + Playwright)
5. **Documentation complète** : 100+ fichiers markdown organisés
6. **CI/CD** : GitHub Actions + Railway + Vercel

---

**Dernière mise à jour** : 2025-12-16

