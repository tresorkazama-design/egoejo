# 🌿 GUIDE : VISUALISATIONS "VIVANT"
## Pédagogie du Vivant (Mycélium, Cycles)

**Document** : Guidelines pour visualisations pédagogiques  
**Date** : 2025-12-19  
**Version** : 1.0  
**Audience** : Designers & Développeurs Frontend

---

## 🎯 PRINCIPE FONDAMENTAL

**Tout ajout visuel doit servir la pédagogie du "Vivant".**

Les visualisations doivent expliquer et illustrer les concepts EGOEJO à travers des métaphores naturelles : mycélium, cycles, croissance, réseaux.

---

## 🌾 MÉTAPHORES AUTORISÉES

### 1. Mycélium (Réseau de Connexions)

**Concept** : Réseau souterrain de champignons qui connecte les plantes.

**Usage** :
- Visualisation des projets et contenus connectés
- Réseau sémantique (embeddings)
- Connexions entre utilisateurs et projets

**Exemple** : `MyceliumVisualization.jsx`

**Éléments visuels** :
- Nœuds (projets/contenus)
- Filaments (connexions sémantiques)
- Croissance organique (nouveaux projets)

---

### 2. Cycle SAKA (Cycle de Vie)

**Concept** : Cycle complet du SAKA comme cycle de vie d'une plante.

**Étapes** :
1. **Récolte** (🌱 Germination) : Grains gagnés
2. **Usage** (🌿 Croissance) : Grains dépensés
3. **Compost** (🍂 Automne) : Grains inactifs retournent à la terre
4. **Silo** (💧 Réservoir) : Grains compostés collectés
5. **Redistribution** (🌧️ Irrigation) : Grains redistribués aux actifs

**Visualisation** : Cercle avec étapes animées

---

### 3. Silo Commun (Réservoir d'Eau)

**Concept** : Réservoir qui collecte l'eau (SAKA composté) et irrigue les plantes (redistribution).

**Éléments visuels** :
- Réservoir (Silo)
- Niveau d'eau (balance)
- Canaux d'irrigation (redistribution)
- Plantes irriguées (wallets actifs)

---

### 4. Croissance Organique

**Concept** : Visualisation de la croissance comme une plante qui pousse.

**Usage** :
- Accumulation SAKA (croissance)
- Nouveaux projets (germination)
- Engagement utilisateur (floraison)

---

## 🎨 PALETTE DE COULEURS

### Couleurs Autorisées

| Couleur | Code | Usage |
|---------|------|-------|
| 🌾 **Vert SAKA** | `#00ffa3` | Récolte, croissance SAKA |
| 🍂 **Orange Compost** | `#ff6b6b` | Compostage, transformation |
| 💧 **Bleu Silo** | `#4ecdc4` | Silo, redistribution |
| 🌿 **Vert Nature** | `#2d5016` | Fond, stabilité |
| 🌱 **Vert Clair** | `#90ee90` | Nouveautés, croissance |
| 🍃 **Vert Feuille** | `#7cb342` | Santé, vitalité |

### Couleurs Interdites

| Couleur | Raison |
|---------|--------|
| ❌ **Or/Jaune** | Trop monétaire |
| ❌ **Rouge Agressif** | Alarmiste, non naturel |
| ❌ **Gris Froid** | Technique, non vivant |

---

## 🎬 ANIMATIONS

### Style "Vivant"

**Caractéristiques** :
- **Fluide** : Transitions douces, organiques
- **Naturel** : Inspirées de la nature
- **Pédagogique** : Expliquent le concept

### Types d'Animations Autorisées

1. **Croissance** : Plante qui grandit (accumulation SAKA)
2. **Circulation** : Particules qui circulent (redistribution)
3. **Transformation** : Compost qui se transforme (compostage)
4. **Extension** : Réseau qui s'étend (nouveaux projets)
5. **Respiration** : Pulsation douce (santé système)

### Exemples

```jsx
// ✅ AUTORISÉ : Animation de croissance
<animated.div
  style={{
    height: `${sakaBalance}px`,
    transition: 'height 0.5s ease-out'
  }}
>
  {/* Plante qui grandit */}
</animated.div>

// ✅ AUTORISÉ : Particules qui circulent
<ParticleSystem
  source="silo"
  destination="wallets"
  color="#4ecdc4"
  speed={0.5}
/>

// ❌ INTERDIT : Animation technique (compteur numérique)
<Counter from={0} to={sakaBalance} />  // Trop technique
```

---

## 📐 COMPOSANTS À CRÉER

### 1. SakaCycleVisualization

**Fichier** : `frontend/frontend/src/components/saka/SakaCycleVisualization.jsx`

