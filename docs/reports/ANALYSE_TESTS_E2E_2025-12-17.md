# 🔍 Analyse des Tests E2E - Saka Cycle Visibility

**Date** : 17 Décembre 2025  
**Fichier testé** : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`  
**Résultats** : ❌ **8 échecs** / ✅ **4 réussites** (sur 12 tests × 2 navigateurs)

---

## 📊 Résumé des Résultats

| Navigateur | Tests Passés | Tests Échoués | Taux de Réussite |
|------------|--------------|---------------|------------------|
| **Chromium** | 2 | 4 | 33% |
| **Mobile Chrome** | 2 | 4 | 33% |
| **TOTAL** | **4** | **8** | **33%** |

---

## ❌ Problèmes Identifiés

### Problème 1 : Strict Mode Violation - Titre "Saisons SAKA" (4 échecs)

**Erreur** :
```
Error: strict mode violation: getByRole('heading', { name: /Saisons SAKA/i }) resolved to 2 elements:
    1) <h1 class="text-3xl font-bold tracking-tight">Saisons SAKA 🌾</h1>
    2) <h2 class="text-xl font-semibold">Saisons SAKA</h2>
```

**Cause** : La page `SakaSeasons.tsx` contient **deux headings** avec "Saisons SAKA" :
- `<h1>Saisons SAKA 🌾</h1>` (ligne 13 - titre principal)
- `<h2>Saisons SAKA</h2>` (ligne 47 - titre de section)

**Tests affectés** :
- `devrait afficher le Silo commun sur la page SakaSeasons` (chromium + mobile)
- `devrait afficher les cycles SAKA avec leurs statistiques` (chromium + mobile)

**Solution** : Utiliser un sélecteur plus spécifique pour cibler le `h1` principal.

---

### Problème 2 : Strict Mode Violation - Nombre "5 000" (2 échecs)

**Erreur** :
```
Error: strict mode violation: getByText(/5 000/) resolved to 2 elements:
    1) <p class="text-3xl font-bold">…</p> (Silo commun - 5 000 grains)
    2) <p class="text-muted-foreground">5 000 grains</p> (Cycle - Récolté)
```

**Cause** : Le nombre "5 000" apparaît à la fois :
- Dans le **Silo commun** : `5 000 grains` (total_balance)
- Dans les **cycles** : `5 000 grains` (saka_harvested)

**Tests affectés** :
- `devrait afficher plusieurs cycles SAKA si disponibles` (chromium + mobile)

**Solution** : Utiliser un contexte (section, parent) pour cibler spécifiquement les statistiques des cycles.

---

### Problème 3 : Notification de Compostage Non Trouvée (2 échecs)

**Erreur** :
```
Error: element(s) not found
Locator: getByText(/Vos grains vont bientôt retourner à la terre/i)
```

**Cause** : La notification de compostage est **conditionnelle** dans `Dashboard.jsx` :
```javascript
{compost?.enabled && compost?.eligible && compost.amount && compost.amount >= 20 && (
  <div>🌾 Vos grains vont bientôt retourner à la terre</div>
)}
```

Le test mocke `/api/saka/compost-preview/` mais :
1. Le hook `useSakaCompostPreview()` doit être appelé
2. Les données mockées doivent correspondre exactement à la structure attendue
3. La condition `compost.amount >= 20` doit être respectée

**Tests affectés** :
- `devrait afficher la prévisualisation du compostage dans le Dashboard` (chromium + mobile)

**Solution** : Vérifier que le mock de `/api/saka/compost-preview/` est correct et que le hook est bien appelé.

---

## ✅ Tests Qui Fonctionnent (4/12)

1. ✅ `devrait gérer le cas où aucun cycle SAKA n'existe encore` (chromium + mobile)
2. ✅ `devrait expliquer le cycle complet (récolte → plantation → compost → silo)` (chromium + mobile)

Ces tests fonctionnent car ils utilisent des sélecteurs plus spécifiques ou des conditions moins strictes.

