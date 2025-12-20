# 📖 Guide d'Implémentation : Échelle de Sobriété

**Document** : Guide pratique pour utiliser l'échelle de sobriété dans le code existant  
**Date** : 2025-12-19  
**Auteur** : Architecte Design System  
**Version** : 1.0

---

## 🎯 OBJECTIF

Montrer comment implémenter l'échelle de sobriété (1-5) dans le code existant, en remplaçant progressivement le booléen `ecoMode`.

---

## 📋 ÉCHELLE DE SOBRIÉTÉ

### Niveaux

```javascript
import { SobrietyLevel } from '@/design-tokens';

// Niveau 1 : Full 3D + Bloom
SobrietyLevel.FULL

// Niveau 2 : 3D simplifié (pas de bloom)
SobrietyLevel.SIMPLIFIED

// Niveau 3 : 2D uniquement (pas de 3D)
SobrietyLevel.FLAT

// Niveau 4 : Animations minimales (transitions basiques)
SobrietyLevel.MINIMAL

// Niveau 5 : Texte seul, zéro animation
SobrietyLevel.TEXT_ONLY
```

---

## 🔧 UTILISATION DANS UN COMPOSANT

### Exemple 1 : Composant 3D Conditionnel

**Avant** :
```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';

function MyComponent() {
  const { ecoMode } = useEcoMode();
  
  if (ecoMode) {
    return <FlatComponent />;
  }
  return <ThreeDComponent />;
}
```

**Après** :
```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';
import { SobrietyLevel, getSobrietyFeature } from '@/design-tokens';

function MyComponent() {
  const { sobrietyLevel, sobrietyConfig } = useEcoMode();
  
  // Vérifier si 3D est activé
  const canRender3D = getSobrietyFeature(sobrietyLevel, 'enable3D');
  const canRenderBloom = getSobrietyFeature(sobrietyLevel, 'enableBloom');
  
  if (!canRender3D) {
    return <FlatComponent />;
  }
  
  return (
    <div data-3d>
      <ThreeDComponent />
      {canRenderBloom && (
        <div data-bloom>
          <BloomEffect />
        </div>
      )}
    </div>
  );
}
```

---

### Exemple 2 : Animations Conditionnelles

**Avant** :
```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';

function AnimatedComponent() {
  const { ecoMode } = useEcoMode();
  
  return (
    <div className={ecoMode ? '' : 'animate-fade-in'}>
      Content
    </div>
  );
}
```

**Après** :
```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';
import { getSobrietyFeature } from '@/design-tokens';

function AnimatedComponent() {
  const { sobrietyLevel } = useEcoMode();
  
  const canAnimate = getSobrietyFeature(sobrietyLevel, 'enableAnimations');
  
  return (
    <div 
      data-animation={canAnimate}
      className={canAnimate ? 'animate-fade-in' : ''}
    >
      Content
    </div>
  );
}
```

---

### Exemple 3 : Parallaxe Conditionnelle

**Avant** :
```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';

function ParallaxSection() {
  const { ecoMode } = useEcoMode();
  
  useEffect(() => {
    if (ecoMode) return;
    
    // Setup parallax
    gsap.to(section, {
      y: -40,
      scrollTrigger: { ... }
    });
  }, [ecoMode]);
}
```

**Après** :
```javascript
import { useEcoMode } from '@/contexts/EcoModeContext';
import { getSobrietyFeature } from '@/design-tokens';

function ParallaxSection() {
  const { sobrietyLevel } = useEcoMode();
  
  const canParallax = getSobrietyFeature(sobrietyLevel, 'enableParallax');
  
  useEffect(() => {
    if (!canParallax) return;
    
    // Setup parallax
    gsap.to(section, {
      y: -40,
      scrollTrigger: { ... }
    });
  }, [canParallax]);
  
  return (
    <section data-parallax={canParallax}>
      Content
    </section>
  );
}
```

