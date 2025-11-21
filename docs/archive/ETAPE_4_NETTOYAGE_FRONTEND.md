# ✅ Étape 4 : Nettoyage des dépendances et fichiers inutilisés frontend

## 🔍 Problème identifié dans l'audit

D'après `npx knip`, plusieurs fichiers et dépendances ne sont plus utilisés :

**Fichiers non utilisés** :
- `src/reveal.js`
- `src/three/HeroWater.jsx`

**Dépendances non utilisées** :
- 3D / expérimental : `@react-three/drei`, `@react-three/fiber`
- observabilité / infra : `@sentry/node`, `@vercel/analytics`, `@vercel/blob`, `@vercel/speed-insights`
- backend-like : `express`, `pg`, `dotenv`, `resend`, `stripe`
- data : `@tanstack/react-query` → **FAUX POSITIF** (utilisé dans plusieurs hooks)

**DevDependencies potentiellement inutilisées** :
- `autoprefixer`, `postcss`, `tailwindcss` (pas de fichiers de config trouvés)

## ✅ Actions effectuées

### 1. Suppression des fichiers inutilisés

**Fichiers supprimés** :
- ✅ `frontend/frontend/src/reveal.js` (fonction d'animation non utilisée)
- ✅ `frontend/frontend/src/three/HeroWater.jsx` (composant Three.js non utilisé)

**Dossier supprimé** :
- ✅ `frontend/frontend/src/three/` (vide après suppression de HeroWater.jsx)

### 2. Suppression des dépendances inutilisées

**Dépendances supprimées** :

#### 3D / expérimental
- ❌ `@react-three/drei` (gardé `three` qui est utilisé dans `HeroSorgho.jsx`)
- ❌ `@react-three/fiber` (gardé `three` qui est utilisé dans `HeroSorgho.jsx`)

#### Observabilité / infra
- ❌ `@sentry/node` (gardé `@sentry/browser` et `@sentry/tracing` utilisés dans `sentry.client.js`)
- ❌ `@vercel/analytics` (pas d'import trouvé)
- ❌ `@vercel/blob` (pas d'import trouvé)
- ❌ `@vercel/speed-insights` (pas d'import trouvé)

#### Backend-like (Node.js)
- ❌ `express` (pas d'import trouvé, backend-like)
- ❌ `pg` (pas d'import trouvé, backend-like)
- ❌ `dotenv` (pas d'import trouvé)
- ❌ `resend` (pas d'import trouvé, backend-like)
- ❌ `stripe` (pas d'import trouvé, backend-like - mentionné uniquement comme texte dans Home.jsx)

**Dépendances conservées** :

✅ **`three`** → Utilisé dans `HeroSorgho.jsx` pour les animations WebGL
✅ **`@sentry/browser`** → Utilisé dans `sentry.client.js`
✅ **`@sentry/tracing`** → Utilisé dans `sentry.client.js`
✅ **`@tanstack/react-query`** → Utilisé massivement dans :
  - `features/community/hooks/useChat.js`
  - `features/polls/hooks/usePolls.js`
  - `features/moderation/hooks/useModeration.js`
  - `app/providers.jsx`

### 3. DevDependencies conservées (à vérifier plus tard)

**DevDependencies conservées** :
- ⚠️ `autoprefixer` (pourrait être utilisé implicitement par Vite/PostCSS)
- ⚠️ `postcss` (pourrait être utilisé implicitement par Vite)
- ⚠️ `tailwindcss` (pas de config trouvée, mais pourrait être utilisé)

**Note** : Ces devDependencies pourraient être utilisées implicitement par Vite ou d'autres outils de build. Si vous n'utilisez pas Tailwind CSS, vous pouvez les retirer plus tard après avoir vérifié que le build fonctionne toujours.

### 4. Vérification post-nettoyage

✅ **Build fonctionne** : `npm run build` réussit sans erreur
✅ **Tests passent** : `npm run test` réussit (5/5 tests passent)
✅ **Aucune régression** : Le code fonctionne toujours correctement

## 📊 Résumé des changements

### Avant
```json
"dependencies": {
  "@gsap/react": "^2.1.2",
  "@react-three/drei": "^10.7.6",        // ❌ Supprimé
  "@react-three/fiber": "^9.4.0",        // ❌ Supprimé
  "@sentry/browser": "^10.23.0",
  "@sentry/node": "^10.23.0",            // ❌ Supprimé
  "@sentry/tracing": "^7.120.4",
  "@tanstack/react-query": "^5.90.7",
  "@vercel/analytics": "^1.5.0",         // ❌ Supprimé
  "@vercel/blob": "^2.0.0",              // ❌ Supprimé
  "@vercel/speed-insights": "^1.2.0",    // ❌ Supprimé
  "dotenv": "^17.2.3",                   // ❌ Supprimé
  "express": "^5.1.0",                   // ❌ Supprimé
  "gsap": "^3.13.0",
  "pg": "^8.16.3",                       // ❌ Supprimé
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "react-router-dom": "^7.9.4",
  "resend": "^6.4.1",                    // ❌ Supprimé
  "stripe": "^19.3.0",                   // ❌ Supprimé
  "three": "^0.180.0"
}
```

### Après
```json
"dependencies": {
  "@gsap/react": "^2.1.2",
  "@sentry/browser": "^10.23.0",
  "@sentry/tracing": "^7.120.4",
  "@tanstack/react-query": "^5.90.7",
  "gsap": "^3.13.0",
  "react": "^19.2.0",
  "react-dom": "^19.2.0",
  "react-router-dom": "^7.9.4",
  "three": "^0.180.0"
}
```

### Impact

**Dépendances supprimées** : 11
- `@react-three/drei`
- `@react-three/fiber`
- `@sentry/node`
- `@vercel/analytics`
- `@vercel/blob`
- `@vercel/speed-insights`
- `dotenv`
- `express`
- `pg`
- `resend`
- `stripe`

**Fichiers supprimés** : 2
- `src/reveal.js`
- `src/three/HeroWater.jsx`

**Réduction estimée** :
- ✅ **Taille du repo** : Réduite (moins de fichiers et de dépendances)
- ✅ **Taille du build** : Réduite (moins de dépendances à bundle)
- ✅ **Temps d'installation** : Réduit (moins de packages npm à installer)
- ✅ **Maintenance** : Simplifiée (moins de dépendances à maintenir)

## 🎯 Résultat

- ✅ **11 dépendances supprimées** (backend-like et inutilisées)
- ✅ **2 fichiers supprimés** (reveal.js et HeroWater.jsx)
- ✅ **Build fonctionne toujours** (vérifié avec `npm run build`)
- ✅ **Tests passent toujours** (5/5 tests réussis)
- ✅ **Aucune régression** (code fonctionnel après nettoyage)

## 🚀 Prochaine étape

L'**Étape 5** consiste à corriger les vulnérabilités npm et Bandit (npm audit fix, bandit sur core/config uniquement).

---

## 📝 Notes supplémentaires

### Dépendances conservées (à vérifier plus tard)

Si vous ne prévoyez pas d'utiliser Tailwind CSS, vous pouvez éventuellement retirer :
- `autoprefixer`
- `postcss`
- `tailwindcss`

**Comment vérifier** :
1. Retirer ces dépendances du `package.json`
2. Lancer `npm install`
3. Lancer `npm run build`
4. Si le build fonctionne, vous pouvez les retirer définitivement

### Dépendances gardées mais notées

- ✅ **`three`** : Utilisé dans `HeroSorgho.jsx` pour les animations WebGL
- ✅ **`@sentry/browser`** et **`@sentry/tracing`** : Utilisés dans `sentry.client.js`
- ✅ **`@tanstack/react-query`** : Utilisé massivement dans les hooks de features

