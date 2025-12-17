# 🚀 Guide de Test de Performance

**Date** : 2025-01-27

---

## 📊 Tests de Performance Disponibles

### 1. Analyse du Bundle (Script Automatique)

```bash
cd frontend/frontend
npm run build
npm run test:performance
```

**Ce qui est analysé** :
- ✅ Taille totale du bundle
- ✅ Taille des fichiers JS, CSS, images
- ✅ Code splitting (chunks vendors)
- ✅ Service Worker
- ✅ Preload/Preconnect

---

### 2. Lighthouse (Recommandé)

**Dans Chrome DevTools** :
1. Ouvrir l'application (dev ou preview)
2. Ouvrir DevTools (F12)
3. Onglet "Lighthouse"
4. Sélectionner "Performance"
5. Cliquer sur "Analyze page load"

**Métriques à vérifier** :
- **Performance** : Objectif > 85
- **First Contentful Paint (FCP)** : Objectif < 1.8s
- **Largest Contentful Paint (LCP)** : Objectif < 2.5s
- **Time to Interactive (TTI)** : Objectif < 3.8s
- **Total Blocking Time (TBT)** : Objectif < 200ms
- **Cumulative Layout Shift (CLS)** : Objectif < 0.1

---

### 3. Build et Analyse

```bash
cd frontend/frontend
npm run build:analyze
```

**Ce qui est fait** :
- Build de production
- Analyse automatique du bundle
- Rapport détaillé

---

### 4. WebPageTest (En ligne)

1. Aller sur https://www.webpagetest.org/
2. Entrer l'URL de votre site
3. Lancer le test
4. Analyser les résultats

**Métriques importantes** :
- Load Time
- First Byte
- Start Render
- Speed Index
- Visual Complete

---

### 5. Chrome DevTools - Network

**Pour analyser le chargement** :
1. Ouvrir DevTools (F12)
2. Onglet "Network"
3. Recharger la page
4. Vérifier :
   - Temps de chargement total
   - Taille des fichiers
   - Ordre de chargement
   - Waterfall

---

### 6. Chrome DevTools - Performance

**Pour analyser l'exécution** :
1. Ouvrir DevTools (F12)
2. Onglet "Performance"
3. Cliquer sur "Record"
4. Interagir avec la page
5. Arrêter l'enregistrement
6. Analyser :
   - FPS
   - CPU usage
   - Memory usage
   - Long tasks

---

## 📈 Métriques Cibles

### Bundle Size

- **Bundle initial** : < 300 KB (gzippé)
- **Total JS** : < 500 KB
- **Total CSS** : < 50 KB
- **Images** : < 1 MB (total)

### Performance Web Vitals

- **LCP** (Largest Contentful Paint) : < 2.5s
- **FID** (First Input Delay) : < 100ms
- **CLS** (Cumulative Layout Shift) : < 0.1
- **FCP** (First Contentful Paint) : < 1.8s
- **TTI** (Time to Interactive) : < 3.8s

### Lighthouse Score

- **Performance** : > 85
- **Accessibility** : > 90
- **Best Practices** : > 90
- **SEO** : > 90

---

## 🔍 Points à Vérifier

### ✅ Code Splitting

Vérifier que les chunks sont bien séparés :
- `react-vendor.js` (React, React DOM, React Router)
- `three-vendor.js` (Three.js)
- `gsap-vendor.js` (GSAP)
- Chunks par route (lazy loading)

### ✅ Service Worker

Vérifier dans DevTools → Application → Service Workers :
- Service worker actif
- Cache Storage rempli
- Assets en cache

### ✅ Lazy Loading

Vérifier dans Network :
- Les pages ne sont chargées qu'à la navigation
- Pas de chargement inutile au démarrage

### ✅ Images

Vérifier :
- Lazy loading activé
- Formats optimisés (WebP si possible)
- Tailles appropriées

---

## 🐛 Dépannage

### Bundle trop gros

1. Vérifier les imports inutiles
2. Vérifier le tree shaking
3. Vérifier les dépendances lourdes
4. Considérer le lazy loading supplémentaire

### Performance faible

1. Vérifier les long tasks (Performance tab)
2. Vérifier les requêtes réseau lentes
3. Vérifier le service worker
4. Vérifier les animations (Three.js)

### Service Worker ne fonctionne pas

1. Vérifier que le build a été fait
2. Vérifier la console pour les erreurs
3. Vérifier que HTTPS est utilisé (ou localhost)

---

## 📝 Checklist de Performance

- [ ] Bundle initial < 300 KB
- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1
- [ ] Lighthouse Performance > 85
- [ ] Service Worker actif
- [ ] Code splitting fonctionnel
- [ ] Lazy loading des pages
- [ ] Images optimisées
- [ ] Cache fonctionnel

---

## 🎯 Résultats Attendus

### Avant Optimisations
- Bundle initial : ~500-600 KB
- LCP : ~2-3s
- Lighthouse : ~70-80

### Après Optimisations
- Bundle initial : ~300-400 KB ⬇️
- LCP : ~1-1.5s ⬇️
- Lighthouse : ~85-95 ⬆️

---

## 💡 Améliorations Supplémentaires

Si les performances ne sont pas optimales :

1. **Images** :
   - Convertir en WebP
   - Utiliser srcset pour responsive
   - Compresser davantage

2. **Fonts** :
   - Utiliser font-display: swap
   - Précharger les fonts critiques
   - Limiter le nombre de fonts

3. **JavaScript** :
   - Réduire les dépendances
   - Utiliser des alternatives plus légères
   - Code splitting plus agressif

4. **CSS** :
   - Purge CSS inutilisé
   - Minification
   - Critical CSS inline

---

## 🚀 Commandes Rapides

```bash
# Build et analyse
npm run build:analyze

# Build seul
npm run build

# Preview du build
npm run preview

# Dev server
npm run dev
```

---

## 📚 Ressources

- [Web Vitals](https://web.dev/vitals/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [WebPageTest](https://www.webpagetest.org/)
- [Bundle Analyzer](https://www.npmjs.com/package/vite-bundle-visualizer)

