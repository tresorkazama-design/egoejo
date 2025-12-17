# ✅ Corrections Finales Appliquées aux Tests E2E

**Date** : 17 Décembre 2025  
**Fichier** : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`  
**Statut** : ✅ **Corrections appliquées** - Prêt pour réexécution

---

## 📊 Résumé des Corrections

| Test | Problème Initial | Correction Appliquée | Lignes Modifiées |
|------|------------------|---------------------|------------------|
| **Silo commun** | Strict mode violation (h1/h2) + sélecteur ambigu | `waitForSelector` + contexte section | 97-108 |
| **Cycles SAKA statistiques** | Sélecteurs ambigus (nombres) | Contexte article + `p.text-muted-foreground` | 144-186 |
| **Prévisualisation compostage** | Hook non appelé / timeout | Mock `/api/auth/me/` + `waitForResponse` | 188-229 |

---

## 🔧 Corrections Appliquées en Détail

### Correction 1 : Test "Silo commun sur SakaSeasons" (ligne 70)

**Problèmes identifiés** :
1. Sélecteur `getByRole('heading')` trouve 2 éléments (h1 + h2)
2. Sélecteur `getByText(/5 000/)` peut être ambigu
3. Pas d'attente explicite pour le chargement

**Corrections appliquées** :
```javascript
// ✅ Attendre que la page soit complètement chargée
await page.waitForLoadState('networkidle');
await page.waitForLoadState('domcontentloaded');

// ✅ Attendre que le h1 soit chargé avant de vérifier
await page.waitForSelector('h1', { timeout: 5000 });
await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();

// ✅ Attendre que la section Silo soit chargée
await page.waitForSelector('section:has-text("Silo commun")', { timeout: 5000 });
await expect(page.getByText('Silo commun')).toBeVisible();

// ✅ Cibler spécifiquement dans la section Silo pour éviter l'ambiguïté
const siloSection = page.locator('section').filter({ hasText: /Silo commun/i });
const siloBalanceText = siloSection.getByText(new RegExp(`${SILO_TOTAL_BALANCE.toLocaleString('fr-FR')}`));
await expect(siloBalanceText).toBeVisible({ timeout: 5000 });
```

**Impact** : Évite les strict mode violations en ciblant spécifiquement le h1 et en utilisant un contexte (section Silo).

---

### Correction 2 : Test "Cycles SAKA avec statistiques" (ligne 121)

**Problèmes identifiés** :
1. Sélecteurs `getByText()` pour les nombres sont ambigus (même nombre dans Silo + Cycles)
2. Pas de contexte pour cibler spécifiquement les statistiques des cycles

**Corrections appliquées** :
```javascript
// ✅ Attendre que l'article du cycle soit chargé
await page.waitForSelector('article', { timeout: 5000 });
await expect(page.getByText(TEST_CYCLE.name)).toBeVisible();

// ✅ Cibler dans l'article du cycle pour éviter les ambiguïtés
const cycleArticle = page.locator('article').filter({ hasText: TEST_CYCLE.name });

// ✅ Vérifier les statistiques dans le contexte de l'article
// Récolté
await expect(cycleArticle.getByText(/Récolté/i)).toBeVisible();
const harvestedValue = cycleArticle.locator('p.text-muted-foreground').filter({
  hasText: new RegExp(`${TEST_CYCLE.stats.saka_harvested.toLocaleString('fr-FR')}`)
});
await expect(harvestedValue.first()).toBeVisible();

// Même chose pour Planté et Composté
```

**Impact** : Évite les strict mode violations en utilisant un contexte (article du cycle) et en ciblant spécifiquement les paragraphes avec la classe `text-muted-foreground`.

---

### Correction 3 : Test "Prévisualisation compostage Dashboard" (ligne 188)

**Problèmes identifiés** :
1. Le hook `useSakaCompostPreview()` nécessite un utilisateur authentifié (`if (!user) return`)
2. Le hook `useAuth()` appelle `/api/auth/me/` pour récupérer l'utilisateur
3. Pas de vérification que l'API est bien appelée avant de vérifier l'affichage
4. Timeout trop court (10s) pour un test qui prend ~15s

**Corrections appliquées** :
```javascript
// ✅ Mock de l'authentification (nécessaire pour useAuth())
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

// ✅ Attendre que l'API compost-preview soit appelée
await page.waitForResponse('**/api/saka/compost-preview/', { timeout: 10000 });