---

## 🎨 UTILISATION EN CSS

### Exemple 1 : Désactiver 3D selon Sobriété

**CSS** :
```css
/* Désactiver 3D pour niveaux 3, 4, 5 */
.sobriety-3 [data-3d],
.sobriety-4 [data-3d],
.sobriety-5 [data-3d] {
  display: none !important;
}

/* Désactiver bloom pour niveaux 2, 3, 4, 5 */
.sobriety-2 [data-bloom],
.sobriety-3 [data-bloom],
.sobriety-4 [data-bloom],
.sobriety-5 [data-bloom] {
  filter: none !important;
  backdrop-filter: none !important;
}
```

**HTML** :
```html
<div data-3d>
  <ThreeDComponent />
</div>
```

---

### Exemple 2 : Désactiver Animations selon Sobriété

**CSS** :
```css
/* Désactiver animations pour niveaux 4, 5 */
.sobriety-4 [data-animation],
.sobriety-5 [data-animation] {
  animation: none !important;
  transition: none !important;
}

/* Désactiver toutes animations pour niveau 5 */
.sobriety-5 * {
  animation: none !important;
  transition: none !important;
}
```

**HTML** :
```html
<div data-animation>
  <AnimatedComponent />
</div>
```

---

### Exemple 3 : Utiliser Z-Index Centralisé

**CSS** :
```css
.modal {
  z-index: var(--z-modal); /* 100 */
}

.tooltip {
  z-index: var(--z-tooltip); /* 200 */
}

.cursor {
  z-index: var(--z-cursor); /* 999 */
}
```

**JavaScript** :
```javascript
import { zIndexLayers } from '@/design-tokens';

<div style={{ zIndex: zIndexLayers.modal }}>
  Modal
</div>
```

---

## 🔄 MIGRATION PROGRESSIVE

### Étape 1 : Rétrocompatibilité

Le code existant continue de fonctionner :
```javascript
const { ecoMode } = useEcoMode(); // Fonctionne toujours
```

### Étape 2 : Migration Progressive

Remplacer progressivement :
```javascript
// Ancien
const { ecoMode } = useEcoMode();
if (ecoMode) { ... }

// Nouveau
const { sobrietyLevel, sobrietyConfig } = useEcoMode();
if (sobrietyConfig.features.enable3D) { ... }
```

### Étape 3 : Utilisation Avancée

Utiliser les helpers :
```javascript
import { getSobrietyFeature } from '@/design-tokens';

const canRender3D = getSobrietyFeature(sobrietyLevel, 'enable3D');
const canRenderBloom = getSobrietyFeature(sobrietyLevel, 'enableBloom');
```

---

## 📊 MAPPING BATTERIE → SOBRIÉTÉ

**Calcul automatique** :
- **Batterie < 10% OU (< 15% et non chargée)** → Niveau 5 (Text Only)
- **Batterie < 20% OU (< 30% et non chargée)** → Niveau 4 (Minimal)
- **Batterie < 40% OU non chargée** → Niveau 3 (Flat)
- **Batterie < 60%** → Niveau 2 (Simplified)
- **Batterie >= 60% et chargée** → Niveau 1 (Full)

---

## ✅ CHECKLIST DE MIGRATION

- [ ] Importer `SobrietyLevel` et `getSobrietyFeature` depuis `@/design-tokens`
- [ ] Remplacer `ecoMode` par `sobrietyLevel` et `sobrietyConfig`
- [ ] Utiliser `getSobrietyFeature()` pour vérifier les features
- [ ] Ajouter attributs `data-3d`, `data-bloom`, `data-animation`, etc.
- [ ] Utiliser classes CSS `.sobriety-{level}` pour styles conditionnels
- [ ] Utiliser `zIndexLayers` pour z-index centralisés
- [ ] Utiliser `breakpoints` pour media queries

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : ✅ Guide d'Implémentation complet**

