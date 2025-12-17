# 🔍 Analyse Architecture Frontend - EGOEJO

**Date** : 2025-12-16  
**Objectif** : Analyser l'architecture frontend telle qu'elle est réellement codée

---

## 📦 Configuration (`frontend/frontend/package.json`)

### Scripts Principaux

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

### Dépendances Clés

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
- `msw` ^2.12.3 : Mock Service Worker (tests)

**Note** : Pas de bibliothèque i18n dédiée visible (probablement custom via `utils/i18n.js`)

---

## ⚙️ Configuration Vite (`vite.config.js`)

### Plugins

1. **React** : `@vitejs/plugin-react`
2. **PWA** : `vite-plugin-pwa`
   - Manifest configuré (nom, icônes, thème)
   - Workbox : Cache stratégies (NetworkFirst pour API, CacheFirst pour images/fonts)
   - Runtime caching : Contents (24h), Chat (5 min), API (5 min), Images (30 jours)

### Alias

- `@` → `./src` (ex: `@/components/Layout`)

### Build Optimisations

**Code Splitting** :
- `react-vendor` : React, React-DOM, React Router
- `three-vendor` : Three.js, @react-three/*
- `gsap-vendor` : GSAP
- `vendor` : Autres node_modules

**Compression** :
- `terser` : Minification
- Suppression `console.log` en production
- Source maps désactivés en production

**Chunks** :
- `chunkSizeWarningLimit: 1000` (avertir si > 1MB)

### Tests (Vitest)

**Configuration** :
- Environnement : `jsdom`
- Setup : `./src/test/setup.js`
- Exclusions : `e2e/`, `node_modules/`, `dist/`
- Coverage : Seuils 70% (lignes, fonctions, branches, statements)

---

## 📁 Structure (`frontend/frontend/src/`)

### Point d'Entrée

**Fichier** : `src/main.jsx`

**Structure** :
```jsx
ReactDOM.createRoot(rootElement).render(
  <React.StrictMode>
    <AppWrapper> {/* Easter egg */}
      <EcoModeProvider>
        <NotificationProvider>
          <AuthProvider>
            <LanguageProvider>
              <RouterProvider router={appRouter} />
            </LanguageProvider>
          </AuthProvider>
        </NotificationProvider>
      </EcoModeProvider>
    </AppWrapper>
  </React.StrictMode>
);
```

**Initialisation** :
- Sentry (production uniquement, lazy load)
- Performance tracking
- Monitoring complet

---

### Router (`src/app/router.jsx`)

**Framework** : React Router 7 (`createBrowserRouter`)

**Structure** :
- Layout global avec `<Layout />` et `<PageViewTracker />`
- Lazy loading de toutes les pages (`lazy()`)
- Suspense avec fallback minimal
- ErrorBoundary par page

**Routes Identifiées** (23 routes) :

**Pages Publiques** :
- `/` : Home
- `/univers` : Univers
- `/vision` : Vision
- `/citations` : Citations
- `/alliances` : Alliances
- `/projets` : Projets
- `/contenus` : Contenus
- `/communaute` : Communauté
- `/votes` : Votes
- `/rejoindre` : Rejoindre
- `/racines-philosophie` : Racines Philosophie
- `/mycelium` : Mycelium (3D)
- `/podcast` : Podcast

**Pages Authentifiées** :
- `/login` : Login
- `/register` : Register
- `/dashboard` : Dashboard (Patrimoine Vivant)
- `/my-card` : MyCard
- `/impact` : Impact
- `/chat` : Chat

**Pages Admin** :
- `/admin` : Admin (Intentions)
- `/admin/saka-monitor` : Saka Monitor (Monitoring SAKA)

**Pages SAKA** :
- `/saka/silo` : Saka Silo (Silo Commun)

**404** :
- `*` : NotFound

---

### Pages (`src/app/pages/`)

**Classification par Rôle** :

#### 1. **Accueil & Présentation**
- `Home.jsx` : Page d'accueil
- `Univers.jsx` : Présentation univers
- `Vision.jsx` : Vision du collectif
- `Citations.jsx` : Citations
- `Alliances.jsx` : Alliances
- `RacinesPhilosophie.jsx` : Racines philosophiques

#### 2. **Contenus**
- `Contenus.jsx` : Liste contenus éducatifs
- `Podcast.jsx` : Podcasts

#### 3. **Projets & Engagement**
- `Projets.jsx` : Liste projets (avec boost SAKA)
- `Votes.jsx` : Sondages et votes
- `Rejoindre.jsx` : Formulaire "Rejoindre"

#### 4. **Communauté**
- `Communaute.jsx` : Communauté
- `Chat.jsx` : Chat temps réel

#### 5. **Utilisateur**
- `Dashboard.jsx` : Patrimoine Vivant (liquidités, SAKA, impact)
- `MyCard.jsx` : Carte utilisateur
- `Impact.jsx` : Impact utilisateur
- `Login.jsx` : Connexion
- `Register.jsx` : Inscription

#### 6. **SAKA**
- `SakaSilo.jsx` : Silo Commun (Phase 3)
- `SakaMonitor.jsx` : Monitoring SAKA (admin)

#### 7. **Admin**
- `Admin.jsx` : Panel admin (intentions, filtres, export)

#### 8. **Visualisation 3D**
- `Mycelium.jsx` : Visualisation Mycelium 3D

#### 9. **Erreurs**
- `NotFound.jsx` : 404

---

### Composants (`src/components/`)

**Organisation** :
- `__tests__/` : Tests composants (12 fichiers)
- `dashboard/` : Composants dashboard (`FourPStrip.jsx`)
- `saka/` : Composants SAKA (`SakaSeasonBadge.jsx`)
- `chat/` : Composants chat (`SupportBubble.jsx`)
- `ui/` : Composants UI (`SwipeButton.jsx`)

**Composants Principaux** :
- `Layout.jsx` : Layout global (navbar, menu, footer)
- `Navbar.jsx` : Navigation principale
- `ErrorBoundary.jsx` : Gestion erreurs React
- `Loader.jsx` : Indicateur de chargement
- `Notification.jsx` / `NotificationContainer.jsx` : Système de notifications
- `SEO.jsx` : Gestion SEO (meta tags, JSON-LD)
- `PageTransition.jsx` : Transitions entre pages
- `PageViewTracker.jsx` : Tracking vues pages
- `EcoModeToggle.jsx` : Toggle mode éco
- `OfflineIndicator.jsx` : Indicateur offline
- `LanguageSelector.jsx` : Sélecteur de langue
- `ChatWindow.jsx` / `ChatList.jsx` : Chat temps réel
- `QuadraticVote.jsx` : Composant vote quadratique
- `SemanticSearch.jsx` / `SemanticSuggestions.jsx` : Recherche sémantique
- `MyceliumVisualization.jsx` : Visualisation 3D Mycelium
- `Logo3D.jsx` / `MenuCube3D.jsx` : Éléments 3D
- `HeroSorgho.jsx` / `HeroSorghoLazy.jsx` : Hero sections
- `CardTilt.jsx` : Carte avec effet tilt
- `CustomCursor.jsx` / `CursorSpotlight.jsx` : Curseur personnalisé
- `ScrollProgress.jsx` : Barre de progression scroll
- `OptimizedImage.jsx` : Image optimisée
- `AudioPlayer.jsx` : Lecteur audio
- `Button.jsx` / `Input.jsx` : Composants UI de base

---

### Contextes (`src/contexts/`)

**Contextes React** :
- `AuthContext.jsx` : Authentification (user, token, login, logout)
- `LanguageContext.jsx` : Internationalisation (langue courante)
- `NotificationContext.jsx` : Notifications (showSuccess, showError, etc.)
- `EcoModeContext.jsx` : Mode éco (réduction animations, etc.)

**Pattern** : Provider + Hook (`useAuth()`, `useLanguage()`, etc.)

---

### Hooks (`src/hooks/`)

**Hooks Personnalisés** :

**API** :
- `useGlobalAssets.js` : Assets globaux utilisateur (liquidités, SAKA, impact)
- `useSaka.js` : Hooks SAKA
  - `useSakaSilo()` : État Silo Commun
  - `useSakaCompostPreview()` : Preview compost
  - `useSakaStats()` : Statistiques SAKA (admin)
  - `useSakaCompostLogs()` : Logs compost (admin)
  - `useSakaCompostRun()` : Lancer compost dry-run (admin)
- `useFetch.js` : Fetch générique avec cache
- `useWebSocket.js` : Connexion WebSocket (chat, polls temps réel)
  - Reconnexion automatique avec backoff exponentiel
  - Heartbeat (ping/pong)
  - Gestion token d'authentification

**UI** :
- `useClickOutside.js` : Détecter clic extérieur
- `useDebounce.js` : Debounce valeurs
- `useToggle.js` : Toggle booléen
- `useMediaQuery.js` : Media queries responsive
- `useLocalStorage.js` : LocalStorage avec sync
- `useLowPowerMode.js` : Détection mode faible consommation
- `useEasterEgg.js` : Easter egg
- `useSEO.js` : Gestion SEO dynamique
- `useNotification.js` : Wrapper notifications

---

### Utilitaires (`src/utils/`)

**API & Communication** :
- `api.js` : `fetchAPI()` - Wrapper fetch avec headers sécurité
- `security.js` : Headers sécurité, validation token, sanitization
- `sentry.js` : Configuration Sentry (lazy load en production)
- `monitoring.js` : Monitoring complet (Sentry, métriques, alertes)

**Formatage** :
- `money.js` : Formatage monétaire (`formatMoney()`)
- `format.js` : Formatage générique
- `i18n.js` : Internationalisation (traductions)

**Autres** :
- `logger.js` : Logger structuré
- `analytics.js` : Analytics
- `performance.js` / `performance-metrics.js` : Métriques performance
- `scrollAnimations.js` : Animations scroll
- `validation.js` : Validation formulaires
- `gdpr.js` : Utilitaires GDPR

---

### Internationalisation (`src/locales/`)

**Langues Supportées** :
- `fr.json` : Français
- `en.json` : Anglais
- `es.json` : Espagnol
- `de.json` : Allemand
- `ar.json` : Arabe
- `sw.json` : Swahili

**Utilisation** : `t(key, language)` via `utils/i18n.js`

---

## 🔌 Communication Frontend ↔ Backend

### Méthode Principale : `fetchAPI()`

**Fichier** : `src/utils/api.js`

**Fonction** :
```javascript
export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const securityHeaders = addSecurityHeaders(options.headers);
  const response = await fetch(url, { headers: securityHeaders, ...options });
  // Gestion erreurs, parsing JSON
}
```

**Base URL** :
- Production : `import.meta.env.VITE_API_URL/api`
- Développement : `http://localhost:8000/api`

