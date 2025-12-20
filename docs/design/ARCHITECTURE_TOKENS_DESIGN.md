# 🎨 Architecture des Tokens Design

**Document** : Architecture centralisée des tokens design  
**Date** : 2025-12-19  
**Auteur** : Architecte Design System  
**Version** : 1.0

---

## 🎯 MISSION

**Objectif** : Créer une architecture de tokens design centralisée pour la gestion fine de la sobriété et des couches (Z-index).

**Constat Audit** : Tokens manquants pour la gestion fine de la sobriété et des couches (Z-index).

---

## ✅ ACTIONS RÉALISÉES

### 1. Échelle de Sobriété (1-5)

**Avant** :
```javascript
const [ecoMode, setEcoMode] = useState(false); // Booléen binaire
```

**Problème** :
- ❌ Mode éco binaire (on/off)
- ❌ Pas de granularité fine
- ❌ Impossible de désactiver progressivement les features

**Après** :
```javascript
// Type SobrietyLevel = 1 | 2 | 3 | 4 | 5
export const SobrietyLevel = {
  FULL: 1,      // Full 3D + Bloom
  SIMPLIFIED: 2, // 3D simplifié
  FLAT: 3,      // 2D uniquement
  MINIMAL: 4,   // Animations minimales
  TEXT_ONLY: 5  // Texte seul, zéro animation
};

const [sobrietyLevel, setSobrietyLevel] = useState(SobrietyLevel.FULL);
```

**Configuration par niveau** :
- **Niveau 1 (Full)** : Full 3D + Bloom + Animations + Parallax + Particles
- **Niveau 2 (Simplified)** : 3D simplifié (pas de bloom, pas de particles)
- **Niveau 3 (Flat)** : 2D uniquement (pas de 3D, pas de parallax)
- **Niveau 4 (Minimal)** : Animations minimales (transitions basiques uniquement)
- **Niveau 5 (Text Only)** : Texte seul, zéro animation

**Impact** :
- ✅ **Granularité fine** : 5 niveaux au lieu de 2 (on/off)
- ✅ **Dégradation progressive** : Désactivation progressive des features
- ✅ **Performance adaptative** : Ajustement selon contexte (batterie, device)

---

### 2. Gestion Z-Index Centralisée

**Avant** :
```css
z-index: 40; /* Navbar - valeur hardcodée */
z-index: 1001; /* Modal - valeur hardcodée */
z-index: 999; /* Cursor - valeur hardcodée */
```

**Problème** :
- ❌ Valeurs hardcodées dispersées
- ❌ Risque de conflits z-index
- ❌ Pas de cohérence

**Après** :
```javascript
export const zIndexLayers = {
  base: 0,
  background: -1,
  content: 1,
  floating: 10,
  dropdown: 20,
  sticky: 30,
  nav: 40,
  overlay: 50,
  modal: 100,
  tooltip: 200,
  cursor: 999,
  max: 9999,
};
```

**Variables CSS** :
```css
:root {
  --z-base: 0;
  --z-background: -1;
  --z-content: 1;
  --z-floating: 10;
  --z-dropdown: 20;
  --z-sticky: 30;
  --z-nav: 40;
  --z-overlay: 50;
  --z-modal: 100;
  --z-tooltip: 200;
  --z-cursor: 999;
  --z-max: 9999;
}
```

**Impact** :
- ✅ **Cohérence** : Tous les z-index centralisés
- ✅ **Maintenabilité** : Modification en un seul endroit
- ✅ **Prévention conflits** : Hiérarchie claire

---

### 3. Breakpoints Centralisés

**Avant** :
```css
@media (max-width: 768px) { ... }
@media (max-width: 1024px) { ... }
/* Valeurs dispersées */
```

**Problème** :
- ❌ Valeurs hardcodées dispersées
- ❌ Pas de cohérence entre composants
- ❌ Difficile à maintenir

