# 🎨 Guide : Réussir tous les tests sans casser le visuel

## 📋 Stratégie générale

**Principe fondamental** : Les tests ne doivent **JAMAIS** modifier les composants de production. On utilise des **mocks** pour isoler les dépendances complexes (Three.js, GSAP, etc.) dans les tests.

## ✅ Ce qui a été fait

### 1. **Mock de HeroSorgho** (Three.js)

**Fichier** : `src/app/pages/__tests__/Home.test.jsx`

```javascript
// Mock HeroSorgho pour éviter les problèmes avec Three.js dans les tests
// On garde juste un placeholder simple qui ne casse pas le visuel
vi.mock('../../components/HeroSorgho', () => ({
  default: () => <div data-testid="hero-sorgho" style={{ minHeight: '70svh' }} />,
}));
```

**Pourquoi** : Three.js nécessite un contexte WebGL qui n'existe pas dans jsdom. Le mock permet de tester la page Home sans initialiser Three.js, tout en préservant le composant original.

### 2. **Mock de scrollAnimations** (GSAP/ScrollTrigger)

**Fichier** : `src/components/__tests__/Layout.test.jsx`

```javascript
vi.mock('../../utils/scrollAnimations', () => ({
  initScrollAnimations: vi.fn(),
  cleanupScrollAnimations: vi.fn(),
}));
```

**Pourquoi** : GSAP/ScrollTrigger nécessite un environnement DOM réel avec scroll. Le mock évite les erreurs dans les tests unitaires.

### 3. **Mock de PageTransition** (GSAP)

**Fichier** : `src/components/__tests__/Layout.test.jsx`

```javascript
vi.mock('../PageTransition', () => ({
  default: ({ children }) => <div data-testid="page-transition">{children}</div>,
}));
```

**Pourquoi** : PageTransition utilise GSAP pour les animations. Le mock simplifie les tests sans affecter le composant de production.

### 4. **Mocks globaux dans setup.js**

**Fichier** : `src/test/setup.js`

- **ResizeObserver** : Utilisé par HeroSorgho
- **window.matchMedia** : Utilisé par HeroSorgho pour détecter `prefers-reduced-motion`
- **WebGL context** : Mock du contexte canvas pour Three.js

## 🎯 Tests mis à jour

### Home.test.jsx

**Avant** : Cherchait des éléments qui n'existaient pas (`getByText('Bienvenue sur EGOEJO')`)

**Après** : Vérifie les vrais éléments du visuel restauré :
- ✅ Tag "Collectif pour le vivant"
- ✅ Titre "Habiter la Terre autrement, ensemble."
- ✅ Description EGOEJO
- ✅ Boutons "Soutenir EGOEJO" et "Rejoindre l'Alliance"
- ✅ Trois piliers (Relier, Apprendre en faisant, Transmettre)
- ✅ Section "Nous soutenir"
- ✅ Liens de don

### Layout.test.jsx

**Avant** : Utilisait des props qui n'existent plus (`showNavbar`, `navbarProps`)

**Après** : Vérifie la structure réelle du Layout :
- ✅ Logo EGOEJO (Logo3D)
- ✅ Navigation principale
- ✅ Footer avec liens
- ✅ Structure header/main/footer

## 🔧 Règles d'or pour préserver le visuel

### ✅ À FAIRE

1. **Utiliser des mocks** pour les dépendances complexes (Three.js, GSAP, etc.)
2. **Tester les éléments visuels réels** (textes, classes CSS, structure HTML)
3. **Vérifier la présence** des composants sans les simplifier
4. **Isoler les tests** : chaque test doit être indépendant

### ❌ À NE PAS FAIRE

1. **Ne jamais modifier** les composants de production pour les tests
2. **Ne pas simplifier** les composants (ex: remplacer HeroSorgho par un div simple dans Home.jsx)
3. **Ne pas supprimer** les styles CSS ou les classes
4. **Ne pas changer** la structure HTML pour faciliter les tests

## 📝 Exemple de test correct

```javascript
// ✅ BON : Mock dans le test, composant original intact
vi.mock('../../components/HeroSorgho', () => ({
  default: () => <div data-testid="hero-sorgho" />,
}));

it('devrait afficher le tag "Collectif pour le vivant"', () => {
  renderWithRouter(<Home />);
  expect(screen.getByText('Collectif pour le vivant')).toBeInTheDocument();
});
```

```javascript
// ❌ MAUVAIS : Modification du composant de production
// Dans Home.jsx - NE PAS FAIRE ÇA
export default function Home() {
  return (
    <div>
      {process.env.NODE_ENV === 'test' ? (
        <div data-testid="hero-sorgho">Mock</div>
      ) : (
        <HeroSorgho />
      )}
    </div>
  );
}
```

## 🚀 Commandes pour lancer les tests

```bash
# Tous les tests
npm run test:run

# Tests en mode watch
npm run test

# Tests avec couverture
npm run test:coverage

# Tests d'accessibilité
npm run test:a11y

# Tests E2E (Playwright)
npm run test:e2e
```

## 🐛 Résolution de problèmes

### Problème : "Three.js context not available"

**Solution** : Vérifier que HeroSorgho est mocké dans le test :

```javascript
vi.mock('../../components/HeroSorgho', () => ({
  default: () => <div data-testid="hero-sorgho" />,
}));
```

### Problème : "GSAP/ScrollTrigger error"

**Solution** : Mocker scrollAnimations :

```javascript
vi.mock('../../utils/scrollAnimations', () => ({
  initScrollAnimations: vi.fn(),
  cleanupScrollAnimations: vi.fn(),
}));
```

### Problème : "ResizeObserver is not defined"

**Solution** : Ajouter dans `src/test/setup.js` :

```javascript
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
```

## 📊 État actuel

- ✅ **Home.test.jsx** : Mis à jour pour correspondre au visuel restauré
- ✅ **Layout.test.jsx** : Mis à jour pour la nouvelle structure
- ✅ **setup.js** : Mocks globaux pour ResizeObserver et WebGL
- ✅ **Composants de production** : **AUCUNE modification** - visuel intact

## 🎨 Vérification du visuel

Pour vérifier que le visuel n'est pas cassé :

1. **Lancer l'application** : `npm run dev`
2. **Vérifier** :
   - Logo 3D "E GOEJO" visible
   - Tag "Collectif pour le vivant" présent
   - Titre "Habiter la Terre autrement, ensemble."
   - Animation HeroSorgho (grains de sorgho) en arrière-plan
   - Navigation complète
   - Footer avec liens

3. **Si le visuel est cassé** : Vérifier que les composants de production n'ont pas été modifiés

## 🔄 Workflow recommandé

1. **Développement** : Modifier uniquement les composants de production
2. **Tests** : Créer/mettre à jour les tests avec des mocks appropriés
3. **Vérification** : Lancer les tests ET vérifier le visuel dans le navigateur
4. **Commit** : Si tests passent ET visuel intact → commit

---

**Rappel** : Les tests servent à vérifier que le code fonctionne, pas à le simplifier. Le visuel doit toujours être préservé ! 🎨

