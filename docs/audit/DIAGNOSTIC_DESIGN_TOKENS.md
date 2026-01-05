# 🔍 DIAGNOSTIC COMPLET : Module `design-tokens`
## EGOEJO Frontend - Analyse des Références et Stratégies de Correction

**Date** : 2025-12-21  
**Contexte** : Erreurs d'import `design-tokens` bloquant la compilation frontend

---

## 📋 RÉSUMÉ EXÉCUTIF

### 🔴 Problème Identifié
- **11 fichiers** importent depuis `../design-tokens` ou `@/design-tokens`
- **Aucun fichier/dossier** `design-tokens` n'existe dans le projet
- **Nature du module** : Module JavaScript (ES6) exportant des constantes et fonctions
- **Impact** : ⚠️ **BLOQUANT** - Compilation frontend impossible

### 📊 Statistiques
- **Fichiers affectés** : 11
- **Exports attendus** : 6 (SobrietyLevel, getSobrietyConfig, getSobrietyFeature, zIndexLayers, breakpoints, sobrietyConfig)
- **Types d'imports** : 2 (relatif `../design-tokens`, alias `@/design-tokens`)

---

## 1. 📁 INVENTAIRE DES FICHIERS AFFECTÉS

### 1.1 Fichiers Utilisant `design-tokens`

| Fichier | Chemin | Import | Exports Utilisés |
|---------|--------|--------|------------------|
| `HeroSorgho.jsx` | `src/components/` | `../design-tokens` | `getSobrietyFeature` |
| `MyceliumVisualization.jsx` | `src/components/` | `../design-tokens` | `getSobrietyFeature` |
| `HeroSorghoLazy.jsx` | `src/components/` | `../design-tokens` | `getSobrietyFeature` |
| `CardTilt.jsx` | `src/components/` | `../design-tokens` | `getSobrietyFeature` |
| `EcoModeContext.jsx` | `src/contexts/` | `../design-tokens` | `SobrietyLevel`, `getSobrietyConfig` |
| `EcoModeToggle.jsx` | `src/components/` | `../design-tokens` | `SobrietyLevel`, `zIndexLayers`, `sobrietyConfig` |
| `FullscreenMenu.jsx` | `src/components/` | `../design-tokens` | `zIndexLayers` |
| `Loader.jsx` | `src/components/` | `../design-tokens` | `zIndexLayers` |
| `OfflineIndicator.jsx` | `src/components/` | `../design-tokens` | `zIndexLayers` |
| `CustomCursor.jsx` | `src/components/` | `../design-tokens` | `breakpoints` |
| `SakaSeasons.tsx` | `src/app/pages/` | `@/design-tokens` | `getSobrietyFeature` |

**Total** : 11 fichiers

---

## 2. 🔍 ANALYSE DES EXPORTS ATTENDUS

### 2.1 Exports Identifiés

#### `SobrietyLevel` (Enum/Object)
**Utilisé dans** : `EcoModeContext.jsx`, `EcoModeToggle.jsx`

