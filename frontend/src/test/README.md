# Tests Frontend - EGOEJO

## Configuration

Les tests utilisent :
- **Vitest** : Framework de test rapide
- **Testing Library** : Utilitaires pour tester React
- **jsdom** : Environnement DOM simulé

## Structure

```
src/
├── test/
│   ├── setup.js          # Configuration globale des tests
│   └── README.md         # Ce fichier
├── contexts/
│   └── __tests__/
│       └── AuthContext.test.jsx  # Tests du contexte d'authentification
└── ...
```

## Commandes

```bash
# Lancer les tests en mode watch
npm test

# Lancer les tests une fois
npm run test:run

# Lancer avec interface UI
npm run test:ui

# Lancer avec couverture de code
npm run test:coverage
```

## Écrire des Tests

### Exemple de test de composant

```jsx
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MyComponent } from '../MyComponent';

describe('MyComponent', () => {
  it('devrait afficher le texte', () => {
    render(<MyComponent />);
    expect(screen.getByText('Hello')).toBeInTheDocument();
  });
});
```

### Exemple de test de hook

```jsx
import { describe, it, expect } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useMyHook } from '../useMyHook';

describe('useMyHook', () => {
  it('devrait retourner la valeur initiale', () => {
    const { result } = renderHook(() => useMyHook());
    expect(result.current.value).toBe(0);
  });
});
```

## Bonnes Pratiques

1. **Un test = une assertion principale**
2. **Nommer les tests clairement** : "devrait faire X quand Y"
3. **Isoler les tests** : Chaque test doit être indépendant
4. **Mocker les dépendances externes** : fetch, localStorage, etc.
5. **Nettoyer après chaque test** : Utiliser `afterEach` si nécessaire

## Couverture

Objectif : **80%+ de couverture**

Vérifier la couverture :
```bash
npm run test:coverage
```

