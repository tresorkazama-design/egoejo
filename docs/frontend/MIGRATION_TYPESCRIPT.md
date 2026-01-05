# Migration TypeScript Progressive - Frontend EGOEJO

## 📋 Vue d'ensemble

Ce document décrit le plan de migration progressive du frontend EGOEJO de JavaScript vers TypeScript.

### Objectif

Migrer progressivement le frontend vers TypeScript pour :
- ✅ **Sécurité de type** : Détecter les erreurs à la compilation
- ✅ **Meilleure DX** : Autocomplétion et IntelliSense améliorés
- ✅ **Maintenabilité** : Documentation implicite via les types
- ✅ **Refactoring sécurisé** : Changements de code plus sûrs

### Principe

**Migration progressive, pas de big bang** :
- Phase 1 : Types globaux et configuration
- Phase 2 : Composants critiques (Three.js, WebSockets, animations)
- Phase 3 : Composants UI de base
- Phase 4 : Pages et routes
- Phase 5 : Hooks et utilitaires

---

## 🔍 Analyse des Composants à Risque Élevé

### Composants Three.js (Risque : ÉLEVÉ)

**Raison** : Gestion manuelle de la mémoire, types complexes, WebGL

| Composant | Fichier | Complexité | Priorité |
|-----------|---------|------------|----------|
| `HeroSorgho` | `components/HeroSorgho.jsx` | ⭐⭐⭐⭐⭐ | **P0** |
| `MyceliumVisualization` | `components/MyceliumVisualization.jsx` | ⭐⭐⭐⭐⭐ | **P0** |
| `MenuCube3D` | `components/MenuCube3D.jsx` | ⭐⭐⭐⭐ | **P1** |
| `Logo3D` | `components/Logo3D.jsx` | ⭐⭐⭐ | **P2** |

**Risques identifiés** :
- Fuites mémoire (géométries, matériaux, textures non disposées)
- Erreurs de type sur objets Three.js (Vector3, Matrix4, etc.)
- Gestion du contexte WebGL non typée

### Composants WebSocket (Risque : ÉLEVÉ)

**Raison** : Gestion d'état asynchrone, types de messages non typés

| Composant | Fichier | Complexité | Priorité |
|-----------|---------|------------|----------|
| `ChatWindow` | `components/ChatWindow.jsx` | ⭐⭐⭐⭐ | **P0** |
| `useWebSocket` | `hooks/useWebSocket.js` | ⭐⭐⭐⭐ | **P0** |
| `ChatList` | `components/ChatList.jsx` | ⭐⭐⭐ | **P1** |

**Risques identifiés** :
- Types de messages WebSocket non typés
- Gestion d'erreurs de connexion non typée
- État de reconnexion non typé

### Composants Animations (Risque : MOYEN)

**Raison** : Configuration d'animations complexes, props non typées

| Composant | Fichier | Complexité | Priorité |
|-----------|---------|------------|----------|
| `PageTransition` | `components/PageTransition.jsx` | ⭐⭐⭐ | **P1** |
| `CustomCursor` | `components/CustomCursor.jsx` | ⭐⭐⭐ | **P1** |
| `SwipeButton` | `components/ui/SwipeButton.jsx` | ⭐⭐⭐ | **P1** |

**Risques identifiés** :
- Configuration GSAP/Framer Motion non typée
- Props d'animation non typées
- Callbacks d'animation non typés

---

## 📅 Plan de Migration par Phases

### Phase 1 : Types Globaux et Configuration ✅

**Objectif** : Mettre en place l'infrastructure TypeScript

**Actions** :
1. ✅ Créer `tsconfig.strict.json` avec configuration progressive
2. ✅ Créer `src/types/common.d.ts` avec types minimaux
3. ✅ Configurer Vite pour supporter TypeScript
4. ✅ Ajouter les types pour les dépendances (React, Three.js, etc.)

**Fichiers créés** :
- `tsconfig.strict.json`
- `src/types/common.d.ts`

