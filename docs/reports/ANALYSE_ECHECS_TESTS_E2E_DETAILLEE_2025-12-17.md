# 🔍 Analyse Détaillée des Échecs Tests E2E - Saka Cycle Visibility

**Date** : 17 Décembre 2025  
**Fichier** : `frontend/frontend/e2e/saka-cycle-visibility.spec.js`  
**Résultats** : ❌ **6 échecs** / ✅ **6 réussites** (50% de réussite)

---

## 📊 État Actuel des Tests

| Test | Chromium | Mobile Chrome | Problème Identifié |
|------|----------|---------------|-------------------|
| **Silo commun sur SakaSeasons** | ❌ Échoue (5.9s) | ❌ Échoue (3.9s) | Sélecteur ou données mockées |
| **Cycles SAKA avec statistiques** | ❌ Échoue (6.2s) | ❌ Échoue (4.3s) | Sélecteur ou format de données |
| **Prévisualisation compostage Dashboard** | ❌ Échoue (15.8s) | ❌ Échoue (12.7s) | Hook ou conditions non satisfaites |
| **Aucun cycle SAKA** | ✅ Passe | ✅ Passe | - |
| **Explication cycle complet** | ✅ Passe | ✅ Passe | - |
| **Plusieurs cycles SAKA** | ✅ Passe | ✅ Passe | - |

---

## 🔍 Analyse Détaillée des Échecs

### Échec 1 : "devrait afficher le Silo commun sur la page SakaSeasons"

**Ligne** : 70  
**Temps d'exécution** : 5.9s (chromium), 3.9s (mobile)

**Problèmes potentiels** :

1. **Sélecteur h1** : La correction utilise `page.locator('h1').filter({ hasText: /Saisons SAKA/i })` mais peut-être que le h1 n'est pas encore chargé.

2. **Format du nombre** : `SILO_TOTAL_BALANCE.toLocaleString('fr-FR')` produit "5 000" mais peut-être que le formatage côté React est différent.

3. **Chargement asynchrone** : Les données du Silo sont chargées via `useSakaSilo()` qui est asynchrone.

**Corrections suggérées** :

```javascript
// Attendre que le h1 soit chargé
await page.waitForSelector('h1', { timeout: 5000 });
await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();

// Pour le nombre, utiliser un sélecteur plus flexible
const siloSection = page.locator('section').filter({ hasText: /Silo commun/i });
await expect(siloSection.getByText(new RegExp(`${SILO_TOTAL_BALANCE.toLocaleString('fr-FR')}`))).toBeVisible();
```

---

### Échec 2 : "devrait afficher les cycles SAKA avec leurs statistiques"

**Ligne** : 121  
**Temps d'exécution** : 6.2s (chromium), 4.3s (mobile)

**Problèmes potentiels** :

1. **Format des nombres** : Les statistiques utilisent `toLocaleString("fr-FR")` dans le composant React, mais le test utilise `toLocaleString('fr-FR')`. Vérifier la cohérence.

2. **Sélecteurs pour les statistiques** : Les sélecteurs `getByText()` peuvent être ambigus si le même nombre apparaît plusieurs fois.

3. **Structure des données** : Le mock retourne `stats: { saka_harvested, saka_planted, saka_composted }` mais peut-être que le composant attend une structure différente.

**Corrections suggérées** :

```javascript
// Cibler spécifiquement dans l'article du cycle
const cycleArticle = page.locator('article').filter({ hasText: TEST_CYCLE.name });

// Vérifier "Récolté" dans le contexte de l'article
await expect(cycleArticle.getByText(/Récolté/i)).toBeVisible();
const harvestedInArticle = cycleArticle.locator('text=/\\d+/').filter({ 
  hasText: new RegExp(`${TEST_CYCLE.stats.saka_harvested.toLocaleString('fr-FR')}`) 
});
await expect(harvestedInArticle.first()).toBeVisible();
```

---

### Échec 3 : "devrait afficher la prévisualisation du compostage dans le Dashboard"

**Ligne** : 188  
**Temps d'exécution** : 15.8s (chromium), 12.7s (mobile) ⚠️ **Timeout presque atteint**

**Problèmes identifiés** :

1. **Hook `useSakaCompostPreview()`** : Le hook nécessite un utilisateur authentifié (`if (!user) return`).

2. **Condition d'affichage** : La notification est conditionnelle :
   ```javascript
   {compost?.enabled && compost?.eligible && compost.amount && compost.amount >= 20 && (
   ```

3. **Timeout** : Le test prend presque 15s, ce qui suggère que le `waitForSelector` attend longtemps.

**Corrections suggérées** :