**Après** :
```javascript
export const breakpoints = {
  xs: '320px',   // Extra small (mobile portrait)
  sm: '640px',   // Small (mobile landscape)
  md: '768px',   // Medium (tablet)
  lg: '1024px',  // Large (desktop)
  xl: '1280px',  // Extra large (large desktop)
  '2xl': '1536px', // 2X Large (ultra-wide)
};

export const mediaQueries = {
  xs: `(min-width: ${breakpoints.xs})`,
  sm: `(min-width: ${breakpoints.sm})`,
  md: `(min-width: ${breakpoints.md})`,
  lg: `(min-width: ${breakpoints.lg})`,
  xl: `(min-width: ${breakpoints.xl})`,
  '2xl': `(min-width: ${breakpoints['2xl']})`,
  maxXs: `(max-width: ${parseInt(breakpoints.xs) - 1}px)`,
  maxSm: `(max-width: ${parseInt(breakpoints.sm) - 1}px)`,
  maxMd: `(max-width: ${parseInt(breakpoints.md) - 1}px)`,
  maxLg: `(max-width: ${parseInt(breakpoints.lg) - 1}px)`,
  maxXl: `(max-width: ${parseInt(breakpoints.xl) - 1}px)`,
};
```

**Variables CSS** :
```css
:root {
  --breakpoint-xs: 320px;
  --breakpoint-sm: 640px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 1024px;
  --breakpoint-xl: 1280px;
  --breakpoint-2xl: 1536px;
}
```

**Impact** :
- ✅ **Cohérence** : Tous les breakpoints centralisés
- ✅ **Maintenabilité** : Modification en un seul endroit
- ✅ **Réutilisabilité** : Exportable pour JavaScript et CSS

---

## 📊 IMPLÉMENTATION

### 1. Fichiers Créés

**`frontend/frontend/src/design-tokens/index.js`** :
- Export des tokens JavaScript
- `SobrietyLevel` (1-5)
- `sobrietyConfig` (configuration par niveau)
- `zIndexLayers` (couches z-index)
- `breakpoints` (responsive)
- `mediaQueries` (helpers)

**`frontend/frontend/src/design-tokens/tokens.css`** :
- Variables CSS pour z-index
- Variables CSS pour breakpoints
- Classes utilitaires pour z-index
- Classes pour niveaux de sobriété

---

### 2. Mise à Jour EcoModeContext

**Avant** :
```javascript
const [ecoMode, setEcoMode] = useState(false);
```

**Après** :
```javascript
const [sobrietyLevel, setSobrietyLevel] = useState(SobrietyLevel.FULL);

// Rétrocompatibilité
const [ecoMode, setEcoMode] = useState(false);
```

**Fonctionnalités** :
- ✅ **Échelle de sobriété** : Gestion des niveaux 1-5
- ✅ **API Batterie** : Calcul automatique du niveau selon batterie
- ✅ **Rétrocompatibilité** : `ecoMode` booléen toujours disponible
- ✅ **Classes CSS** : Application automatique des classes `sobriety-{level}`

---

### 3. Utilisation dans le Code

**JavaScript** :
```javascript
import { SobrietyLevel, zIndexLayers, breakpoints } from '@/design-tokens';
import { useEcoMode } from '@/contexts/EcoModeContext';

function MyComponent() {
  const { sobrietyLevel, sobrietyConfig } = useEcoMode();
  
  // Vérifier si 3D est activé
  if (sobrietyConfig.features.enable3D) {
    // Rendre composant 3D
  }
  
  // Utiliser z-index
  <div style={{ zIndex: zIndexLayers.modal }}>
    Modal
  </div>
}
```

**CSS** :
```css
.my-component {
  z-index: var(--z-modal);
}

@media (min-width: var(--breakpoint-md)) {
  .my-component {
    /* Styles desktop */
  }
}

/* Conditionnel selon sobriété */
.sobriety-3 [data-3d],
.sobriety-4 [data-3d],
.sobriety-5 [data-3d] {
  display: none !important;
}
```

---

## 📈 MAPPING BATTERIE → SOBRIÉTÉ