**Headers Sécurité** :
- Ajout automatique via `addSecurityHeaders()` (`security.js`)
- Token JWT : Géré via `AuthContext` (localStorage)

---

### Hooks API

**Pattern** : Hooks personnalisés qui encapsulent `fetchAPI()`

**Exemples** :
- `useGlobalAssets()` : `GET /api/impact/global-assets/`
- `useSakaSilo()` : `GET /api/saka/silo/`
- `useSakaStats()` : `GET /api/saka/stats/`
- `useSakaCompostPreview()` : `GET /api/saka/compost-preview/`

**Avantages** :
- Réutilisabilité
- Gestion loading/error centralisée
- Refetch facile

---

### WebSockets

**Hook** : `useWebSocket.js`

**Utilisation** :
- Chat temps réel (`ChatWindow.jsx`)
- Sondages temps réel (probablement dans `Votes.jsx`)

**Fonctionnalités** :
- Authentification via token (query param)
- Reconnexion automatique (backoff exponentiel)
- Heartbeat (ping/pong toutes les 30s)
- Gestion erreurs

**URL** : Probablement `ws://` ou `wss://` vers backend Django Channels

---

### Authentification

**Context** : `AuthContext.jsx`

**Méthode** :
- Token JWT stocké dans `localStorage`
- Headers `Authorization: Bearer <token>` ajoutés automatiquement
- Refresh token : Rotation gérée côté backend

