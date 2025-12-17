# 🧪 Guide des Tests - EGOEJO Frontend

Ce document explique comment utiliser les différents types de tests disponibles dans le projet.

---

## 📊 Tests Unitaires et d'Intégration (Vitest)

### Commandes Disponibles

```bash
# Lancer les tests en mode watch
npm test

# Lancer les tests une fois
npm run test:run

# Interface graphique
npm run test:ui

# Avec couverture de code
npm run test:coverage
```

### Structure des Tests

Les tests sont organisés dans des dossiers `__tests__` à côté des fichiers qu'ils testent :

```
src/
├── app/
│   ├── pages/
│   │   └── __tests__/
│   │       ├── Home.test.jsx
│   │       └── Rejoindre.test.jsx
├── components/
│   └── __tests__/
│       └── Button.test.jsx
└── hooks/
    └── __tests__/
        └── useFetch.test.js
```

### Couverture de Code

La couverture est configurée avec des seuils minimums :
- **Lines** : 70%
- **Functions** : 70%
- **Branches** : 70%
- **Statements** : 70%

Le rapport HTML est généré dans `coverage/index.html`.

---

## ♿ Tests d'Accessibilité

### Installation

Les dépendances sont déjà installées :
- `jest-axe` - Outil de test d'accessibilité
- `@axe-core/react` - Intégration React

### Exécution

```bash
# Lancer uniquement les tests d'accessibilité
npm run test:a11y
```

### Tests Disponibles

- ✅ Tests de toutes les pages principales
- ✅ Tests des composants réutilisables
- ✅ Tests de navigation au clavier
- ✅ Vérification des labels ARIA
- ✅ Vérification du contraste

### Exemple

```javascript
import { render } from '@testing-library/react';
import { axe } from 'jest-axe';

it('devrait être accessible', async () => {
  const { container } = render(<MonComposant />);
  const results = await axe(container);
  expect(results.violations).toHaveLength(0);
});
```

---

## 🎭 Tests E2E (End-to-End) avec Playwright

### Installation

Playwright est déjà installé. Pour installer les navigateurs :

```bash
npx playwright install
```

### Commandes Disponibles

```bash
# Lancer tous les tests E2E
npm run test:e2e

# Interface graphique Playwright
npm run test:e2e:ui

# Tests avec navigateur visible
npm run test:e2e:headed

# Tests sur un navigateur spécifique
npx playwright test --project=chromium
```

### Structure des Tests E2E

Les tests E2E sont dans le dossier `e2e/` :

```
e2e/
├── home.spec.js        # Tests de la page d'accueil
├── rejoindre.spec.js   # Tests du formulaire
└── navigation.spec.js   # Tests de navigation
```

### Navigateurs Testés

- ✅ Chromium (Chrome/Edge)
- ✅ Firefox
- ✅ WebKit (Safari)
- ✅ Chrome Mobile
- ✅ Safari Mobile

### Exemple de Test

```javascript
import { test, expect } from '@playwright/test';

test('devrait charger la page', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/EGOEJO/i);
});
```

---

## ⚡ Analyse de Performance

### Analyse des Bundles

```bash
# Analyser la taille des bundles
npm run analyze
```

Cette commande génère un rapport visuel de la taille des bundles.

### Utilitaires de Performance

Le fichier `src/utils/performance.js` contient des utilitaires :

- `lazyLoadImage()` - Chargement paresseux des images
- `debounce()` - Limiter les appels de fonctions
- `throttle()` - Throttler les appels
- `preloadResource()` - Précharger des ressources
- `measurePerformance()` - Mesurer les performances
- `createCache()` - Cache en mémoire

---

## 📈 CI/CD

### GitHub Actions

Les tests sont automatiquement exécutés sur :
- ✅ Push sur `main` et `develop`
- ✅ Pull Requests
- ✅ Déclenchement manuel

**Workflows disponibles :**
- Tests unitaires et d'intégration
- Tests d'accessibilité
- Tests E2E
- Analyse de couverture

---

## 🐛 Debugging

### Tests Unitaires

```bash
# Mode watch avec logs détaillés
npm test -- --reporter=verbose

# Tester un fichier spécifique
npm test -- src/components/__tests__/Button.test.jsx
```

### Tests E2E

```bash
# Mode debug avec interface
npm run test:e2e:ui

# Mode headed (navigateur visible)
npm run test:e2e:headed

# Traces pour debugging
npx playwright test --trace on
```

---

## 📝 Bonnes Pratiques

### Écriture de Tests

1. **Nommage clair** : `devrait [action] quand [condition]`
2. **Un test = une assertion principale**
3. **Tests indépendants** : chaque test doit pouvoir s'exécuter seul
4. **Mock approprié** : utiliser MSW pour les API

### Accessibilité

1. **Tester toutes les pages** lors de leur création
2. **Vérifier la navigation clavier**
3. **Valider les labels ARIA**
4. **Tester avec des lecteurs d'écran** (manuellement)

### E2E

1. **Tester les flux critiques** utilisateur
2. **Tester sur plusieurs navigateurs**
3. **Tester sur mobile**
4. **Éviter les tests fragiles** (attendre des sélecteurs stables)

---

## 🎯 Objectifs de Couverture

- **Actuel** : ~70% (estimé)
- **Cible** : 80% minimum
- **Idéal** : 90%+

---

## 📚 Ressources

- [Vitest Documentation](https://vitest.dev/)
- [Testing Library](https://testing-library.com/)
- [Playwright Documentation](https://playwright.dev/)
- [jest-axe Documentation](https://github.com/nickcolley/jest-axe)
- [Web Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

---

*Document mis à jour le 2025-01-27*