**Calcul automatique** :
```javascript
const calculateBatterySobrietyLevel = (battery) => {
  const level = battery.level; // 0.0 à 1.0
  const charging = battery.charging;

  if (level < 0.1 || (!charging && level < 0.15)) {
    return SobrietyLevel.TEXT_ONLY; // Niveau 5
  } else if (level < 0.2 || (!charging && level < 0.3)) {
    return SobrietyLevel.MINIMAL; // Niveau 4
  } else if (level < 0.4 || !charging) {
    return SobrietyLevel.FLAT; // Niveau 3
  } else if (level < 0.6) {
    return SobrietyLevel.SIMPLIFIED; // Niveau 2
  }
  return SobrietyLevel.FULL; // Niveau 1
};
```

**Mapping** :
- **Batterie < 10% OU (< 15% et non chargée)** → Niveau 5 (Text Only)
- **Batterie < 20% OU (< 30% et non chargée)** → Niveau 4 (Minimal)
- **Batterie < 40% OU non chargée** → Niveau 3 (Flat)
- **Batterie < 60%** → Niveau 2 (Simplified)
- **Batterie >= 60% et chargée** → Niveau 1 (Full)

---

## ✅ VALIDATION

### Tests de Performance

**Scénarios** :
1. ✅ **Niveau 1** : Full 3D + Bloom (performance maximale)
2. ✅ **Niveau 2** : 3D simplifié (performance medium-high)
3. ✅ **Niveau 3** : 2D uniquement (performance medium)
4. ✅ **Niveau 4** : Animations minimales (performance low)
5. ✅ **Niveau 5** : Texte seul (performance minimal)

### Tests Visuels

**Scénarios** :
1. ✅ **Z-Index** : Hiérarchie cohérente (pas de conflits)
2. ✅ **Breakpoints** : Responsive cohérent
3. ✅ **Sobriété** : Dégradation progressive visible
4. ✅ **Rétrocompatibilité** : Ancien code fonctionne toujours

---

## 🎯 OBJECTIF ATTEINT

**Mission** : Architecture de tokens design centralisée

**Résultat** :
- ✅ **Échelle de Sobriété** : 5 niveaux (1-5) au lieu de booléen
- ✅ **Z-Index** : Centralisé et cohérent
- ✅ **Breakpoints** : Centralisés et exportables
- ✅ **Rétrocompatibilité** : Ancien code fonctionne toujours

**Verdict** : **Architecture Design System complète** ✅

---

## 📝 FICHIERS CRÉÉS/MODIFIÉS

1. `frontend/frontend/src/design-tokens/index.js` (NOUVEAU)
   - Tokens JavaScript exportables
   - SobrietyLevel, zIndexLayers, breakpoints

2. `frontend/frontend/src/design-tokens/tokens.css` (NOUVEAU)
   - Variables CSS pour z-index et breakpoints
   - Classes utilitaires

3. `frontend/frontend/src/contexts/EcoModeContext.jsx` (MODIFIÉ)
   - Échelle de sobriété (1-5)
   - Rétrocompatibilité avec ecoMode booléen

4. `frontend/frontend/src/styles/global.css` (MODIFIÉ)
   - Import de tokens.css

---

## 🔄 EXEMPLE D'UTILISATION

### Dans un Composant React

```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';
import { SobrietyLevel, zIndexLayers } from '@/design-tokens';

function MyComponent() {
  const { sobrietyLevel, sobrietyConfig } = useEcoMode();
  
  return (
    <div 
      style={{ zIndex: zIndexLayers.modal }}
      data-3d={sobrietyConfig.features.enable3D}
      data-bloom={sobrietyConfig.features.enableBloom}
    >
      {sobrietyConfig.features.enable3D ? (
        <ThreeDComponent />
      ) : (
        <FlatComponent />
      )}
    </div>
  );
}
```

### Dans CSS

```css
.my-component {
  z-index: var(--z-modal);
}

@media (min-width: var(--breakpoint-md)) {
  .my-component {
    /* Styles desktop */
  }
}

/* Désactiver 3D selon sobriété */
.sobriety-3 [data-3d],
.sobriety-4 [data-3d],
.sobriety-5 [data-3d] {
  display: none !important;
}
```

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : ✅ Architecture Tokens Design complète**