**Endpoints** :
- `POST /api/auth/login/` : Connexion
- `POST /api/auth/refresh/` : Refresh token
- `GET /api/auth/me/` : Utilisateur courant
- `POST /api/auth/register/` : Inscription

---

## 🧪 Tests

### Tests Unitaires (Vitest)

**Emplacement** : `src/**/__tests__/`

**Couverture** :
- **Composants** : 12 tests (`Button`, `Layout`, `Navbar`, `ChatWindow`, `FourPStrip`, `SakaSeasonBadge`, etc.)
- **Pages** : 12 tests (`Home`, `Projets`, `Votes`, `Admin`, `Rejoindre`, etc.)
- **Hooks** : 6 tests (`useFetch`, `useDebounce`, `useLocalStorage`, `useMediaQuery`, `useToggle`, `useClickOutside`)
- **Utils** : 6 tests (`api`, `format`, `validation`, `backend-connection`, `integration-backend`, `performance`)
- **Contextes** : 1 test (`AuthContext`)
- **Accessibilité** : 5 tests (`aria`, `contrast`, `keyboard`, `enhanced`)
- **Performance** : 3 tests (`metrics`, `automated`, `lighthouse`)
- **Intégration** : 1 test (`api`)

**Configuration** :
- Environnement : `jsdom`
- Setup : `src/test/setup.js`
- Mocks : `src/test/mocks/server.js` (MSW)
- Coverage : Seuils 70% (configurable à 80%)

