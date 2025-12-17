# 🔧 Fix: `process is not defined` - Problème Résolu

**Date** : 2025-01-27  
**Erreur** : `ReferenceError: process is not defined`

---

## 🐛 Problème

Avec Vite, `process.env` n'est pas disponible dans le navigateur. Il faut utiliser `import.meta.env` à la place.

**Erreur** :
```
ReferenceError: process is not defined
at getWebSocketUrl (ChatWindow.jsx:26:21)
```

---

## ✅ Corrections Appliquées

### 1. ChatWindow.jsx

**Avant** :
```javascript
const apiBase = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000/api';
```

**Après** :
```javascript
const apiBase = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : 'http://127.0.0.1:8000/api';
```

---

### 2. Admin.jsx

**Avant** :
```javascript
process.env.REACT_APP_API_URL
process.env.REACT_APP_ADMIN_TOKEN
```

**Après** :
```javascript
import.meta.env.VITE_API_URL
import.meta.env.VITE_ADMIN_TOKEN
```

---

### 3. performance.js

**Avant** :
```javascript
if (process.env.NODE_ENV === 'development' && 'performance' in window) {
```

**Après** :
```javascript
if (import.meta.env.DEV && 'performance' in window) {
```

---

## 📝 Variables d'Environnement Vite

### Convention de Nommage

- **Vite** : `VITE_*` (ex: `VITE_API_URL`)
- **React (ancien)** : `REACT_APP_*` (ne fonctionne pas avec Vite)

### Variables Disponibles

- `import.meta.env.MODE` : Mode actuel (`development` ou `production`)
- `import.meta.env.DEV` : `true` en développement
- `import.meta.env.PROD` : `true` en production
- `import.meta.env.VITE_*` : Variables personnalisées

### Exemple de `.env`

```env
# .env.local (pour le développement)
VITE_API_URL=http://127.0.0.1:8000
VITE_ADMIN_TOKEN=your-admin-token-here
```

---

## 🧪 Tests à Effectuer

### 1. ChatWindow

1. Recharger la page `/chat`
2. Vérifier que l'erreur `process is not defined` ne s'affiche plus
3. Vérifier que le WebSocket se connecte correctement

### 2. Admin

1. Accéder à `/admin`
2. Vérifier que les fonctionnalités fonctionnent
3. Tester l'export CSV

### 3. Performance

1. Vérifier que les mesures de performance fonctionnent en développement

---

## 📚 Documentation

- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Import Meta](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/import.meta)

---

## ✅ Checklist

- [x] ChatWindow.jsx - `process.env` remplacé
- [x] Admin.jsx - `process.env` remplacé
- [x] performance.js - `process.env.NODE_ENV` remplacé
- [ ] Tester ChatWindow (à faire)
- [ ] Tester Admin (à faire)

---

## 💡 Notes

- Les tests peuvent toujours utiliser `process.env` car ils s'exécutent dans Node.js
- Tous les fichiers source doivent utiliser `import.meta.env`
- Les variables doivent être préfixées par `VITE_` pour être exposées au client

