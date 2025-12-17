# 🚀 Guide de Test de Performance - EGOEJO

**Date** : 2025-01-27

---

## 📋 Tests Disponibles

### 1. Test Automatique (Script)

```bash
cd frontend/frontend
npm run build
npm run test:performance
```

**Ce que le script vérifie** :
- ✅ Taille des bundles
- ✅ Code splitting (chunks React, Three.js, GSAP)
- ✅ Service worker
- ✅ Manifest PWA
- ✅ Lazy loading des pages
- ✅ Optimisations Three.js
- ✅ Preload/prefetch

---

### 2. Test Lighthouse (Recommandé)

#### Méthode 1 : Chrome DevTools

1. **Lancer l'application** :
   ```bash
   cd frontend/frontend
   npm run build
   npm run preview
   ```

2. **Ouvrir Chrome DevTools** :
   - F12 ou Clic droit → Inspecter
   - Onglet **Lighthouse**

3. **Configurer l'audit** :
   - ✅ Performance
   - ✅ Accessibility
   - ✅ Best Practices
   - ✅ SEO
   - Mode : **Navigation**

4. **Lancer l'audit** :
   - Cliquer sur "Analyze page load"
   - Attendre les résultats

5. **Vérifier les métriques** :
   - **Performance Score** : Objectif 90+
   - **First Contentful Paint (FCP)** : < 1.8s
   - **Largest Contentful Paint (LCP)** : < 2.5s
   - **Time to Interactive (TTI)** : < 3.8s
   - **Total Blocking Time (TBT)** : < 200ms
   - **Cumulative Layout Shift (CLS)** : < 0.1

#### Méthode 2 : Lighthouse CLI

```bash
# Installer Lighthouse CLI
npm install -g lighthouse

# Lancer un audit
lighthouse http://localhost:4173 --view
```

---

### 3. Test Web Vitals

#### Extension Chrome

1. Installer l'extension **Web Vitals** depuis le Chrome Web Store
2. Ouvrir votre site
3. Vérifier les métriques en temps réel :
   - **FCP** (First Contentful Paint)
   - **LCP** (Largest Contentful Paint)
   - **FID** (First Input Delay)
   - **CLS** (Cumulative Layout Shift)
   - **TTFB** (Time to First Byte)

#### Code JavaScript