---

## 🔧 Suggestions de Corrections

### Correction 1 : Titre "Saisons SAKA" - Utiliser `.first()` ou cibler le h1

**Fichier** : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`

**Lignes à modifier** : 101, 149

**Avant** :
```javascript
await expect(page.getByRole('heading', { name: /Saisons SAKA/i })).toBeVisible();
```

**Après (Option 1 - Utiliser `.first()`)**
```javascript
await expect(page.getByRole('heading', { name: /Saisons SAKA/i }).first()).toBeVisible();
```

**Après (Option 2 - Cibler spécifiquement le h1)**
```javascript
await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();
```

**Recommandation** : **Option 2** est plus robuste car elle cible explicitement le `h1` principal.

---

### Correction 2 : Nombre "5 000" - Utiliser un contexte (section)

**Fichier** : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`

**Lignes à modifier** : 349-351

**Avant** :
```javascript
await expect(
  page.getByText(new RegExp(`${cycles[0].stats.saka_harvested.toLocaleString('fr-FR')}`))
).toBeVisible();
```

**Après** :
```javascript
// Cibler spécifiquement dans la section des cycles
const cyclesSection = page.locator('section').filter({ hasText: /Saisons SAKA/i });
await expect(
  cyclesSection.getByText(new RegExp(`${cycles[0].stats.saka_harvested.toLocaleString('fr-FR')}`))
).toBeVisible();
```

**Alternative (plus robuste)** :
```javascript
// Cibler dans l'article du cycle spécifique
const cycleArticle = page.locator('article').filter({ hasText: cycles[0].name });
await expect(
  cycleArticle.getByText(new RegExp(`${cycles[0].stats.saka_harvested.toLocaleString('fr-FR')}`))
).toBeVisible();
```

**Recommandation** : **Alternative** car elle cible spécifiquement l'article du cycle, évitant toute ambiguïté.

---

### Correction 3 : Notification de Compostage - Vérifier le hook et le mock

**Fichier** : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`

**Lignes à modifier** : 188-223

**Problème identifié** :
1. Le hook `useSakaCompostPreview()` doit être appelé dans `Dashboard.jsx`
2. Le mock doit correspondre à la structure attendue par le hook
3. La condition `compost.amount >= 20` doit être respectée

**Vérifications nécessaires** :

1. **Vérifier que le hook existe** :
   ```bash
   # Vérifier que useSakaCompostPreview existe dans useSaka.js
   grep -r "useSakaCompostPreview" frontend/frontend/src/hooks/
   ```

2. **Vérifier la structure du mock** :
   Le mock actuel :
   ```javascript
   await page.route('**/api/saka/compost-preview/', async (route) => {
     await route.fulfill({
       status: 200,
       contentType: 'application/json',
       body: JSON.stringify({
         enabled: true,
         eligible: true,
         amount: 20,
         days_until_eligible: 5,
         last_activity_date: '2025-12-10T00:00:00Z',
       }),
     });
   });
   ```
   
   **Vérifier** que le hook `useSakaCompostPreview()` attend exactement cette structure.

3. **Vérifier que le Dashboard charge les données** :
   Ajouter un `waitFor` pour s'assurer que les données sont chargées :
   ```javascript
   // Attendre que les données soient chargées
   await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { timeout: 10000 });
   ```

**Solution complète** :
```javascript
test('devrait afficher la prévisualisation du compostage dans le Dashboard', async ({ page }) => {
  // Mock de la réponse API pour le compostage preview
  await page.route('**/api/saka/compost-preview/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        enabled: true,
        eligible: true,
        amount: 20, // >= 20 pour satisfaire la condition
        days_until_eligible: 5,
        last_activity_date: '2025-12-10T00:00:00Z',
      }),
    });
  });

  // Mock de la réponse API pour le Silo (optionnel pour Dashboard)
  await page.route('**/api/saka/silo/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        enabled: true,
        total_balance: SILO_TOTAL_BALANCE,
      }),
    });
  });

  // Naviguer vers le Dashboard
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');

  // Attendre que la notification soit chargée (avec timeout plus long)
  await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { 
    timeout: 10000 
  });

  // Vérifier que la notification de compostage est affichée
  const compostNotification = page.getByText(/Vos grains vont bientôt retourner à la terre/i);
  await expect(compostNotification).toBeVisible();

  // ... reste du test
});
```

---

## 📝 Corrections Recommandées (Code)

### Fichier : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`