**Durée estimée** : 1-2 jours

---

### Phase 2 : Composants Critiques (Three.js, WebSockets)

**Objectif** : Migrer les composants à risque élevé

#### 2.1 Composants Three.js

**Ordre de migration** :
1. `HeroSorgho.jsx` → `HeroSorgho.tsx`
2. `MyceliumVisualization.jsx` → `MyceliumVisualization.tsx`
3. `MenuCube3D.jsx` → `MenuCube3D.tsx`
4. `Logo3D.jsx` → `Logo3D.tsx`

**Types nécessaires** :
```typescript
// src/types/three.d.ts
import * as THREE from 'three';

export interface ThreeJSComponentProps {
  threeConfig?: ThreeJSConfig;
  onLoad?: () => void;
  onError?: (error: Error) => void;
}

export interface ThreeJSConfig {
  enable: boolean;
  quality?: 'low' | 'medium' | 'high';
  maxFPS?: number;
  enableShadows?: boolean;
}
```

**Durée estimée** : 3-5 jours par composant

#### 2.2 Composants WebSocket

**Ordre de migration** :
1. `useWebSocket.js` → `useWebSocket.ts`
2. `ChatWindow.jsx` → `ChatWindow.tsx`
3. `ChatList.jsx` → `ChatList.tsx`

**Types nécessaires** :
```typescript
// src/types/websocket.d.ts
export interface WebSocketMessage<T = unknown> {
  type: string;
  data: T;
  timestamp?: string;
}

export interface WebSocketState {
  connected: boolean;
  connecting: boolean;
  error: string | null;
  reconnectAttempts: number;
}
```

**Durée estimée** : 2-3 jours par composant

---

### Phase 3 : Composants UI de Base

**Objectif** : Migrer les composants UI réutilisables

**Ordre de migration** :
1. ✅ `Button.jsx` → `Button.tsx` (EXEMPLE)
2. `Input.jsx` → `Input.tsx`
3. `Loader.jsx` → `Loader.tsx`
4. `Notification.jsx` → `Notification.tsx`
5. `ErrorBoundary.jsx` → `ErrorBoundary.tsx`

**Durée estimée** : 1 jour par composant

---

### Phase 4 : Pages et Routes

**Objectif** : Migrer les pages principales

**Ordre de migration** :
1. Pages simples (NotFound, Login, Register)
2. Pages avec logique métier (Home, Projets, Contenus)
3. Pages complexes (Dashboard, Admin, Chat)

**Durée estimée** : 2-3 jours par page

---

### Phase 5 : Hooks et Utilitaires

**Objectif** : Migrer les hooks et utilitaires

**Ordre de migration** :
1. Hooks simples (useToggle, useDebounce, useLocalStorage)
2. Hooks avec API (useFetch, useSaka, useGlobalAssets)
3. Utilitaires (api.js, format.js, validation.js)

**Durée estimée** : 1-2 jours par hook/utilitaire

---

## 🛠️ Configuration TypeScript

### tsconfig.strict.json

Configuration stricte pour migration progressive :

```json
{
  "extends": "./tsconfig.json",
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "allowJs": true, // Permet de migrer progressivement
    "checkJs": false, // Désactivé pour éviter les erreurs sur fichiers JS existants
    "noEmit": true // Vite gère la compilation
  }
}
```

### Types Minimaux

Fichier `src/types/common.d.ts` contient :
- Types de base (ButtonProps, APIResponse, etc.)
- Types pour composants critiques (ThreeJS, WebSocket, Animations)
- Types pour contextes (Auth, Language, Notification, EcoMode)
- Types pour entités (User, Project, Content, ChatMessage)

---

## 📝 Exemple de Migration : Button.jsx → Button.tsx

### Avant (Button.jsx)

```jsx
export const Button = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  type = 'button',
  className = '',
  ...props
}) => {
  // ...
};
```

### Après (Button.tsx)