---

### Tests E2E (Playwright)

**Emplacement** : `e2e/`

**Fichiers Identifiés** :
- `admin.spec.js` : Tests admin
- `backend-connection.spec.js` : Tests connexion backend
- `contenus.spec.js` : Tests contenus
- `home.spec.js` : Tests page d'accueil
- `navigation.spec.js` : Tests navigation
- `rejoindre.spec.js` : Tests formulaire "Rejoindre"

**Configuration** (`playwright.config.js`) :
- Navigateurs : Chromium, Mobile Chrome
- Timeout : 30s par test
- Retry : 2 tentatives en CI
- Screenshots : Sur échec uniquement
- Trace : Sur retry
- WebServer : Démarre `npm run dev` automatiquement

---

## 📊 Résumé

### Organisation Front

**Architecture** : **SPA React 19 avec React Router 7**

**Structure** :
- **Pages** : 23 pages organisées par rôle (accueil, contenus, projets, admin, SAKA)
- **Composants** : 30+ composants réutilisables (UI, dashboard, SAKA, chat, 3D)
- **Hooks** : 15+ hooks personnalisés (API, UI, WebSocket)
- **Contextes** : 4 contextes (Auth, Language, Notification, EcoMode)
- **Utils** : 15+ utilitaires (API, sécurité, formatage, i18n)

**Patterns** :
- **Lazy Loading** : Toutes les pages chargées à la demande
- **Error Boundaries** : Gestion erreurs par page
- **Hooks API** : Encapsulation `fetchAPI()` dans hooks réutilisables
- **Contextes** : State management via React Context
- **PWA** : Service Workers, manifest, cache stratégies

---

### Communication avec le Backend

**Méthode Principale** : `fetchAPI()` (wrapper fetch)

**Endpoints Utilisés** :
- `/api/auth/*` : Authentification
- `/api/impact/global-assets/` : Assets globaux
- `/api/projets/` : Projets (liste, détail, boost)
- `/api/saka/*` : SAKA (silo, compost, cycles, stats)
- `/api/polls/` : Sondages
- `/api/intents/*` : Intentions
- `/api/chat/*` : Chat
- `/api/contents/` : Contenus éducatifs
- `/api/config/features/` : Feature flags

**WebSockets** :
- Chat temps réel
- Sondages temps réel
- Hook `useWebSocket()` avec reconnexion automatique

**Authentification** :
- JWT stocké dans `localStorage`
- Headers `Authorization` ajoutés automatiquement
- Refresh token géré côté backend

---

### Tests

**Vitest (Unitaires)** :
- **50+ tests** couvrant composants, pages, hooks, utils
- **Couverture** : Seuils 70% (configurable 80%)
- **Mocks** : MSW pour mocker API
- **Accessibilité** : Tests a11y (ARIA, contrast, keyboard)

**Playwright (E2E)** :
- **6 fichiers de tests** (admin, backend, contenus, home, navigation, rejoindre)
- **Navigateurs** : Chromium, Mobile Chrome
- **CI** : Retry automatique, screenshots sur échec

**Scripts** :
- `npm test` : Vitest watch
- `npm run test:run` : Vitest one-shot
- `npm run test:coverage` : Couverture
- `npm run test:e2e` : Playwright
- `npm run test:performance` : Performance
- `npm run test:lighthouse` : Lighthouse CI

---

## 🎯 Points Clés à Retenir

1. **Architecture moderne** : React 19 + Vite 7 + React Router 7
2. **PWA** : Service Workers, manifest, cache stratégies
3. **3D** : Three.js pour visualisations Mycelium
4. **Tests robustes** : Vitest (unitaires) + Playwright (E2E)
5. **Internationalisation** : 6 langues supportées
6. **Sécurité** : Headers sécurité, sanitization, validation
7. **Performance** : Lazy loading, code splitting, optimisations build
8. **Monitoring** : Sentry (production), métriques performance

---

**Dernière mise à jour** : 2025-12-16

