# 🧪 Tests à faire - Pages avec style Citations

## 📋 Résumé

Après l'application du style Citations aux pages du navbar, voici les tests à créer ou mettre à jour.

---

## ✅ Tests à METTRE À JOUR (pages existantes)

### 1. **Univers.test.jsx** ❌ À mettre à jour

**Problème** : Les tests cherchent des éléments qui n'existent plus (ancien style)

**Tests à mettre à jour** :
- ✅ Vérifier que la page s'affiche
- ❌ **NOUVEAU** : Vérifier le badge "Explorer le vivant"
- ❌ **NOUVEAU** : Vérifier le titre "Univers" dans `.citations-hero__title`
- ❌ **NOUVEAU** : Vérifier le sous-titre
- ❌ **NOUVEAU** : Vérifier le blockquote highlight
- ❌ **NOUVEAU** : Vérifier les stats (3 éléments)
- ✅ Vérifier les 3 thématiques (Le Vivant, L'Histoire, La Reliance)
- ❌ **NOUVEAU** : Vérifier la section CTA "Un monde en transition"
- ❌ **NOUVEAU** : Vérifier les liens de navigation (Découvrir les projets, Rejoindre)
- ❌ **NOUVEAU** : Vérifier la section références

**Structure attendue** :
```javascript
describe('Univers', () => {
  it('devrait afficher le hero avec badge', () => {
    // Vérifier citations-hero__badge "Explorer le vivant"
  });
  
  it('devrait afficher le titre principal', () => {
    // Vérifier citations-hero__title "Univers"
  });
  
  it('devrait afficher le blockquote highlight', () => {
    // Vérifier citations-hero__highlight avec texte et auteur
  });
  
  it('devrait afficher les stats', () => {
    // Vérifier citations-hero__stats avec 3 éléments
  });
  
  it('devrait afficher les 3 thématiques', () => {
    // Vérifier citation-group pour chaque thématique
  });
  
  it('devrait afficher la section CTA', () => {
    // Vérifier citations-cta avec titre et boutons
  });
});
```

---

### 2. **Vision.test.jsx** ❌ À mettre à jour

**Problème** : Les tests cherchent "Notre Vision" mais le nouveau titre est "Vision"

**Tests à mettre à jour** :
- ✅ Vérifier que la page s'affiche
- ❌ **NOUVEAU** : Vérifier le badge "Notre vision"
- ❌ **NOUVEAU** : Vérifier le titre "Vision" dans `.citations-hero__title`
- ❌ **NOUVEAU** : Vérifier le blockquote highlight
- ❌ **NOUVEAU** : Vérifier les stats
- ❌ **NOUVEAU** : Vérifier les 3 piliers (Relier, Apprendre en faisant, Transmettre)
- ❌ **NOUVEAU** : Vérifier la section CTA "Rejoignez notre vision"
- ❌ **NOUVEAU** : Vérifier la section références "Nos valeurs"

---

### 3. **Alliances.test.jsx** ❌ À mettre à jour

**Problème** : Les tests cherchent des éléments avec `data-testid="alliance-1"` qui n'existent plus

**Tests à mettre à jour** :
- ✅ Vérifier que la page s'affiche
- ❌ **NOUVEAU** : Vérifier le badge "Réseau de coopération"
- ❌ **NOUVEAU** : Vérifier le titre "Alliances"
- ❌ **NOUVEAU** : Vérifier le blockquote highlight
- ❌ **NOUVEAU** : Vérifier les stats
- ❌ **NOUVEAU** : Vérifier les 3 types d'alliances (territoriales, savoirs, internationales)
- ❌ **NOUVEAU** : Vérifier la section CTA "Devenez notre allié·e"
- ❌ **NOUVEAU** : Vérifier la section références "Nos partenaires"

---

### 4. **Projets.test.jsx** ⚠️ À mettre à jour partiellement

**État** : Les tests fonctionnent mais doivent être adaptés au nouveau style

**Tests à mettre à jour** :
- ✅ Vérifier que la page s'affiche
- ✅ Vérifier le loader (déjà OK)
- ✅ Vérifier la liste des projets (déjà OK)
- ❌ **NOUVEAU** : Vérifier le badge "Nos projets"
- ❌ **NOUVEAU** : Vérifier le hero avec blockquote
- ❌ **NOUVEAU** : Vérifier les stats dynamiques (nombre de projets)
- ❌ **NOUVEAU** : Vérifier que les projets utilisent `.citation-group`
- ❌ **NOUVEAU** : Vérifier la section CTA "Participez à nos projets"
- ✅ Vérifier les erreurs (déjà OK mais adapter au nouveau style)

---

## 🆕 Tests à CRÉER (nouvelles pages)

### 5. **Communaute.test.jsx** ❌ À créer

**Page** : `/communaute`

**Tests à créer** :
```javascript
describe('Communaute', () => {
  it('devrait afficher la page Communauté', () => {
    // Vérifier que la page s'affiche
  });
  
  it('devrait afficher le badge "Communauté vivante"', () => {
    // Vérifier citations-hero__badge
  });
  
  it('devrait afficher le titre "Communauté"', () => {
    // Vérifier citations-hero__title
  });
  
  it('devrait afficher le blockquote highlight', () => {
    // Vérifier citations-hero__highlight
  });
  
  it('devrait afficher les stats', () => {
    // Vérifier citations-hero__stats avec 3 éléments
  });
  
  it('devrait afficher les 3 façons de s\'engager', () => {
    // Vérifier les 3 citation-group
  });
  
  it('devrait afficher la section CTA', () => {
    // Vérifier citations-cta avec boutons
  });
  
  it('devrait afficher la section références', () => {
    // Vérifier citations-references "Nos valeurs"
  });
  
  it('devrait avoir des liens de navigation fonctionnels', () => {
    // Vérifier les liens vers /rejoindre et /projets
  });
});
```

---

### 6. **Votes.test.jsx** ❌ À créer

**Page** : `/votes`

**Tests à créer** :
```javascript
describe('Votes', () => {
  it('devrait afficher la page Votes', () => {
    // Vérifier que la page s'affiche
  });
  
  it('devrait afficher le badge "Démocratie participative"', () => {
    // Vérifier citations-hero__badge
  });
  
  it('devrait afficher le titre "Votes"', () => {
    // Vérifier citations-hero__title
  });
  
  it('devrait afficher le blockquote highlight', () => {
    // Vérifier citations-hero__highlight
  });
  
  it('devrait afficher les stats', () => {
    // Vérifier citations-hero__stats avec 3 éléments
  });
  
  it('devrait afficher les 3 principes de gouvernance', () => {
    // Vérifier les 3 citation-group
  });
  
  it('devrait afficher la section CTA', () => {
    // Vérifier citations-cta avec boutons
  });
  
  it('devrait afficher la section références', () => {
    // Vérifier citations-references "Comment ça marche"
  });
  
  it('devrait avoir des liens de navigation fonctionnels', () => {
    // Vérifier les liens vers /rejoindre et /communaute
  });
});
```

---

## 🎯 Tests d'intégration (optionnel mais recommandé)

### 7. **Navigation entre pages** ✅ Déjà testé (E2E)

Les tests E2E Playwright dans `e2e/navigation.spec.js` devraient déjà couvrir la navigation entre toutes les pages.

**À vérifier** :
- ✅ Navigation vers `/univers`
- ✅ Navigation vers `/vision`
- ✅ Navigation vers `/citations`
- ✅ Navigation vers `/alliances`
- ✅ Navigation vers `/projets`
- ❌ **NOUVEAU** : Navigation vers `/communaute`
- ❌ **NOUVEAU** : Navigation vers `/votes`

---

## 📊 Priorités

### 🔴 **PRIORITÉ HAUTE** (À faire en premier)

1. ✅ **Mettre à jour Univers.test.jsx** - Page importante, tests cassés
2. ✅ **Mettre à jour Vision.test.jsx** - Page importante, tests cassés
3. ✅ **Mettre à jour Alliances.test.jsx** - Page importante, tests cassés
4. ✅ **Créer Communaute.test.jsx** - Nouvelle page, pas de tests
5. ✅ **Créer Votes.test.jsx** - Nouvelle page, pas de tests

### 🟡 **PRIORITÉ MOYENNE** (À faire ensuite)

6. ⚠️ **Mettre à jour Projets.test.jsx** - Tests fonctionnent mais à adapter
7. ✅ **Vérifier les tests E2E** - Ajouter `/communaute` et `/votes`

### 🟢 **PRIORITÉ BASSE** (Optionnel)

8. 📝 **Tests d'accessibilité** - Vérifier que les nouvelles pages sont accessibles
9. 🎨 **Tests visuels** - Vérifier que le style Citations est bien appliqué partout

---

## 🛠️ Structure de test recommandée

Tous les tests doivent suivre cette structure pour être cohérents :

```javascript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PageName from '../PageName';

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('PageName', () => {
  it('devrait afficher la page', () => {
    renderWithRouter(<PageName />);
    expect(screen.getByText(/PageName/i)).toBeInTheDocument();
  });
  
  it('devrait afficher le badge hero', () => {
    renderWithRouter(<PageName />);
    expect(screen.getByText(/Badge Text/i)).toBeInTheDocument();
  });
  
  it('devrait afficher le titre principal', () => {
    renderWithRouter(<PageName />);
    const title = screen.getByRole('heading', { level: 1 });
    expect(title).toHaveTextContent(/PageName/i);
  });
  
  it('devrait afficher le blockquote highlight', () => {
    renderWithRouter(<PageName />);
    const blockquote = screen.getByRole('blockquote');
    expect(blockquote).toBeInTheDocument();
  });
  
  it('devrait afficher les stats', () => {
    renderWithRouter(<PageName />);
    const stats = screen.getByRole('definition');
    expect(stats).toBeInTheDocument();
  });
  
  it('devrait afficher les sections de contenu', () => {
    renderWithRouter(<PageName />);
    // Vérifier les citation-group
  });
  
  it('devrait afficher la section CTA', () => {
    renderWithRouter(<PageName />);
    // Vérifier citations-cta
  });
  
  it('devrait avoir des liens de navigation fonctionnels', () => {
    renderWithRouter(<PageName />);
    const links = screen.getAllByRole('link');
    // Vérifier les liens
  });
});
```

---

## ✅ Checklist finale

- [ ] Univers.test.jsx mis à jour
- [ ] Vision.test.jsx mis à jour
- [ ] Alliances.test.jsx mis à jour
- [ ] Projets.test.jsx mis à jour
- [ ] Communaute.test.jsx créé
- [ ] Votes.test.jsx créé
- [ ] Tests E2E mis à jour pour nouvelles routes
- [ ] Tous les tests passent
- [ ] Couverture de code maintenue (>70%)

---

**Note** : Tous les tests doivent préserver le visuel (utiliser des mocks pour les dépendances complexes, ne pas modifier les composants de production).