```javascript
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  console.log(metric);
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

---

### 4. Test de Performance Chrome DevTools

1. **Ouvrir DevTools** → Onglet **Performance**

2. **Enregistrer** :
   - Cliquer sur le bouton d'enregistrement (cercle)
   - Recharger la page (F5)
   - Attendre le chargement complet
   - Arrêter l'enregistrement

3. **Analyser** :
   - **Network** : Vérifier les temps de chargement
   - **Main** : Vérifier le JavaScript
   - **Rendering** : Vérifier le rendu
   - **Memory** : Vérifier l'utilisation mémoire

4. **Métriques importantes** :
   - Temps de chargement total
   - Temps de parsing JavaScript
   - Temps de rendu
   - Utilisation CPU/GPU

---

### 5. Test du Service Worker

1. **Ouvrir DevTools** → Onglet **Application**

2. **Service Workers** :
   - Vérifier que le service worker est **actif**
   - Vérifier qu'il n'y a pas d'erreurs

3. **Cache Storage** :
   - Vérifier les caches créés :
     - `workbox-precache-v2-...`
     - `google-fonts-cache`
     - `images-cache`
     - `api-cache`

4. **Manifest** :
   - Vérifier que le manifest est chargé
   - Vérifier les icônes

---

### 6. Test de Lazy Loading

1. **Ouvrir DevTools** → Onglet **Network**

2. **Configurer** :
   - Filtrer par **JS**
   - Cocher **Disable cache**

3. **Tester** :
   - Recharger la page d'accueil
   - Noter les fichiers chargés
   - Naviguer vers `/univers`
   - Vérifier que de nouveaux chunks sont chargés

4. **Vérifier** :
   - Les chunks sont chargés à la demande
   - Le bundle initial est plus petit
   - Les pages suivantes chargent rapidement

---

### 7. Test Three.js Performance

1. **Ouvrir DevTools** → Onglet **Performance**

2. **Enregistrer** :
   - Démarrer l'enregistrement
   - Laisser la page ouverte 10 secondes
   - Changer d'onglet (pour tester la pause)
   - Revenir sur l'onglet
   - Arrêter l'enregistrement

3. **Vérifier** :
   - L'animation se met en pause quand l'onglet n'est pas visible
   - La consommation CPU/GPU est réduite
   - L'animation reste fluide à 60 FPS

---

## 📊 Métriques Cibles

### Performance Lighthouse

| Métrique | Objectif | Excellent |
|---------|----------|-----------|
| Performance Score | 85+ | 90+ |
| FCP | < 1.8s | < 1.0s |
| LCP | < 2.5s | < 1.5s |
| TTI | < 3.8s | < 2.5s |
| TBT | < 200ms | < 100ms |
| CLS | < 0.1 | < 0.05 |

### Bundle Size

| Type | Objectif | Excellent |
|------|----------|-----------|
| Bundle initial (JS) | < 300KB | < 200KB |
| Total JS | < 500KB | < 400KB |
| Total CSS | < 50KB | < 30KB |
| Total Images | < 500KB | < 300KB |

### Web Vitals

| Métrique | Objectif | Excellent |
|---------|----------|-----------|
| FCP | < 1.8s | < 1.0s |
| LCP | < 2.5s | < 1.5s |
| FID | < 100ms | < 50ms |
| CLS | < 0.1 | < 0.05 |
| TTFB | < 600ms | < 300ms |

---

## 🔧 Commandes Utiles

```bash
# Build de production
npm run build

# Preview du build
npm run preview

# Test de performance (script)
npm run test:performance

# Analyse du bundle
npm run analyze

# Test E2E (inclut des tests de performance)
npm run test:e2e
```

---

## 📝 Checklist de Test

- [ ] Build de production créé (`npm run build`)
- [ ] Service worker actif (DevTools → Application)
- [ ] Caches créés (Cache Storage)
- [ ] Lighthouse score > 85
- [ ] FCP < 1.8s
- [ ] LCP < 2.5s
- [ ] TTI < 3.8s
- [ ] Bundle initial < 300KB
- [ ] Lazy loading fonctionne (Network tab)
- [ ] Three.js optimisé (Performance tab)
- [ ] Pas d'erreurs dans la console
- [ ] Web Vitals dans les objectifs

---

## 🐛 Dépannage

### Service Worker ne se charge pas

1. Vérifier que le build a été fait : `npm run build`
2. Vérifier que le SW est dans `dist/sw.js`
3. Vérifier la console pour les erreurs
4. Vider le cache du navigateur

### Performance faible

1. Vérifier le throttling réseau (DevTools → Network)
2. Vérifier les ressources bloquantes
3. Vérifier la taille des images
4. Vérifier les fonts (chargement asynchrone)

### Lazy loading ne fonctionne pas

1. Vérifier que les imports utilisent `lazy()`
2. Vérifier la console pour les erreurs
3. Vérifier le Network tab (filtre JS)

---

## 🎉 Résultats Attendus

Après les optimisations, vous devriez voir :

- ✅ **Performance Score** : 85-95 (au lieu de 70-80)
- ✅ **Bundle initial** : -30 à -40% de réduction
- ✅ **Temps de chargement** : -40 à -50% de réduction
- ✅ **Service Worker** : Actif et fonctionnel
- ✅ **Lazy loading** : Chunks chargés à la demande
- ✅ **Three.js** : Animation optimisée (pause quand invisible)

---

## 📚 Ressources

- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [Web Vitals](https://web.dev/vitals/)
- [Chrome DevTools Performance](https://developer.chrome.com/docs/devtools/performance/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)

