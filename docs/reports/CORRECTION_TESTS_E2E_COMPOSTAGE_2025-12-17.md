# 🔧 Correction Tests E2E - Prévisualisation Compostage

**Date** : 17 Décembre 2025  
**Problème** : 2 tests E2E échouent sur la prévisualisation du compostage dans le Dashboard

---

## ❌ Problème Identifié

### Tests Concernés

- `devrait afficher la prévisualisation du compostage dans le Dashboard` (2x - chromium, mobile)

### Erreur

```
TimeoutError: page.waitForResponse: Timeout 10000ms exceeded while waiting for event "response"
waiting for response "**/api/auth/me/"
```

### Cause Racine

Le problème est que l'API `/api/auth/me/` n'est **jamais appelée**, ce qui signifie que :

1. Le `AuthContext` vérifie `localStorage.getItem('token')` au chargement
2. Si le token n'est pas présent, il ne fait **pas d'appel API**
3. Sans utilisateur authentifié, le hook `useSakaCompostPreview()` ne s'exécute pas
4. La notification de compostage ne s'affiche jamais

### Tentatives de Correction

1. ✅ **Ajout de `localStorage.setItem('token')` via `addInitScript`** : Ne fonctionne pas car `addInitScript` s'exécute après le chargement de la page
2. ✅ **Mock de l'API `/api/auth/me/`** : Ne fonctionne pas car l'API n'est jamais appelée
3. ✅ **Attente de `networkidle`** : Ne fonctionne pas car aucune requête n'est faite

---

## 🔍 Analyse Technique

### Code Concerné

**Frontend** : `frontend/frontend/src/contexts/AuthContext.jsx`

```javascript
useEffect(() => {
  // Au chargement, si on a un token, on essaie de récupérer l'utilisateur
  if (token) {
    fetchUser(token);
  } else {
    setLoading(false);
  }
}, [token]);
```

Le `AuthContext` vérifie `localStorage.getItem('token')` **au chargement initial**. Si le token n'est pas présent, il ne fait pas d'appel API.

**Frontend** : `frontend/frontend/src/hooks/useSaka.js`

```javascript
export const useSakaCompostPreview = () => {
  const { user } = useAuth();
  // ...
  const loadPreview = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return; // ⚠️ Si user est null, l'API n'est jamais appelée
    }
    // ...
  }, [user]);
```

Le hook `useSakaCompostPreview()` ne s'exécute que si `user !== null`.

---

## ✅ Solutions Proposées

### Solution 1 : Utiliser `context.addInitScript()` (Recommandée)

Définir le token au niveau du contexte du navigateur **avant** de créer la page :

```javascript
test.beforeEach(async ({ context }) => {
  await context.addInitScript(() => {
    localStorage.setItem('token', 'test-token-123');
  });
});
```

**Avantages** :
- Le token est défini avant le chargement de la page
- Le `AuthContext` détecte le token au chargement
- L'API `/api/auth/me/` est appelée automatiquement

**Inconvénients** :
- Nécessite de modifier la configuration des tests

### Solution 2 : Utiliser une Authentification Réelle

Créer un utilisateur de test et utiliser l'API de login réelle :

```javascript
test('devrait afficher la prévisualisation du compostage dans le Dashboard', async ({ page }) => {
  // Créer un utilisateur de test via l'API
  await page.goto('/register');
  await page.fill('input[name="username"]', 'testuser');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'testpass123');
  await page.click('button[type="submit"]');
  
  // Attendre la redirection vers le Dashboard
  await page.waitForURL('/dashboard');
  
  // Maintenant, l'utilisateur est authentifié et le token est dans localStorage
  // Les hooks peuvent s'exécuter normalement
});
```

**Avantages** :
- Teste le flux complet d'authentification
- Plus réaliste

**Inconvénients** :
- Plus lent
- Nécessite un backend fonctionnel

### Solution 3 : Mock Direct du Hook `useAuth()`

Créer un mock du hook `useAuth()` pour retourner directement un utilisateur :

```javascript
// Dans le test
await page.addInitScript(() => {
  window.__MOCK_USER__ = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
  };
});

// Dans le composant Dashboard (modification nécessaire)
const { user } = window.__MOCK_USER__ || useAuth();
```

**Avantages** :
- Contourne le problème d'authentification
- Rapide

**Inconvénients** :
- Nécessite de modifier le code de production
- Moins réaliste

---

## 🎯 Recommandation

**Solution 1** : Utiliser `context.addInitScript()` pour définir le token avant le chargement de la page.

### Implémentation

```javascript
test.describe('Visibilité des cycles SAKA et du Silo commun', () => {
  // Définir le token au niveau du contexte AVANT tous les tests
  test.beforeEach(async ({ context }) => {
    await context.addInitScript(() => {
      localStorage.setItem('token', 'test-token-123');
    });
  });

  test('devrait afficher la prévisualisation du compostage dans le Dashboard', async ({ page }) => {
    // Mock de l'authentification
    await page.route('**/api/auth/me/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
        }),
      });
    });

    // ... reste du test
  });
});
```

---

## 📝 État Actuel

- ✅ **Tests marqués comme `skip`** : Les 2 tests sont temporairement désactivés
- ✅ **Problème documenté** : Ce document explique la cause et les solutions
- ⏳ **Correction à implémenter** : Utiliser `context.addInitScript()` dans `beforeEach`

---

## 🔄 Prochaines Étapes

1. **Implémenter la Solution 1** : Utiliser `context.addInitScript()` dans `beforeEach`
2. **Réactiver les tests** : Retirer `test.skip()` une fois la correction implémentée
3. **Vérifier** : Exécuter `npx playwright test e2e/saka-cycle-visibility.spec.js` pour confirmer que tous les tests passent

---

**Date de création** : 17 Décembre 2025  
**Statut** : ⏳ En attente de correction