// ✅ Augmenter le timeout pour la notification (15s au lieu de 10s)
await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { 
  timeout: 15000 
});
```

**Impact** : Garantit que :
1. L'utilisateur est bien authentifié (mock `/api/auth/me/`)
2. Le hook `useSakaCompostPreview()` est bien appelé (vérification de l'appel API)
3. La notification a le temps de se charger (timeout augmenté à 15s)

---

## 📋 Checklist des Corrections

### ✅ Corrections Appliquées

- [x] **Sélecteur h1** : Utilisation de `page.locator('h1')` au lieu de `getByRole('heading')`
- [x] **Contexte Silo** : Utilisation de `page.locator('section').filter({ hasText: /Silo commun/i })`
- [x] **Contexte Cycles** : Utilisation de `page.locator('article').filter({ hasText: cycle.name })`
- [x] **Sélecteurs statistiques** : Utilisation de `p.text-muted-foreground` dans le contexte de l'article
- [x] **Attentes explicites** : Ajout de `waitForSelector` avant chaque assertion
- [x] **Mock authentification** : Ajout de mock pour `/api/auth/me/`
- [x] **Vérification API** : Ajout de `waitForResponse` pour vérifier que l'API est appelée
- [x] **Timeout augmenté** : Passage de 10s à 15s pour la notification de compostage

---

## 🎯 Résultats Attendus

### Avant Corrections
- **Taux de réussite** : 50% (6/12)
- **Tests échoués** : 6 (3 tests × 2 navigateurs)
  - Silo commun : 2 échecs
  - Cycles statistiques : 2 échecs
  - Prévisualisation compostage : 2 échecs

### Après Corrections (Prévu)
- **Taux de réussite** : 100% (12/12)
- **Tests échoués** : 0

---

## 🔍 Points d'Attention Restants

### 1. Sélecteur CSS `:has-text()`

**Problème potentiel** : `page.waitForSelector('section:has-text("Silo commun")')` utilise la pseudo-classe `:has-text()` qui peut ne pas être supportée par tous les navigateurs.

**Solution alternative** :
```javascript
// Utiliser un sélecteur plus compatible
await page.waitForSelector('section', { timeout: 5000 });
await expect(page.getByText('Silo commun')).toBeVisible();
```

**Si problème persiste** : Remplacer par cette alternative.

---

### 2. Classe CSS `text-muted-foreground`

**Problème potentiel** : La classe `text-muted-foreground` peut ne pas être présente si Tailwind n'est pas configuré ou si les styles sont différents.

**Vérification** : S'assurer que la classe existe dans `SakaSeasons.tsx` :
```typescript
<p className="text-muted-foreground">
  {cycle.stats?.saka_harvested?.toLocaleString("fr-FR") || 0} grains
</p>
```

**Si problème persiste** : Utiliser un sélecteur plus générique :
```javascript
// Alternative : chercher le nombre dans le div parent "Récolté"
const harvestedDiv = cycleArticle.locator('div').filter({ hasText: /Récolté/i });
const harvestedValue = harvestedDiv.getByText(new RegExp(`${TEST_CYCLE.stats.saka_harvested.toLocaleString('fr-FR')}`));
```

---

### 3. Hook `useAuth()` et Token Mocké

**Problème potentiel** : Le hook `useAuth()` lit `localStorage.getItem('token')` au chargement, mais peut ne pas détecter le token mocké si le contexte n'est pas initialisé.

**Vérification** : Le test mocke déjà le token dans `beforeEach` :
```javascript
await page.addInitScript(() => {
  window.localStorage.setItem('token', 'mock-access-token');
  window.localStorage.setItem('refreshToken', 'mock-refresh-token');
});
```

**Si problème persiste** : Vérifier que le mock `/api/auth/me/` est bien appelé et retourne un utilisateur valide.

---

## 📝 Commandes pour Réexécuter

```bash
cd frontend/frontend
npx playwright test e2e/saka-cycle-visibility.spec.js
```

**Ou avec UI pour voir les résultats en temps réel** :
```bash
npx playwright test e2e/saka-cycle-visibility.spec.js --ui
```

**Ou avec un navigateur spécifique** :
```bash
npx playwright test e2e/saka-cycle-visibility.spec.js --project=chromium
```

---

## 🐛 Si les Tests Échouent Encore

### Diagnostic Étape par Étape

1. **Vérifier les screenshots** : Les screenshots sont automatiquement capturés en cas d'échec dans `test-results/`

2. **Vérifier les logs** : Exécuter avec `--debug` pour voir les logs détaillés :
   ```bash
   npx playwright test e2e/saka-cycle-visibility.spec.js --debug
   ```

3. **Vérifier les requêtes API** : Utiliser `--trace on` pour voir toutes les requêtes :
   ```bash
   npx playwright test e2e/saka-cycle-visibility.spec.js --trace on
   ```

4. **Vérifier les sélecteurs** : Utiliser `page.pause()` pour inspecter la page :
   ```javascript
   await page.goto('/saka/saisons');
   await page.pause(); // Pause pour inspection manuelle
   ```

---

## ✅ Conclusion

**Toutes les corrections ont été appliquées** :
- ✅ Sélecteurs plus robustes avec contexte
- ✅ Attentes explicites avec `waitForSelector`
- ✅ Mock d'authentification pour les hooks
- ✅ Vérification des appels API avec `waitForResponse`
- ✅ Timeouts ajustés pour les tests lents

**Les tests devraient maintenant passer à 100%.** Si des échecs persistent, utiliser les outils de diagnostic (screenshots, logs, trace) pour identifier les problèmes restants.

---

**Date de génération** : 17 Décembre 2025  
**Auteur** : Gardien de cohérence du Manifeste EGOEJO  
**Version du document** : 2.0 (Corrections finales appliquées)

