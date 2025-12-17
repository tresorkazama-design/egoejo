# ✅ Résolution Finale - Tests E2E Compostage

**Date** : 17 Décembre 2025  
**Statut** : ✅ **RÉSOLU** - Tous les tests passent maintenant

---

## 🎯 Problème Identifié

### Symptôme Initial

L'API `/api/saka/compost-preview/` n'était jamais appelée dans les tests E2E, même avec un utilisateur authentifié.

### Cause Racine

**Violation des règles de React (Rules of Hooks)** :

Les hooks `useSakaSilo()` et `useSakaCompostPreview()` étaient appelés **APRÈS** les retours précoces conditionnels dans le composant Dashboard :

```javascript
// ❌ MAUVAIS : Hooks appelés après les retours précoces
if (authLoading) return <Loader />;
if (!user) return <div>Connectez-vous</div>;

// Les hooks sont appelés ICI, après les retours précoces
const { data: silo } = useSakaSilo();
const { data: compost } = useSakaCompostPreview();
```

**Problème** : React exige que les hooks soient toujours appelés dans le même ordre à chaque rendu. Si un rendu retourne tôt, les hooks ne sont pas appelés, ce qui change l'ordre des hooks entre les rendus.

**Erreur React** :
```
Error: Rendered more hooks than during the previous render.
React has detected a change in the order of Hooks called by Dashboard.
```

---

## ✅ Solution Appliquée

### Correction 1 : Déplacer les hooks AVANT les retours précoces

```javascript
// ✅ BON : Hooks appelés AVANT les retours précoces
const { user, loading: authLoading } = useAuth();
const { data: silo } = useSakaSilo();  // ✅ Hook appelé avant les retours
const { data: compost } = useSakaCompostPreview();  // ✅ Hook appelé avant les retours

// Maintenant, les vérifications conditionnelles
if (authLoading) return <Loader />;
if (!user) return <div>Connectez-vous</div>;
```

**Avantages** :
- Les hooks sont toujours appelés dans le même ordre
- Respecte les règles de React
- Le hook s'exécute même si le composant retourne tôt

### Correction 2 : Simplifier le hook pour dépendre directement de `user`

```javascript
// Avant : useCallback avec dépendance sur user
const loadPreview = useCallback(async () => { ... }, [user]);
useEffect(() => { loadPreview(); }, [loadPreview]);

// Après : useEffect dépend directement de user
useEffect(() => {
  if (!user) return;
  const loadPreview = async () => { ... };
  loadPreview();
}, [user]); // Dépendre directement de user
```

**Avantages** :
- Plus simple et direct
- Réagit immédiatement aux changements de `user`
- Moins de complexité

### Correction 3 : Attendre `authLoading` avant de vérifier `user`

```javascript
// Attendre que l'authentification soit terminée
if (authLoading) {
  return <Loader message="Vérification de l'authentification..." />;
}

if (!user) {
  return <div>Veuillez vous connecter...</div>;
}
```

**Avantages** :
- Garantit que `user` est défini ou `null` de manière stable
- Évite les rendus avec `user` qui change pendant le chargement

### Correction 4 : Améliorer les sélecteurs dans les tests E2E

```javascript
// Avant : Sélecteur ambigu
await expect(page.getByText(/Silo Commun/i)).toBeVisible();

// Après : Sélecteur spécifique
const notificationSection = page.locator('div').filter({ 
  hasText: /Vos grains vont bientôt retourner à la terre/i 
});
await expect(notificationSection.getByText(/Silo Commun/i).first()).toBeVisible();
```

**Avantages** :
- Évite les erreurs "strict mode violation"
- Plus robuste et prévisible

---

## 📊 Résultats

### Avant les corrections

- ❌ 2 tests échouaient (timeout)
- ❌ API `/api/saka/compost-preview/` jamais appelée
- ❌ Erreur React : "Rendered more hooks than during the previous render"

### Après les corrections

- ✅ **2 tests PASSENT** (100% de réussite pour ces tests)
- ✅ API `/api/saka/compost-preview/` appelée correctement
- ✅ Hook `useSakaCompostPreview()` s'exécute correctement
- ✅ Notification de compostage s'affiche dans le Dashboard

### Logs de confirmation

```
[TEST] API /api/saka/compost-preview/ appelée
[useSakaCompostPreview] Réponse API reçue: {enabled: true, eligible: true, amount: 20, ...}
[Dashboard] Rendu du composant {compost: Object, compostLoading: false}
```

---

## 🔍 Découvertes de l'Investigation

### 1. Problème de timing

Le composant Dashboard se montait **AVANT** que l'API `/api/auth/me/` ait répondu, mais le `AuthContext.Provider` ne rend les enfants que si `!loading`, donc le problème était ailleurs.

### 2. Violation des règles de React

Le vrai problème était que les hooks étaient appelés **conditionnellement** (après des retours précoces), ce qui violait les règles de React.

### 3. Importance des logs de débogage

Les logs de débogage ont été cruciaux pour identifier :
- Que l'API était appelée
- Que le hook s'exécutait
- Que les données étaient reçues
- Que le problème était dans les sélecteurs des tests

---

## 📝 Fichiers Modifiés

1. ✅ `frontend/frontend/src/app/pages/Dashboard.jsx`
   - Hooks déplacés avant les retours précoces
   - Ajout de la vérification `authLoading`

2. ✅ `frontend/frontend/src/hooks/useSaka.js`
   - Hook simplifié pour dépendre directement de `user`

3. ✅ `frontend/frontend/e2e/saka-cycle-visibility.spec.js`
   - Sélecteurs améliorés pour éviter l'ambiguïté
   - Logs de débogage ajoutés (puis retirés)

---

## ✅ Tests E2E - Résultats Finaux

### Tests pour la prévisualisation du compostage

- ✅ **2/2 tests PASSENT** (100%)

### Tous les tests E2E SAKA cycle visibility

- ✅ **12/12 tests PASSENT** (100%)

---

## 🎓 Leçons Apprises

1. **Respecter les règles de React** : Les hooks doivent toujours être appelés dans le même ordre, peu importe les conditions
2. **Logs de débogage** : Essentiels pour comprendre le comportement asynchrone
3. **Sélecteurs spécifiques** : Utiliser des sélecteurs précis pour éviter les ambiguïtés
4. **Timing** : Attendre que les états soient stables avant de vérifier

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ **RÉSOLU** - Tous les tests passent

