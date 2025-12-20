# 🧪 Guide de Test Manuel - Échelle de Sobriété

**Document** : Guide pour tester manuellement l'échelle de sobriété (1-5)  
**Date** : 2025-12-19  
**Auteur** : Architecte Design System  
**Version** : 1.0

---

## 🎯 OBJECTIF

Valider que l'échelle de sobriété fonctionne correctement dans l'application en testant chaque niveau (1-5) et en vérifiant que les composants respectent les restrictions.

---

## 📋 PRÉREQUIS

1. **Application en développement**
   ```bash
   cd frontend/frontend
   npm run dev
   ```

2. **Backend démarré** (optionnel, pour tester les API)
   ```bash
   cd backend
   python manage.py runserver
   ```

3. **Navigateur** : Chrome, Firefox, ou Edge (avec DevTools)

---

## 🧪 TESTS PAR NIVEAU

### Niveau 1 : Full (Full 3D + Bloom)

**Configuration** :
- 3D : ✅ Activé
- Bloom : ✅ Activé
- Animations : ✅ Activées
- Parallaxe : ✅ Activée
- Particles : ✅ Activées
- Shadows : ✅ Activées
- Gradients : ✅ Activés

**Tests à effectuer** :

1. **HeroSorgho (3D)**
   - [ ] Ouvrir la page d'accueil (`/`)
   - [ ] Vérifier que le champ 3D de sorgho s'affiche
   - [ ] Vérifier que les particules sont animées
   - [ ] Vérifier que le bloom est visible (effet lumineux)

2. **MyceliumVisualization (3D)**
   - [ ] Naviguer vers `/mycelium` (ou page avec visualisation mycélium)
   - [ ] Vérifier que la visualisation 3D s'affiche
   - [ ] Vérifier que les nœuds sont visibles
   - [ ] Vérifier que le bloom est activé (si applicable)

3. **Animations**
   - [ ] Vérifier que les animations GSAP fonctionnent
   - [ ] Vérifier que les transitions sont fluides
   - [ ] Vérifier que le parallaxe fonctionne au scroll

4. **Performance**
   - [ ] Ouvrir DevTools → Performance
   - [ ] Enregistrer 10 secondes
   - [ ] Vérifier que les FPS sont stables (≈60 FPS)
   - [ ] Vérifier que la consommation GPU est normale

**Résultat attendu** : ✅ Toutes les fonctionnalités visuelles sont actives

---

### Niveau 2 : Simplified (3D simplifié, pas de bloom)

**Configuration** :
- 3D : ✅ Activé
- Bloom : ❌ Désactivé
- Animations : ✅ Activées
- Parallaxe : ✅ Activée
- Particles : ❌ Désactivées
- Shadows : ✅ Activées
- Gradients : ✅ Activés

**Tests à effectuer** :

1. **HeroSorgho (3D)**
   - [ ] Changer le niveau à 2 via `EcoModeToggle`
   - [ ] Vérifier que le champ 3D s'affiche toujours
   - [ ] Vérifier que le bloom est désactivé (moins lumineux)
   - [ ] Vérifier que les particules sont réduites ou absentes

2. **MyceliumVisualization (3D)**
   - [ ] Vérifier que la visualisation 3D s'affiche
   - [ ] Vérifier que le bloom est désactivé
   - [ ] Vérifier que les effets de particules sont réduits

3. **Animations**
   - [ ] Vérifier que les animations fonctionnent toujours
   - [ ] Vérifier que le parallaxe fonctionne

**Résultat attendu** : ✅ 3D actif mais sans bloom, performances améliorées

---

### Niveau 3 : Flat (2D uniquement, pas de 3D)

**Configuration** :
- 3D : ❌ Désactivé
- Bloom : ❌ Désactivé
- Animations : ✅ Activées
- Parallaxe : ❌ Désactivée
- Particles : ❌ Désactivées
- Shadows : ❌ Désactivées
- Gradients : ✅ Activés

**Tests à effectuer** :

1. **HeroSorgho (Fallback 2D)**
   - [ ] Changer le niveau à 3 via `EcoModeToggle`
   - [ ] Vérifier que le champ 3D est remplacé par une version statique
   - [ ] Vérifier que le texte "EGOEJO - Collectif pour le vivant" s'affiche
   - [ ] Vérifier qu'aucun rendu 3D n'est présent

2. **MyceliumVisualization (Fallback 2D)**
   - [ ] Vérifier que la visualisation 3D est désactivée
   - [ ] Vérifier qu'un message ou une version 2D s'affiche
   - [ ] Vérifier qu'aucun canvas WebGL n'est présent

3. **Animations**
   - [ ] Vérifier que les animations CSS fonctionnent
   - [ ] Vérifier que le parallaxe est désactivé (pas de mouvement au scroll)

4. **Performance**
   - [ ] Vérifier que la consommation GPU est très faible
   - [ ] Vérifier que les FPS sont stables (≈60 FPS)

**Résultat attendu** : ✅ Pas de 3D, interface 2D uniquement, performances optimales

---

### Niveau 4 : Minimal (Animations minimales)

**Configuration** :
- 3D : ❌ Désactivé
- Bloom : ❌ Désactivé
- Animations : ❌ Désactivées
- Parallaxe : ❌ Désactivée
- Particles : ❌ Désactivées
- Shadows : ❌ Désactivées
- Gradients : ❌ Désactivés