**Fonctionnalités** :
- Animation du cycle complet
- Indicateurs pour chaque étape
- Statistiques temps réel
- Légende pédagogique

**Design** :
- Cercle avec 5 étapes
- Flèches animées entre étapes
- Couleurs par étape (vert → orange → bleu)

---

### 2. SakaSiloRedistributionVisualization

**Fichier** : `frontend/frontend/src/components/saka/SakaSiloRedistributionVisualization.jsx`

**Fonctionnalités** :
- Visualisation du Silo (réservoir)
- Flux de redistribution (particules)
- Wallets actifs (plantes irriguées)
- Statistiques redistribution

**Design** :
- Réservoir en haut (Silo)
- Canaux d'irrigation (flux)
- Plantes en bas (wallets)

---

### 3. EcosystemeVivantDashboard

**Fichier** : `frontend/frontend/src/app/pages/EcosystemeVivant.jsx`

**Sections** :
1. Mycélium Numérique (réseau)
2. Cycle SAKA (cycle complet)
3. Silo Commun (redistribution)
4. Métriques Vivant (santé)

**Design** :
- Layout organique (pas de grille rigide)
- Transitions fluides entre sections
- Métaphores visuelles cohérentes

---

## ✅ CHECKLIST AVANT CRÉATION

### Vérifications Design

- [ ] Métaphore "Vivant" utilisée (mycélium, cycle, croissance)
- [ ] Palette couleurs autorisée (verts, oranges, bleus naturels)
- [ ] Animations fluides et pédagogiques
- [ ] Légende explicative présente
- [ ] Pas de références monétaires (€, $)
- [ ] Pas de graphiques financiers (candlesticks, etc.)

---

### Vérifications Technique

- [ ] Composant réutilisable
- [ ] Performance optimisée (lazy loading si nécessaire)
- [ ] Responsive (mobile-friendly)
- [ ] Accessible (ARIA labels)
- [ ] Tests unitaires présents

---

## 📚 EXEMPLES DE CODE

### Composant Cycle SAKA

```jsx
import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function SakaCycleVisualization({ userSaka }) {
  const stages = [
    { name: 'Récolte', icon: '🌱', color: '#00ffa3', progress: 100 },
    { name: 'Usage', icon: '🌿', color: '#7cb342', progress: 60 },
    { name: 'Compost', icon: '🍂', color: '#ff6b6b', progress: 10 },
    { name: 'Silo', icon: '💧', color: '#4ecdc4', progress: 10 },
    { name: 'Redistribution', icon: '🌧️', color: '#90ee90', progress: 5 },
  ];

  return (
    <div className="saka-cycle-visualization">
      <h2>Cycle du Vivant SAKA</h2>
      <div className="cycle-circle">
        {stages.map((stage, index) => (
          <motion.div
            key={stage.name}
            className="cycle-stage"
            initial={{ opacity: 0, scale: 0 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.2 }}
          >
            <div className="stage-icon">{stage.icon}</div>
            <div className="stage-name">{stage.name}</div>
            <div className="stage-progress" style={{ color: stage.color }}>
              {stage.progress}%
            </div>
          </motion.div>
        ))}
      </div>
      <p className="cycle-legend">
        Le SAKA suit un cycle naturel : Récolte → Usage → Compost → Silo → Redistribution.
        Chaque étape est essentielle pour maintenir l'écosystème vivant.
      </p>
    </div>
  );
}
```

---

## 🚫 INTERDICTIONS

### Métaphores Interdites

- ❌ Graphiques financiers (candlesticks, barres de trading)
- ❌ Compteurs numériques froids
- ❌ Indicateurs monétaires (€, $, % ROI)
- ❌ Métaphores bancaires (comptes, prêts, intérêts)

### Animations Interdites

- ❌ Animations techniques (compteurs, progress bars froides)
- ❌ Transitions brusques (non organiques)
- ❌ Effets "glitch" ou "tech"

---

## 📊 MÉTRIQUES DE SUCCÈS

### Pédagogie

- **Compréhension** : Utilisateurs comprennent le cycle SAKA
- **Engagement** : Visualisations incitent à l'action
- **Clarté** : Concepts expliqués visuellement

### Performance

- **LCP** : < 2.5s (mobile)
- **FID** : < 100ms
- **Animations** : 60 FPS

---

## 🔗 RÉFÉRENCES

- **MyceliumVisualization** : `frontend/frontend/src/components/MyceliumVisualization.jsx`
- **SakaSeasons** : `frontend/frontend/src/app/pages/SakaSeasons.tsx`
- **SakaSilo** : `frontend/frontend/src/app/pages/SakaSilo.jsx`

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : Guidelines Design**