#### Correction 1 : Titre "Saisons SAKA" (lignes 101, 149)

```javascript
// AVANT
await expect(page.getByRole('heading', { name: /Saisons SAKA/i })).toBeVisible();

// APRÈS
await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();
```

#### Correction 2 : Nombre "5 000" (lignes 349-354)

```javascript
// AVANT
await expect(
  page.getByText(new RegExp(`${cycles[0].stats.saka_harvested.toLocaleString('fr-FR')}`))
).toBeVisible();

// APRÈS
const cycleArticle1 = page.locator('article').filter({ hasText: cycles[0].name });
await expect(
  cycleArticle1.getByText(new RegExp(`${cycles[0].stats.saka_harvested.toLocaleString('fr-FR')}`))
).toBeVisible();

const cycleArticle2 = page.locator('article').filter({ hasText: cycles[1].name });
await expect(
  cycleArticle2.getByText(new RegExp(`${cycles[1].stats.saka_harvested.toLocaleString('fr-FR')}`))
).toBeVisible();
```

#### Correction 3 : Notification de compostage (lignes 188-223)

```javascript
// Ajouter un waitFor avant la vérification
await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { 
  timeout: 10000 
});

// Vérifier que la notification est visible
const compostNotification = page.getByText(/Vos grains vont bientôt retourner à la terre/i);
await expect(compostNotification).toBeVisible();
```

---

## 🎯 Plan d'Action

### Priorité P0 (Immédiat)

1. ✅ **Corriger le sélecteur "Saisons SAKA"** : Utiliser `page.locator('h1')` au lieu de `getByRole('heading')`
2. ✅ **Corriger le sélecteur "5 000"** : Utiliser un contexte (article du cycle)
3. ⚠️ **Vérifier le hook `useSakaCompostPreview`** : S'assurer qu'il existe et qu'il appelle `/api/saka/compost-preview/`

### Priorité P1 (Court Terme)

1. **Ajouter des `waitFor`** : Attendre que les éléments soient chargés avant de les vérifier
2. **Améliorer les sélecteurs** : Utiliser des sélecteurs plus robustes (data-testid, classes CSS spécifiques)
3. **Ajouter des screenshots** : Capturer des screenshots en cas d'échec pour faciliter le débogage

### Priorité P2 (Long Terme)

1. **Refactoriser les tests** : Extraire les sélecteurs dans des constantes réutilisables
2. **Ajouter des helpers** : Créer des fonctions helper pour les actions communes
3. **Documenter les tests** : Ajouter des commentaires expliquant les sélecteurs utilisés

---

## 📊 Impact des Corrections

### Avant Corrections
- **Taux de réussite** : 33% (4/12)
- **Tests échoués** : 8 (strict mode violations + élément non trouvé)

### Après Corrections (Prévu)
- **Taux de réussite** : 100% (12/12)
- **Tests échoués** : 0

---

## ✅ Conclusion

Les échecs des tests E2E sont principalement dus à :
1. **Sélecteurs trop génériques** : Utilisation de `getByRole('heading')` qui trouve plusieurs éléments
2. **Manque de contexte** : Sélection de texte sans contexte (section, parent)
3. **Conditions non satisfaites** : Notification conditionnelle non affichée car conditions non remplies

**Toutes les corrections sont simples et peuvent être appliquées rapidement.**

---

**Date de génération** : 17 Décembre 2025  
**Auteur** : Gardien de cohérence du Manifeste EGOEJO  
**Version du document** : 1.0