**Valeurs attendues** (d'après le code) :
```javascript
SobrietyLevel.FULL = 1
SobrietyLevel.SIMPLIFIED = 2
SobrietyLevel.MINIMAL = 3
// Probablement aussi : 4, 5 pour les niveaux supérieurs
```

**Usage** :
```javascript
// EcoModeContext.jsx:29
return saved ? parseInt(saved, 10) : SobrietyLevel.FULL;

// EcoModeToggle.jsx:20
level: SobrietyLevel.FULL,
```

#### `getSobrietyConfig(level)` (Function)
**Utilisé dans** : `EcoModeContext.jsx`

**Signature attendue** :
```javascript
getSobrietyConfig(sobrietyLevel) // Retourne un objet de configuration
```

**Usage** :
```javascript
// EcoModeContext.jsx:17
import { SobrietyLevel, getSobrietyConfig } from '../design-tokens';

// Probablement utilisé pour obtenir la config d'un niveau
const config = getSobrietyConfig(sobrietyLevel);
```

#### `getSobrietyFeature(level, feature)` (Function)
**Utilisé dans** : `HeroSorgho.jsx`, `MyceliumVisualization.jsx`, `HeroSorghoLazy.jsx`, `CardTilt.jsx`, `SakaSeasons.tsx`

**Signature attendue** :
```javascript
getSobrietyFeature(sobrietyLevel, featureName) // Retourne un booléen
```

**Usage** :
```javascript
// HeroSorgho.jsx:18
import { getSobrietyFeature } from "../design-tokens";

// SakaSeasons.tsx:14
const canAnimate = getSobrietyFeature(sobrietyLevel, 'enableAnimations');
```

#### `zIndexLayers` (Object)
**Utilisé dans** : `EcoModeToggle.jsx`, `FullscreenMenu.jsx`, `Loader.jsx`, `OfflineIndicator.jsx`

**Structure attendue** :
```javascript
zIndexLayers = {
  background: -1,
  content: 1,
  overlay: 100,
  modal: 200,
  tooltip: 300,
  // etc.
}
```

**Usage** :
```javascript
// FullscreenMenu.jsx:3
import { zIndexLayers } from '../design-tokens';

// Probablement utilisé pour définir z-index
style={{ zIndex: zIndexLayers.modal }}
```

#### `breakpoints` (Object)
**Utilisé dans** : `CustomCursor.jsx`

**Structure attendue** :
```javascript
breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
}
```

**Usage** :
```javascript
// CustomCursor.jsx:7
import { breakpoints } from '../design-tokens';

// CustomCursor.jsx:29
const isMobile = window.matchMedia(`(max-width: ${breakpoints.md})`).matches;
```

#### `sobrietyConfig` (Object)
**Utilisé dans** : `EcoModeToggle.jsx`

**Structure attendue** :
```javascript
sobrietyConfig = {
  [SobrietyLevel.FULL]: {
    name: 'Full',
    description: '...',
    performance: '...',
  },
  [SobrietyLevel.SIMPLIFIED]: { ... },
  // etc.
}
```

**Usage** :
```javascript
// EcoModeToggle.jsx:8
import { SobrietyLevel, zIndexLayers, sobrietyConfig } from '../design-tokens';

// EcoModeToggle.jsx:21
name: sobrietyConfig[SobrietyLevel.FULL].name,
description: sobrietyConfig[SobrietyLevel.FULL].description,
```

---

## 3. 🔎 VÉRIFICATION DE L'EXISTENCE

### 3.1 Recherche Globale

**Résultats** :
- ❌ Aucun fichier `design-tokens` trouvé dans `frontend/`
- ❌ Aucun dossier `design-tokens/` trouvé
- ❌ Aucun package `design-tokens` dans `package.json`

### 3.2 Structure de Répertoires Attendue

**Chemin attendu** (selon les imports) :
```
frontend/frontend/src/design-tokens/
  ├── index.js (ou index.ts)
  └── tokens.css (déjà créé dans styles/)
```

**Chemin actuel** :
```
frontend/frontend/src/
  ├── styles/
  │   ├── global.css (importe './tokens.css' ✅)
  │   └── tokens.css (✅ créé)
  └── design-tokens/ (❌ N'EXISTE PAS)
      └── index.js (❌ MANQUANT)
```

### 3.3 Alias Vite (`@/design-tokens`)

**Configuration** (`vite.config.js:122`) :
```javascript
resolve: {
  alias: {
    '@': path.resolve(__dirname, './src'),
  },
}
```

**Résolution** :
- `@/design-tokens` → `src/design-tokens/index.js`
- `../design-tokens` → `src/design-tokens/index.js` (depuis `src/components/`)

**Conclusion** : Les deux types d'imports pointent vers le même fichier manquant.

---

## 4. 🎯 NATURE DU MODULE

### 4.1 Type de Module

**Module JavaScript ES6** (pas CSS, pas package npm)

**Preuves** :
1. Imports JavaScript : `import { ... } from '../design-tokens'`
2. Exports utilisés : Fonctions, objets, enums (pas de CSS)
3. Pas de package dans `package.json`
4. Chemin relatif (`../design-tokens`) = module local

### 4.2 Fonctionnalité

**Design System / Tokens** pour :
- **Sobriété** : Gestion des niveaux de performance (1-5)
- **Z-index** : Gestion des couches d'affichage
- **Breakpoints** : Points de rupture responsive
- **Configuration** : Configurations par niveau de sobriété

### 4.3 Hypothèse sur l'Origine

**Reliquat non commité** ou **fichier supprimé par erreur**

**Indices** :
- 11 fichiers l'utilisent (intégration profonde)
- Code fonctionnel (pas de TODO ou commentaires "à implémenter")
- Structure cohérente (exports bien définis)
- Alias Vite configuré (`@/design-tokens`)

**Conclusion** : Le module a probablement existé mais a été supprimé ou jamais commité.

---

## 5. 📊 IMPACT PAR FICHIER

### 5.1 Composants 3D (Critique)

| Fichier | Impact | Blocage |
|---------|--------|---------|
| `HeroSorgho.jsx` | ⚠️ **HAUT** | Animation 3D désactivée si erreur |
| `MyceliumVisualization.jsx` | ⚠️ **HAUT** | Visualisation 3D désactivée |
| `HeroSorghoLazy.jsx` | ⚠️ **MOYEN** | Lazy loading 3D désactivé |
| `CardTilt.jsx` | ⚠️ **MOYEN** | Animation tilt désactivée |

### 5.2 Contexte Éco-Mode (Critique)

| Fichier | Impact | Blocage |
|---------|--------|---------|
| `EcoModeContext.jsx` | 🔴 **CRITIQUE** | Contexte principal inutilisable |
| `EcoModeToggle.jsx` | 🔴 **CRITIQUE** | Toggle éco-mode inutilisable |

### 5.3 Composants UI (Moyen)

| Fichier | Impact | Blocage |
|---------|--------|---------|
| `FullscreenMenu.jsx` | ⚠️ **MOYEN** | Z-index incorrect |
| `Loader.jsx` | ⚠️ **MOYEN** | Z-index incorrect |
| `OfflineIndicator.jsx` | ⚠️ **MOYEN** | Z-index incorrect |
| `CustomCursor.jsx` | ⚠️ **MOYEN** | Breakpoints incorrects |
| `SakaSeasons.tsx` | ⚠️ **MOYEN** | Animations désactivées |

---

## 6. 🎯 STRATÉGIES DE CORRECTION

### 6.1 Stratégie A : Suppression Complète

**Principe** : Supprimer tous les imports et remplacer par des valeurs en dur.

**Avantages** :
- ✅ Solution rapide (pas de création de fichier)
- ✅ Pas de dépendance externe
- ✅ Build fonctionne immédiatement

**Inconvénients** :
- ❌ Code dupliqué (valeurs en dur dans 11 fichiers)
- ❌ Maintenance difficile (changement = modifier 11 fichiers)
- ❌ Perte de cohérence (valeurs peuvent diverger)
- ❌ Pas de centralisation (contraire aux bonnes pratiques)

**Fichiers à modifier** : 11 fichiers

**Exemple de modification** :
```javascript
// Avant
import { getSobrietyFeature } from '../design-tokens';
const canAnimate = getSobrietyFeature(sobrietyLevel, 'enableAnimations');

// Après
const canAnimate = sobrietyLevel <= 2; // En dur
```

**Temps estimé** : 30-45 minutes

**Recommandation** : ⚠️ **NON RECOMMANDÉ** - Solution de contournement temporaire uniquement.

---

### 6.2 Stratégie B : Correction (Création du Module Minimal)

**Principe** : Créer `src/design-tokens/index.js` avec les exports minimaux nécessaires.

**Avantages** :
- ✅ Solution propre (module centralisé)
- ✅ Maintenance facile (un seul fichier)
- ✅ Cohérence garantie (valeurs centralisées)
- ✅ Extensible (facile d'ajouter de nouveaux tokens)

**Inconvénients** :
- ⚠️ Nécessite de deviner les valeurs exactes (pas de référence)
- ⚠️ Tests nécessaires pour valider le comportement

**Fichiers à créer** : 1 (`src/design-tokens/index.js`)

**Structure proposée** :
```javascript
// src/design-tokens/index.js

// Sobriety Levels (1-5)
export const SobrietyLevel = {
  FULL: 1,
  SIMPLIFIED: 2,
  MINIMAL: 3,
  ULTRA_MINIMAL: 4,
  TEXT_ONLY: 5,
};

// Z-index Layers
export const zIndexLayers = {
  background: -1,
  content: 1,
  overlay: 100,
  modal: 200,
  tooltip: 300,
};

// Breakpoints
export const breakpoints = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
};

// Sobriety Config
export const sobrietyConfig = {
  [SobrietyLevel.FULL]: {
    name: 'Full',
    description: 'Performance maximale avec toutes les animations',
    performance: 'Haute',
  },
  [SobrietyLevel.SIMPLIFIED]: {
    name: 'Simplifié',
    description: '3D simplifié sans bloom',
    performance: 'Moyenne',
  },
  // ... autres niveaux
};

// Get Sobriety Config
export const getSobrietyConfig = (level) => {
  return sobrietyConfig[level] || sobrietyConfig[SobrietyLevel.FULL];
};

// Get Sobriety Feature
export const getSobrietyFeature = (level, feature) => {
  const config = getSobrietyConfig(level);
  
  switch (feature) {
    case 'enableAnimations':
      return level <= SobrietyLevel.SIMPLIFIED;
    case 'enable3D':
      return level <= SobrietyLevel.MINIMAL;
    case 'enableBloom':
      return level === SobrietyLevel.FULL;
    default:
      return true;
  }
};
```

**Temps estimé** : 1-2 heures (création + tests)

**Recommandation** : ✅ **RECOMMANDÉ** - Solution propre et maintenable.

---

### 6.3 Stratégie C : Implémentation Complète (Design System)

**Principe** : Créer un vrai Design System avec tokens CSS + JS, documentation, tests.

**Avantages** :
- ✅ Solution professionnelle (Design System complet)
- ✅ Documentation intégrée
- ✅ Tests unitaires
- ✅ Extensible et maintenable
- ✅ Aligné avec les bonnes pratiques

**Inconvénients** :
- ⚠️ Temps de développement important (4-6 heures)
- ⚠️ Overkill pour un fix urgent

**Fichiers à créer** :
- `src/design-tokens/index.js` (exports JS)
- `src/design-tokens/tokens.css` (variables CSS - déjà créé)
- `src/design-tokens/README.md` (documentation)
- `src/design-tokens/__tests__/index.test.js` (tests)

**Structure proposée** :
```
src/design-tokens/
  ├── index.js (exports JS complets)
  ├── tokens.css (variables CSS)
  ├── README.md (documentation)
  └── __tests__/
      └── index.test.js (tests unitaires)
```

**Temps estimé** : 4-6 heures

**Recommandation** : ⚠️ **OPTIONNEL** - À faire si temps disponible, sinon Stratégie B suffit.

---

## 7. 📝 RECOMMANDATION FINALE

### 🎯 Stratégie Recommandée : **Stratégie B (Correction Minimal)**

**Justification** :
1. ✅ **Rapide** : 1-2 heures vs 4-6 heures
2. ✅ **Propre** : Module centralisé, maintenable
3. ✅ **Suffisant** : Couvre tous les besoins actuels
4. ✅ **Extensible** : Facile d'ajouter des tokens plus tard

### 📋 Plan d'Action

1. **Créer** `frontend/frontend/src/design-tokens/index.js`
2. **Implémenter** les 6 exports nécessaires :
   - `SobrietyLevel`
   - `getSobrietyConfig`
   - `getSobrietyFeature`
   - `zIndexLayers`
   - `breakpoints`
   - `sobrietyConfig`
3. **Tester** la compilation frontend
4. **Valider** le comportement des composants affectés

### ⚠️ Points d'Attention

- **Valeurs à deviner** : Certaines valeurs (ex: descriptions sobriety) doivent être inférées du code
- **Tests nécessaires** : Valider que `getSobrietyFeature` retourne les bonnes valeurs
- **Compatibilité** : S'assurer que les valeurs correspondent aux attentes du code existant

---

## 8. 📊 COMPARAISON DES STRATÉGIES

| Critère | Stratégie A (Suppression) | Stratégie B (Minimal) | Stratégie C (Complet) |
|---------|---------------------------|----------------------|----------------------|
| **Temps** | 30-45 min | 1-2 heures | 4-6 heures |
| **Maintenabilité** | ❌ Faible | ✅ Bonne | ✅ Excellente |
| **Cohérence** | ❌ Risque de divergence | ✅ Centralisé | ✅ Design System |
| **Extensibilité** | ❌ Difficile | ✅ Facile | ✅ Très facile |
| **Tests** | ❌ Non | ⚠️ Optionnel | ✅ Recommandé |
| **Documentation** | ❌ Non | ⚠️ Optionnel | ✅ Incluse |
| **Recommandation** | ⚠️ Urgence uniquement | ✅ **RECOMMANDÉ** | ⚠️ Si temps disponible |

---

## 9. ✅ CONCLUSION

### État Actuel
- 🔴 **11 fichiers** bloqués par import manquant
- 🔴 **Module `design-tokens`** complètement absent
- 🔴 **Compilation frontend** impossible

### Solution Recommandée
- ✅ **Stratégie B** : Créer `src/design-tokens/index.js` avec exports minimaux
- ⏱️ **Temps estimé** : 1-2 heures
- 🎯 **Objectif** : Build fonctionnel + code maintenable

### Prochaines Étapes
1. Implémenter la Stratégie B
2. Tester la compilation
3. Valider le comportement des composants
4. (Optionnel) Améliorer vers Stratégie C si temps disponible

---

**Date de génération** : 2025-12-21  
**Version** : 1.0.0

