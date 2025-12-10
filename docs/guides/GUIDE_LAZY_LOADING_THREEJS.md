# ⚡ Guide Lazy Loading Agressif Three.js - EGOEJO

**Date** : 2025-01-27  
**Objectif** : Réduire le bundle JavaScript en chargeant Three.js uniquement si nécessaire

---

## 🎯 Problème Actuel

- Three.js chargé même en mode éco/low-power
- Bundle JavaScript lourd (~500KB+)
- FCP ralenti sur mobile
- Bibliothèques lourdes téléchargées inutilement

---

## ✅ Solution : Code Splitting Conditionnel

### 1. Vérifier le Chargement Actuel

**Problème** : Même si `HeroSorgho` détecte le mode low-power, Three.js peut être chargé dans le bundle initial.

**Vérification** :
```bash
cd frontend/frontend
npm run build
# Vérifier la taille des chunks dans dist/
```

### 2. Import Conditionnel Dynamique

**Solution** : Utiliser `React.lazy()` et import dynamique pour charger Three.js uniquement si nécessaire.

**Fichier créé** : `frontend/frontend/src/components/HeroSorghoLazy.jsx`

**Avantages** :
- Three.js dans un chunk séparé
- Chargé uniquement si `isLowPower === false`
- Réduction bundle initial : ~40-50%

### 3. Configuration Vite

**Vérifier** : `vite.config.js` doit séparer Three.js dans un chunk dédié.

**Configuration actuelle** :
```javascript
manualChunks: (id) => {
  if (id.includes('three') || id.includes('@react-three')) {
    return 'three-vendor';
  }
}
```

**Amélioration** : S'assurer que Three.js est toujours dans un chunk séparé, même avec lazy loading.

---

## 🔧 Implémentation

### Étape 1 : Utiliser HeroSorghoLazy

**Modifier** `frontend/frontend/src/app/pages/Home.jsx` :

```javascript
// Avant
import HeroSorgho from '../../components/HeroSorgho';

// Après
import HeroSorghoLazy from '../../components/HeroSorghoLazy';
```

### Étape 2 : Vérifier le Code Splitting

**Build et analyser** :
```bash
cd frontend/frontend
npm run build
npm run analyze  # Si configuré
```

**Vérifier** :
- Chunk `three-vendor.js` existe
- Chunk `three-vendor.js` n'est pas dans le bundle initial
- Taille bundle initial réduite

### Étape 3 : Test en Mode Éco

1. Activer Eco-Mode
2. Ouvrir DevTools → Network
3. Vérifier que `three-vendor.js` n'est **pas** chargé
4. Vérifier que le bundle initial est plus léger

---

## 📊 Métriques Attendues

### Bundle Initial (Mode Éco)
- **Avant** : ~800KB (avec Three.js)
- **Après** : ~400KB (sans Three.js)
- **Réduction** : ~50%

### FCP Mobile
- **Avant** : ~2.5-3s
- **Après** : ~1.5-2s
- **Amélioration** : ~40%

### Chargement Three.js (Si nécessaire)
- **Lazy** : Chargé uniquement après détection low-power
- **Temps** : ~200-300ms supplémentaire (acceptable)

---

## 🧪 Tests

### Test 1 : Mode Éco

```bash
# 1. Activer Eco-Mode
# 2. Ouvrir DevTools → Network
# 3. Vérifier : three-vendor.js absent
```

### Test 2 : Mode Normal

```bash
# 1. Désactiver Eco-Mode
# 2. Ouvrir DevTools → Network
# 3. Vérifier : three-vendor.js chargé
```

### Test 3 : Mobile (Low Power Auto)

```bash
# 1. Simuler mobile (DevTools)
# 2. Vérifier : three-vendor.js absent
```

---

## 🔍 Vérification Technique

### Vite Bundle Analysis

```bash
cd frontend/frontend
npm install --save-dev rollup-plugin-visualizer
```

**Ajouter à `vite.config.js`** :
```javascript
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    // ...
    visualizer({
      open: true,
      filename: 'dist/stats.html',
    }),
  ],
});
```

**Analyser** :
```bash
npm run build
# Ouvrir dist/stats.html
```

---

## 📝 Notes Importantes

1. **Compatibilité** : `React.lazy()` fonctionne avec React 19
2. **Fallback** : Suspense avec fallback minimal
3. **Performance** : Lazy loading ajoute ~200ms, mais économise ~400KB initialement
4. **SEO** : Pas d'impact (Three.js est côté client)

---

## 🚀 Prochaines Étapes

1. ✅ Créer `HeroSorghoLazy.jsx`
2. ⏳ Remplacer `HeroSorgho` par `HeroSorghoLazy` dans `Home.jsx`
3. ⏳ Vérifier bundle analysis
4. ⏳ Tester en mode éco
5. ⏳ Mesurer amélioration FCP

---

**Dernière mise à jour** : 2025-01-27  
**Statut** : 📋 Composant créé, intégration à faire

