# Tests Frontend - EGOEJO

**Stack** : React 19, Vite, Vitest, Playwright, Testing Library  
**Date de mise à jour** : 2025-01-16

---

## 🚀 Comment lancer les tests

### Tests unitaires (Vitest)

```bash
# Depuis le répertoire frontend/frontend/
cd frontend/frontend

# Lancer tous les tests en mode watch
npm test

# Lancer tous les tests une fois
npm run test:run

# Lancer avec interface UI
npm run test:ui

# Lancer avec couverture de code
npm run test:coverage

# Lancer avec seuils de couverture (80%)
npm run test:coverage:threshold

# Lancer un fichier spécifique
npm test src/components/__tests__/Button.test.jsx

# Lancer les tests d'accessibilité
npm run test:a11y

# Lancer les tests d'intégration backend
npm run test:integration
```

### Tests E2E (Playwright)

```bash
# Lancer tous les tests E2E
npm run test:e2e

# Lancer avec interface UI
npm run test:e2e:ui

# Lancer en mode headed (avec navigateur visible)
npm run test:e2e:headed

# Lancer un fichier spécifique
npx playwright test e2e/backend-connection.spec.js

# Lancer les tests de connexion backend
npm run test:e2e:backend

# Lancer en mode debug
npx playwright test --debug
```

### Tests de performance

```bash
# Tests de performance
npm run test:performance

# Tests Lighthouse
npm run test:lighthouse
```

---

## 📦 Structure des tests

### Tests unitaires (Vitest)

**Localisation** : `src/**/__tests__/**/*.test.{js,jsx,ts,tsx}`

**Organisation** :
- `src/app/pages/__tests__/` - Tests des pages
- `src/components/__tests__/` - Tests des composants
- `src/hooks/__tests__/` - Tests des hooks
- `src/contexts/__tests__/` - Tests des contextes
- `src/utils/__tests__/` - Tests des utilitaires
- `src/__tests__/` - Tests d'intégration, accessibilité, performance

**Framework** : Vitest + React Testing Library

**Exemple** :
```javascript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Button } from '../Button';

describe('Button', () => {
  it('devrait afficher le texte', () => {
    render(<Button>Cliquer</Button>);
    expect(screen.getByText('Cliquer')).toBeInTheDocument();
  });
});
```

### Tests E2E (Playwright)

**Localisation** : `e2e/**/*.spec.js`

**Fichiers existants** :
- `e2e/backend-connection.spec.js` - Connexion backend-frontend, parcours "Nouveau membre"
- `e2e/votes-quadratic.spec.js` - Vote quadratique avec SAKA
- `e2e/projects-saka-boost.spec.js` - Boost SAKA d'un projet
- `e2e/auth.spec.js` - Authentification
- `e2e/home.spec.js` - Page d'accueil
- `e2e/navigation.spec.js` - Navigation
- `e2e/rejoindre.spec.js` - Formulaire Rejoindre
- `e2e/admin.spec.js` - Page Admin
- `e2e/contenus.spec.js` - Page Contenus
- `e2e/saka-flow.spec.js` - Flux SAKA

**Framework** : Playwright

**Exemple** :
```javascript
import { test, expect } from '@playwright/test';

test('devrait afficher la page Projets', async ({ page }) => {
  await page.goto('/projets');
  await expect(page.getByTestId('projets-page')).toBeVisible();
});
```

---

## 📋 Parcours E2E couverts

### 1. "Nouveau membre" (`e2e/backend-connection.spec.js`)

