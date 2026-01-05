# 🔧 CORRECTION DU CONTEXTE REACT QUERY DANS LES TESTS

**Date** : 2026-01-03  
**Mission** : Fix React Query Test Context

---

## ✅ PROBLÈME IDENTIFIÉ

35 tests échouaient avec l'erreur :
```
Error: No QueryClient set, use QueryClientProvider to set one
```

**Cause** : Certains tests utilisaient `render()` directement au lieu de `renderWithProviders()`, ce qui ne fournissait pas le `QueryClientProvider` nécessaire pour les hooks `useQuery`.

---

## 🔧 CORRECTIONS EFFECTUÉES

### 1. Utilitaire de test existant

L'utilitaire `src/test/test-utils.jsx` existait déjà et incluait :
- ✅ `QueryClientProvider` avec une nouvelle instance de `QueryClient` pour chaque test
- ✅ Tous les providers nécessaires (BrowserRouter, LanguageProvider, AuthProvider, etc.)
- ✅ Configuration optimisée pour les tests (pas de retry, cache désactivé)

### 2. Correction des tests défaillants

**Fichier corrigé** : `src/app/pages/__tests__/Contenus.editorial-compliance.test.jsx`

**Changements** :
- ✅ Remplacement de `import { render, screen }` par `import { screen }` + `import { renderWithProviders }`
- ✅ Remplacement de toutes les occurrences de `render(<Contenus />)` par `renderWithProviders(<Contenus />)`

**Lignes corrigées** :
- Ligne 64 : `render(<Contenus />)` → `renderWithProviders(<Contenus />)`
- Ligne 133 : `render(<Contenus />)` → `renderWithProviders(<Contenus />)`
- Ligne 176 : `render(<Contenus />)` → `renderWithProviders(<Contenus />)`

---

## 📊 RÉSULTATS

### Avant les corrections :
- ❌ 35 tests échouaient avec "No QueryClient set"
- ❌ Tests utilisant `useQuery` sans `QueryClientProvider`

### Après les corrections :
- ✅ **Aucune erreur "No QueryClient set"**
- ✅ Tous les tests utilisent `renderWithProviders()` qui inclut `QueryClientProvider`
- ✅ Les tests échouent maintenant pour d'autres raisons (éléments non trouvés, timeouts) mais **le problème de QueryClient est résolu**

---

## 📝 FICHIERS MODIFIÉS

1. `frontend/frontend/src/app/pages/__tests__/Contenus.editorial-compliance.test.jsx`
   - Remplacement de `render` par `renderWithProviders`
   - Ajout de l'import `renderWithProviders`

---

## ✅ STATUT FINAL

**Le problème de `QueryClientProvider` est résolu.**

Tous les tests qui utilisent `useQuery` ou d'autres hooks React Query ont maintenant accès au `QueryClientProvider` via `renderWithProviders()`.

Les tests restants qui échouent le font pour d'autres raisons (éléments DOM non trouvés, timeouts, etc.) et ne sont pas liés au problème de `QueryClient`.

---

## 📚 BONNES PRATIQUES

Pour tous les nouveaux tests utilisant React Query :

1. **Toujours utiliser `renderWithProviders()`** au lieu de `render()`
2. **Importer depuis `test/test-utils`** :
   ```jsx
   import { renderWithProviders } from '../../../test/test-utils';
   ```
3. **Utiliser `renderWithProviders`** :
   ```jsx
   renderWithProviders(<MonComposant />);
   ```

---

**Mission accomplie** ✅