```tsx
import type { ButtonProps } from '../types/common';

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  disabled = false,
  variant = 'primary',
  type = 'button',
  className = '',
  ...props
}) => {
  // ...
};
```

**Changements** :
- ✅ Import du type `ButtonProps`
- ✅ Typage explicite avec `React.FC<ButtonProps>`
- ✅ Aucun changement fonctionnel

---

## 🎯 Périmètre de Migration

### Inclus dans la Migration

✅ **Composants React** : `.jsx` → `.tsx`
✅ **Hooks personnalisés** : `.js` → `.ts`
✅ **Utilitaires** : `.js` → `.ts`
✅ **Types** : `.d.ts`

### Exclus de la Migration (pour l'instant)

❌ **Tests** : Restent en `.test.js` / `.test.jsx`
❌ **Configurations** : `vite.config.js`, `playwright.config.js`
❌ **Scripts** : Scripts de build et CI/CD

### Règles de Migration

1. **Un fichier à la fois** : Migrer progressivement, tester après chaque migration
2. **Aucun changement fonctionnel** : Seulement ajouter les types
3. **Tests inchangés** : Les tests existants doivent continuer à passer
4. **Compatibilité** : Les fichiers `.js` et `.ts` peuvent coexister

---

## ✅ Checklist de Migration

Pour chaque composant migré :

- [ ] Fichier renommé `.jsx` → `.tsx` ou `.js` → `.ts`
- [ ] Types importés depuis `src/types/common.d.ts`
- [ ] Props typées avec interface TypeScript
- [ ] Hooks typés (si applicable)
- [ ] Tests passent sans modification
- [ ] Aucune erreur TypeScript (`npm run type-check`)
- [ ] Build fonctionne (`npm run build`)
- [ ] Documentation mise à jour

---

## 🚀 Commandes Utiles

### Vérifier les types

```bash
npm run type-check
```

### Build avec TypeScript

```bash
npm run build
```

### Lancer les tests

```bash
npm run test
```

### Mode développement

```bash
npm run dev
```

---

## 📊 Progression

### Phase 1 : Types Globaux ✅

- [x] `tsconfig.strict.json` créé
- [x] `src/types/common.d.ts` créé
- [x] Configuration Vite vérifiée

### Phase 2 : Composants Critiques

- [ ] `HeroSorgho.jsx` → `HeroSorgho.tsx`
- [ ] `MyceliumVisualization.jsx` → `MyceliumVisualization.tsx`
- [ ] `useWebSocket.js` → `useWebSocket.ts`
- [ ] `ChatWindow.jsx` → `ChatWindow.tsx`

### Phase 3 : Composants UI de Base

- [x] `Button.jsx` → `Button.tsx` (EXEMPLE)
- [ ] `Input.jsx` → `Input.tsx`
- [ ] `Loader.jsx` → `Loader.tsx`

### Phase 4 : Pages et Routes

- [ ] Pages simples
- [ ] Pages avec logique métier
- [ ] Pages complexes

### Phase 5 : Hooks et Utilitaires

- [ ] Hooks simples
- [ ] Hooks avec API
- [ ] Utilitaires

---

## 🐛 Dépannage

### Erreur : "Cannot find module"

**Solution** : Vérifier que les types sont bien importés depuis `src/types/common.d.ts`

### Erreur : "Property does not exist on type"

**Solution** : Ajouter le type manquant dans `src/types/common.d.ts` ou créer un type spécifique

### Erreur : "Type 'X' is not assignable to type 'Y'"

**Solution** : Vérifier la compatibilité des types, utiliser `as` si nécessaire (avec précaution)

---

## 📝 Notes Importantes

1. **Migration progressive** : Ne pas tout migrer d'un coup
2. **Tests inchangés** : Les tests doivent continuer à passer
3. **Aucun changement fonctionnel** : Seulement ajouter les types
4. **Compatibilité** : Les fichiers `.js` et `.ts` peuvent coexister

---

**Fin du document**

*La migration TypeScript progressive permet d'améliorer la sécurité de type sans perturber le développement en cours.*