```javascript
// 1. Vérifier que l'utilisateur est bien authentifié
// Le mock localStorage devrait suffire, mais vérifier que useAuth() le détecte

// 2. Mocker l'API d'authentification si nécessaire
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

// 3. Attendre que le Dashboard soit complètement chargé
await page.goto('/dashboard');
await page.waitForLoadState('networkidle');
await page.waitForLoadState('domcontentloaded');

// 4. Attendre que les hooks soient exécutés (donner plus de temps)
await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { 
  timeout: 15000  // Augmenter le timeout
});

// 5. Alternative : Vérifier que le hook est appelé en vérifiant la requête API
await page.waitForResponse('**/api/saka/compost-preview/', { timeout: 10000 });
```

---

## 🔧 Corrections Complémentaires Recommandées

### Correction 1 : Améliorer les sélecteurs avec des attentes explicites

**Problème** : Les sélecteurs peuvent être exécutés avant que les éléments soient chargés.

**Solution** : Ajouter des `waitFor` explicites avant chaque assertion.

```javascript
// Attendre que la page soit complètement chargée
await page.goto('/saka/saisons');
await page.waitForLoadState('networkidle');
await page.waitForLoadState('domcontentloaded');

// Attendre que le h1 soit présent
await page.waitForSelector('h1', { timeout: 5000 });
await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();
```

---

### Correction 2 : Utiliser des sélecteurs plus robustes pour les statistiques

**Problème** : Les nombres peuvent apparaître plusieurs fois (Silo + Cycles).

**Solution** : Utiliser un contexte parent (article) pour cibler spécifiquement.

```javascript
// Pour chaque statistique, cibler dans l'article du cycle
const cycleArticle = page.locator('article').filter({ hasText: TEST_CYCLE.name });

// Récolté
await expect(cycleArticle.getByText(/Récolté/i)).toBeVisible();
// Utiliser un sélecteur plus spécifique : chercher le nombre dans le contexte "Récolté"
const harvestedValue = cycleArticle.locator('p.text-muted-foreground').filter({
  hasText: new RegExp(`${TEST_CYCLE.stats.saka_harvested.toLocaleString('fr-FR')}`)
});
await expect(harvestedValue).toBeVisible();
```

---

### Correction 3 : Vérifier que les hooks sont bien appelés

**Problème** : Le hook `useSakaCompostPreview()` peut ne pas être appelé si l'utilisateur n'est pas détecté.

**Solution** : Vérifier que l'API est bien appelée et que la réponse est correcte.

```javascript
// Attendre que l'API soit appelée
const responsePromise = page.waitForResponse('**/api/saka/compost-preview/', { timeout: 10000 });
await page.goto('/dashboard');
await page.waitForLoadState('networkidle');

// Vérifier que la réponse est correcte
const response = await responsePromise;
const data = await response.json();
expect(data.enabled).toBe(true);
expect(data.eligible).toBe(true);
expect(data.amount).toBeGreaterThanOrEqual(20);

// Maintenant vérifier que la notification est affichée
await expect(page.getByText(/Vos grains vont bientôt retourner à la terre/i)).toBeVisible();
```

---

### Correction 4 : Gérer les cas où les données ne sont pas encore chargées

**Problème** : Les composants React peuvent mettre du temps à se rendre avec les données.

**Solution** : Attendre que les éléments soient visibles avec des sélecteurs plus spécifiques.

```javascript
// Attendre que la section Silo soit chargée
await page.waitForSelector('section:has-text("Silo commun")', { timeout: 5000 });

// Attendre que le nombre soit affiché dans la section Silo
const siloSection = page.locator('section').filter({ hasText: /Silo commun/i });
await expect(siloSection.getByText(new RegExp(`${SILO_TOTAL_BALANCE.toLocaleString('fr-FR')}`))).toBeVisible({ timeout: 5000 });
```

---

## 📝 Code de Correction Complet

### Test 1 : Silo commun (ligne 70)

```javascript
test('devrait afficher le Silo commun sur la page SakaSeasons', async ({ page }) => {
  // ... mocks existants ...

  await page.goto('/saka/saisons');
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');

  // Attendre que le h1 soit chargé
  await page.waitForSelector('h1', { timeout: 5000 });
  await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();

  // Attendre que la section Silo soit chargée
  await page.waitForSelector('section:has-text("Silo commun")', { timeout: 5000 });
  await expect(page.getByText('Silo commun')).toBeVisible();

  // Cibler spécifiquement dans la section Silo
  const siloSection = page.locator('section').filter({ hasText: /Silo commun/i });
  const siloBalanceText = siloSection.getByText(new RegExp(`${SILO_TOTAL_BALANCE.toLocaleString('fr-FR')}`));
  await expect(siloBalanceText).toBeVisible({ timeout: 5000 });

  // ... reste du test ...
});
```