**Parcours complet** :
1. Arrive sur `/` (page d'accueil)
2. Navigue vers `/rejoindre` via le lien de navigation
3. Remplit le formulaire (nom, email, profil, message optionnel)
4. Soumet le formulaire
5. Voit un message de succès

**Vérifications** :
- ✅ Page d'accueil chargée (`home-page`)
- ✅ Navigation vers `/rejoindre`
- ✅ Formulaire rempli et soumis
- ✅ Requête API POST `/api/intents/rejoindre/` avec les bonnes données
- ✅ Message de succès affiché

---

### 2. "Vote quadratique avec SAKA" (`e2e/votes-quadratic.spec.js`)

**Parcours complet** :
1. Va sur `/votes`
2. Vérifie la présence du solde SAKA
3. Ajuste l'intensité (slider 1-5)
4. Voit le coût SAKA mis à jour (intensité × 5)
5. Soumet un vote
6. Voit son solde diminuer + message de confirmation

**Vérifications** :
- ✅ Contrôles de vote quadratique affichés
- ✅ Solde SAKA initial affiché
- ✅ Slider d'intensité fonctionnel
- ✅ Coût SAKA calculé correctement
- ✅ Requête API POST `/api/polls/{id}/vote/` avec les bonnes données
- ✅ Solde SAKA mis à jour après le vote
- ✅ Message de confirmation affiché

**Tests** :
- `devrait afficher les contrôles de vote quadratique avec SAKA`
- `devrait soumettre un vote et mettre à jour le solde SAKA`
- `devrait afficher une erreur si le solde SAKA est insuffisant`

---

### 3. "Boost d'un projet avec SAKA" (`e2e/projects-saka-boost.spec.js`)

**Parcours complet** :
1. Va sur `/projets`
2. Sélectionne un projet
3. Clique sur "Nourrir ce projet (−10 SAKA)"
4. Confirme (pas de modal de confirmation actuellement)
5. Voit le score SAKA du projet augmenter

**Vérifications** :
- ✅ Liste des projets affichée
- ✅ Score SAKA du projet affiché
- ✅ Bouton "Nourrir ce projet" présent et activé
- ✅ Requête API POST `/api/projets/{id}/boost/` avec `amount: 10`
- ✅ Score SAKA mis à jour (ex: 50 → 60)
- ✅ Notification de succès affichée
- ✅ Nombre de supporters augmenté
- ✅ Solde SAKA utilisateur diminué (100 → 90)

**Tests** :
- `devrait afficher la liste des projets avec les boutons de boost SAKA`
- `devrait booster un projet avec SAKA et voir le score augmenter`
- `devrait désactiver le bouton de boost si le solde SAKA est insuffisant`
- `devrait afficher une erreur si le boost échoue`

---

## 📊 Couverture des tests unitaires

### Pages testées (`src/app/pages/__tests__/`)

| Page | Fichier | Statut | Couverture |
|------|---------|--------|------------|
| **Home** | `Home.test.jsx` | ✅ | Complète |
| **Rejoindre** | `Rejoindre.test.jsx` | ✅ | Complète |
| **Admin** | `Admin.test.jsx` | ✅ | Complète |
| **Votes** | `Votes.test.jsx` | ✅ | Complète |
| **Contenus** | `Contenus.test.jsx` | ✅ | Basique |
| **Alliances** | `Alliances.test.jsx` | ✅ | Basique |
| **Communaute** | `Communaute.test.jsx` | ✅ | Basique |
| **Vision** | `Vision.test.jsx` | ✅ | Basique |
| **Projets** | `Projets.test.jsx` | ✅ | Basique (manque boost SAKA) |
| **Univers** | `Univers.test.jsx` | ✅ | Basique |
| **NotFound** | `NotFound.test.jsx` | ✅ | Complète |
| **Chat** | `Chat.test.jsx` | ✅ | Complète |
| **SakaSeasons** | `SakaSeasons.test.tsx` | ✅ | Complète |
| **Dashboard** | ❌ | 🔴 **MANQUANT** | Critique |
| **SakaMonitor** | ❌ | 🔴 **MANQUANT** | Critique |
| **SakaSilo** | ❌ | 🟡 **MANQUANT** | Important |
| **Login** | ❌ | 🟡 **MANQUANT** | Important |
| **Register** | ❌ | 🟡 **MANQUANT** | Important |
| **Impact** | ❌ | 🟡 **MANQUANT** | Important |

### Composants testés (`src/components/__tests__/`)

| Composant | Fichier | Statut | Couverture |
|-----------|---------|--------|------------|
| **FourPStrip** | `FourPStrip.test.jsx` | ✅ | Complète |
| **SakaSeasonBadge** | `SakaSeasonBadge.test.jsx` | ✅ | Complète |
| **Button** | `Button.test.jsx` | ✅ | Complète |
| **Input** | `Input.test.jsx` | ✅ | Complète |
| **Navbar** | `Navbar.test.jsx` | ✅ | Complète |
| **Layout** | `Layout.test.jsx` | ✅ | Complète |
| **Loader** | `Loader.test.jsx` | ✅ | Complète |
| **ErrorBoundary** | `ErrorBoundary.test.jsx` | ✅ | Complète |
| **ChatWindow** | `ChatWindow.test.jsx` | ✅ | Complète |
| **ChatList** | `ChatList.test.jsx` | ✅ | Complète |
| **FullscreenMenu** | `FullscreenMenu.test.jsx` | ✅ | Complète |
| **CustomCursor** | `CustomCursor.test.jsx` | ✅ | Complète |
| **UserImpact4P** | ❌ | 🔴 **MANQUANT** | Critique |
| **Impact4PCard** | ❌ | 🔴 **MANQUANT** | Critique |
| **QuadraticVote** | ❌ | 🟡 **MANQUANT** | Important |
| **SemanticSearch** | ❌ | 🟡 **MANQUANT** | Important |
| **Notification** | ❌ | 🟡 **MANQUANT** | Important |
| **NotificationContainer** | ❌ | 🟡 **MANQUANT** | Important |

### Hooks testés (`src/hooks/__tests__/`)

| Hook | Fichier | Statut | Couverture |
|------|---------|--------|------------|
| **useFetch** | `useFetch.test.js` | ✅ | Complète |
| **useLocalStorage** | `useLocalStorage.test.js` | ✅ | Complète |
| **useDebounce** | `useDebounce.test.js` | ✅ | Complète |
| **useToggle** | `useToggle.test.js` | ✅ | Complète |
| **useMediaQuery** | `useMediaQuery.test.js` | ✅ | Complète |
| **useClickOutside** | `useClickOutside.test.jsx` | ✅ | Complète |
| **useGlobalAssets** | ❌ | 🔴 **MANQUANT** | Critique |
| **useSaka** | ❌ | 🔴 **MANQUANT** | Critique |
| **useSakaSilo** | ❌ | 🔴 **MANQUANT** | Critique |
| **useSakaCycles** | ❌ | 🔴 **MANQUANT** | Critique |
| **useNotification** | ❌ | 🟡 **MANQUANT** | Important |
| **useSEO** | ❌ | 🟡 **MANQUANT** | Important |
| **useWebSocket** | ❌ | 🟡 **MANQUANT** | Important |

### Tests d'intégration (`src/__tests__/`)

- ✅ **API Integration** : `integration/api.test.jsx`
- ✅ **Router** : `app/__tests__/router.test.jsx`
- ✅ **Navigation** : `app/__tests__/navigation.test.jsx`
- ✅ **Chat Integration** : `app/__tests__/chat-integration.test.jsx`
- ✅ **Accessibility** : `accessibility/*.test.jsx` (4 fichiers)
- ✅ **Performance** : `performance/*.test.js` (3 fichiers)

---

## 🎯 Plan de complétion

Voir `docs/tests/AUDIT_TESTS_FRONTEND_2025-01-16.md` pour le plan détaillé.

### Priorité 🔴 (Critique - 9 fichiers)

1. `src/app/pages/__tests__/Dashboard.test.jsx`
2. `src/app/pages/__tests__/SakaMonitor.test.jsx`
3. `src/app/pages/__tests__/SakaSilo.test.jsx`
4. `src/components/__tests__/UserImpact4P.test.jsx`
5. `src/components/__tests__/Impact4PCard.test.jsx`
6. `src/hooks/__tests__/useGlobalAssets.test.js`
7. `src/hooks/__tests__/useSaka.test.js`
8. `src/hooks/__tests__/useSakaSilo.test.ts`
9. `src/hooks/__tests__/useSakaCycles.test.ts`

### Priorité 🟡 (Important - 14 fichiers)

10. `src/app/pages/__tests__/Login.test.jsx`  
11. `src/app/pages/__tests__/Register.test.jsx`  
12. `src/app/pages/__tests__/Impact.test.jsx`  
13. `src/components/__tests__/QuadraticVote.test.jsx`  
14. `src/components/__tests__/SemanticSearch.test.jsx`  
15. `src/components/__tests__/Notification.test.jsx`  
16. `src/components/__tests__/NotificationContainer.test.jsx`  
17. `src/hooks/__tests__/useNotification.test.js`  
18. `src/hooks/__tests__/useSEO.test.js`  
19. `src/hooks/__tests__/useWebSocket.test.js`  
20. `src/contexts/__tests__/LanguageContext.test.jsx`  
21. `src/contexts/__tests__/NotificationContext.test.jsx`  
22. `src/utils/__tests__/money.test.js`  
23. `src/utils/__tests__/i18n.test.js`

---

## 📝 Règles et bonnes pratiques

### Règles strictes

1. **Ne jamais modifier la logique métier depuis les tests**
   - Les tests doivent révéler des bugs, pas les masquer
   - Si un test échoue, corriger le bug dans le code métier, pas dans le test

2. **Tests rapides et isolés**
   - Chaque test doit être indépendant
   - Utiliser des mocks pour les APIs externes
   - Utiliser MSW (Mock Service Worker) pour les appels API

3. **Utiliser les `data-testid` existants**
   - Ne pas utiliser de sélecteurs CSS fragiles
   - Ajouter des `data-testid` si nécessaire pour les tests E2E

4. **Mocking approprié**
   - Mocker les appels API avec `page.route()` dans Playwright
   - Utiliser MSW pour les tests Vitest
   - Ne pas mocker les hooks/composants internes sauf si nécessaire

### Fixtures et helpers

**Vitest** :
- `renderWithProviders` : Helper pour rendre des composants avec les providers (Auth, Language, Notification)
- `test-utils.jsx` : Utilitaires de test (mocks, helpers)

**Playwright** :
- `beforeEach` : Configuration commune (mocks, authentification)
- `page.route()` : Mock des APIs
- `page.addInitScript()` : Injection de scripts (localStorage, etc.)

**Exemple de mock API (Playwright)** :
```javascript
await page.route('**/api/impact/global-assets/', async (route) => {
  await route.fulfill({
    status: 200,
    contentType: 'application/json',
    body: JSON.stringify({
      saka: { balance: 100 },
    }),
  });
});
```

---

## 🔧 Configuration

### Vitest

**Fichier** : `vite.config.js` ou `vitest.config.js`

**Configuration** :
- Environnement : `jsdom` pour simuler le DOM
- Setup : `src/test/setup.js`
- Mocks : `src/test/mocks/` (MSW handlers)

### Playwright

**Fichier** : `playwright.config.js`

**Configuration** :
- Navigateurs : Chromium, Firefox, WebKit
- Base URL : `http://localhost:5173` (Vite dev server)
- Timeout : 30s par défaut
- Screenshots : Activés en cas d'échec

---

## 🎨 Tests d'accessibilité

**Fichiers** : `src/__tests__/accessibility/*.test.jsx`

**Couverture** :
- ✅ ARIA attributes (`aria.test.jsx`)
- ✅ Contraste des couleurs (`contrast.test.jsx`)
- ✅ Navigation au clavier (`keyboard.test.jsx`)
- ✅ Tests améliorés (`enhanced.test.jsx`)

**Lancer** :
```bash
npm run test:a11y
```

---

## 📊 Tests de performance

**Fichiers** : `src/__tests__/performance/*.test.js`

**Couverture** :
- ✅ Métriques de performance (`metrics.test.js`)
- ✅ Tests automatisés (`automated.test.js`)
- ✅ Tests Lighthouse (`lighthouse.test.js`)

**Lancer** :
```bash
npm run test:performance
npm run test:lighthouse
```

---

## 🔍 Dépannage

### Erreurs courantes

**`Cannot find module`** :
- Vérifier que les imports sont corrects
- Vérifier que les alias Vite sont configurés (`@/`, `@components/`, etc.)

**`Element not found`** :
- Utiliser `waitFor` avec un timeout approprié
- Vérifier que les `data-testid` sont présents dans le code

**Tests flaky (parfois passent, parfois échouent)** :
- Ajouter des `waitFor` pour attendre les mises à jour asynchrones
- Vérifier que les mocks sont correctement configurés
- Utiliser `waitForLoadState('networkidle')` dans Playwright

**Erreurs de mock API** :
- Vérifier que les routes sont correctement interceptées
- Vérifier que les handlers MSW sont correctement configurés
- Vérifier que les URLs mockées correspondent aux URLs réelles

**Tests E2E trop lents** :
- Utiliser `page.waitForLoadState('networkidle')` au lieu de `waitForTimeout`
- Réduire les timeouts si possible
- Utiliser `page.route()` pour mocker les APIs au lieu d'attendre les vraies réponses

---

## 📚 Ressources

- **Documentation Vitest** : https://vitest.dev/
- **Documentation Playwright** : https://playwright.dev/
- **React Testing Library** : https://testing-library.com/react
- **MSW (Mock Service Worker)** : https://mswjs.io/
- **Audit complet** : `docs/tests/AUDIT_TESTS_FRONTEND_2025-01-16.md`

---

## 📈 Statistiques

- **Tests unitaires existants** : ~51 fichiers
- **Tests E2E existants** : 10 fichiers
- **Taux de couverture estimé** : ~60% (pages critiques), ~40% (composants critiques), ~30% (hooks critiques)
- **Tests manquants (critique)** : 9 fichiers
- **Tests manquants (important)** : 14 fichiers