**Tests à effectuer** :

1. **Composants 3D**
   - [ ] Changer le niveau à 4 via `EcoModeToggle`
   - [ ] Vérifier que tous les composants 3D sont désactivés
   - [ ] Vérifier que les fallbacks 2D s'affichent

2. **Animations**
   - [ ] Vérifier que les animations GSAP sont désactivées
   - [ ] Vérifier que les transitions CSS sont minimales
   - [ ] Vérifier que le parallaxe est désactivé
   - [ ] Vérifier que `CardTilt` ne fonctionne pas

3. **CompostAnimation**
   - [ ] Naviguer vers une page avec compostage SAKA
   - [ ] Vérifier que l'animation de compostage est désactivée
   - [ ] Vérifier qu'une version simple s'affiche

4. **Performance**
   - [ ] Vérifier que la consommation CPU est très faible
   - [ ] Vérifier que la consommation GPU est nulle

**Résultat attendu** : ✅ Interface statique, animations minimales, consommation très faible

---

### Niveau 5 : Text Only (Texte seul, zéro animation)

**Configuration** :
- 3D : ❌ Désactivé
- Bloom : ❌ Désactivé
- Animations : ❌ Désactivées
- Parallaxe : ❌ Désactivée
- Particles : ❌ Désactivées
- Shadows : ❌ Désactivées
- Gradients : ❌ Désactivés

**Tests à effectuer** :

1. **Interface**
   - [ ] Changer le niveau à 5 via `EcoModeToggle`
   - [ ] Vérifier que l'interface est entièrement statique
   - [ ] Vérifier qu'aucune animation n'est présente
   - [ ] Vérifier qu'aucun effet visuel n'est présent

2. **Animations**
   - [ ] Vérifier que toutes les animations sont désactivées
   - [ ] Vérifier que les transitions sont désactivées
   - [ ] Vérifier que les hover effects sont minimaux

3. **Performance**
   - [ ] Vérifier que la consommation est minimale
   - [ ] Vérifier que le rendu est instantané

**Résultat attendu** : ✅ Interface texte uniquement, zéro animation, consommation minimale

---

## 🔍 VÉRIFICATIONS GLOBALES

### 1. Persistance

- [ ] Changer le niveau de sobriété
- [ ] Recharger la page (F5)
- [ ] Vérifier que le niveau est conservé dans `localStorage`
- [ ] Vérifier que le niveau est appliqué au chargement

### 2. Classes CSS

- [ ] Ouvrir DevTools → Elements
- [ ] Vérifier que `<html>` a la classe `sobriety-{level}`
- [ ] Vérifier que l'attribut `data-sobriety="{level}"` est présent
- [ ] Changer le niveau et vérifier que les classes sont mises à jour

### 3. API Batterie (si disponible)

- [ ] Vérifier que l'API Batterie est détectée
- [ ] Simuler une batterie faible (< 20%)
- [ ] Vérifier que le niveau de sobriété change automatiquement
- [ ] Vérifier que le niveau revient à 1 si la batterie est suffisante

### 4. Rétrocompatibilité

- [ ] Vérifier que `ecoMode` booléen fonctionne toujours
- [ ] Vérifier que les composants utilisant `ecoMode` fonctionnent
- [ ] Vérifier que la migration depuis l'ancien système fonctionne

---

## 📊 CHECKLIST COMPLÈTE

### Tests Fonctionnels
- [ ] Niveau 1 : Full 3D + Bloom fonctionne
- [ ] Niveau 2 : 3D simplifié fonctionne
- [ ] Niveau 3 : Fallback 2D fonctionne
- [ ] Niveau 4 : Animations minimales fonctionnent
- [ ] Niveau 5 : Texte seul fonctionne

### Tests de Performance
- [ ] Niveau 1 : Performance acceptable (≈60 FPS)
- [ ] Niveau 2 : Performance améliorée
- [ ] Niveau 3 : Performance optimale
- [ ] Niveau 4 : Consommation très faible
- [ ] Niveau 5 : Consommation minimale

### Tests d'Intégration
- [ ] Persistance dans localStorage
- [ ] Classes CSS appliquées
- [ ] API Batterie (si disponible)
- [ ] Rétrocompatibilité avec `ecoMode`

---

## 🐛 PROBLÈMES CONNUS

### API Batterie
- **Problème** : L'API Batterie n'est pas supportée par tous les navigateurs
- **Solution** : Le système fonctionne sans l'API, avec sélection manuelle

### Tests en Environnement de Test
- **Problème** : Les warnings "API Batterie non supportée" dans les tests
- **Solution** : Normal, jsdom ne supporte pas l'API Batterie

---

## ✅ CRITÈRES DE SUCCÈS

**Test réussi si** :
1. ✅ Tous les niveaux (1-5) fonctionnent correctement
2. ✅ Les composants 3D se désactivent selon le niveau
3. ✅ Les animations respectent les restrictions
4. ✅ La persistance fonctionne
5. ✅ Les performances s'améliorent avec les niveaux plus élevés

---

**Document généré le : 2025-12-19**  
**Version : 1.0**  
**Statut : ✅ Guide de Test Manuel prêt**