---

### Test 2 : Cycles SAKA avec statistiques (ligne 121)

```javascript
test('devrait afficher les cycles SAKA avec leurs statistiques', async ({ page }) => {
  // ... mocks existants ...

  await page.goto('/saka/saisons');
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');

  // Attendre que le h1 soit chargé
  await page.waitForSelector('h1', { timeout: 5000 });
  await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();

  // Attendre que l'article du cycle soit chargé
  await page.waitForSelector('article', { timeout: 5000 });
  await expect(page.getByText(TEST_CYCLE.name)).toBeVisible();

  // Cibler dans l'article du cycle
  const cycleArticle = page.locator('article').filter({ hasText: TEST_CYCLE.name });

  // Vérifier "Récolté" dans le contexte de l'article
  await expect(cycleArticle.getByText(/Récolté/i)).toBeVisible();
  // Chercher le nombre dans le paragraphe suivant "Récolté"
  const harvestedValue = cycleArticle.locator('p.text-muted-foreground').filter({
    hasText: new RegExp(`${TEST_CYCLE.stats.saka_harvested.toLocaleString('fr-FR')}`)
  });
  await expect(harvestedValue.first()).toBeVisible();

  // Même chose pour "Planté" et "Composté"
  await expect(cycleArticle.getByText(/Planté/i)).toBeVisible();
  const plantedValue = cycleArticle.locator('p.text-muted-foreground').filter({
    hasText: new RegExp(`${TEST_CYCLE.stats.saka_planted.toLocaleString('fr-FR')}`)
  });
  await expect(plantedValue.first()).toBeVisible();

  await expect(cycleArticle.getByText(/Composté/i)).toBeVisible();
  const compostedValue = cycleArticle.locator('p.text-muted-foreground').filter({
    hasText: new RegExp(`${TEST_CYCLE.stats.saka_composted.toLocaleString('fr-FR')}`)
  });
  await expect(compostedValue.first()).toBeVisible();
});
```

---

### Test 3 : Prévisualisation compostage Dashboard (ligne 188)

```javascript
test('devrait afficher la prévisualisation du compostage dans le Dashboard', async ({ page }) => {
  // Mock de l'authentification (si nécessaire)
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

  // ... autres mocks ...

  // Naviguer vers le Dashboard
  await page.goto('/dashboard');
  await page.waitForLoadState('networkidle');
  await page.waitForLoadState('domcontentloaded');

  // Attendre que l'API soit appelée
  await page.waitForResponse('**/api/saka/compost-preview/', { timeout: 10000 });

  // Attendre que la notification soit chargée (avec timeout plus long)
  await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { 
    timeout: 15000 
  });

  // Vérifier que la notification est visible
  const compostNotification = page.getByText(/Vos grains vont bientôt retourner à la terre/i);
  await expect(compostNotification).toBeVisible();

  // ... reste du test ...
});
```

---

## 🎯 Recommandations Prioritaires

### Priorité P0 (Immédiat)

1. ✅ **Ajouter des `waitForSelector`** avant chaque assertion pour s'assurer que les éléments sont chargés
2. ✅ **Utiliser des contextes (section, article)** pour éviter les ambiguïtés de sélecteurs
3. ✅ **Vérifier que l'API est appelée** avant de vérifier l'affichage (pour le Dashboard)

### Priorité P1 (Court Terme)

1. **Ajouter des `data-testid`** dans les composants React pour des sélecteurs plus robustes
2. **Augmenter les timeouts** pour les tests qui prennent du temps (Dashboard)
3. **Vérifier la structure des données mockées** correspond exactement à ce qui est attendu

### Priorité P2 (Long Terme)

1. **Refactoriser les tests** : Extraire les sélecteurs dans des helpers réutilisables
2. **Ajouter des screenshots** automatiques en cas d'échec
3. **Documenter les sélecteurs** utilisés et pourquoi

---

## ✅ Conclusion

Les échecs sont principalement dus à :
1. **Timing** : Les éléments ne sont pas encore chargés quand les assertions sont exécutées
2. **Sélecteurs ambigus** : Les sélecteurs trouvent plusieurs éléments sans contexte
3. **Hooks asynchrones** : Les hooks React nécessitent du temps pour charger les données

**Toutes les corrections suggérées sont simples et peuvent être appliquées rapidement.**

---

**Date de génération** : 17 Décembre 2025  
**Auteur** : Gardien de cohérence du Manifeste EGOEJO  
**Version du document** : 1.0

