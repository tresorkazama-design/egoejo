# 📝 Instructions : Commiter les changements Frontend

## ⚠️ Note importante

Le dossier `frontend` est un **sous-module Git**, vous devez donc commiter les changements dans le dossier `frontend/frontend/`.

## 🚀 Étapes pour commiter les changements

### 1. Aller dans le dossier frontend/frontend

```powershell
cd frontend/frontend
```

### 2. Vérifier les changements

```powershell
git status
```

Vous devriez voir :
- `src/pages/AdminDashboard.jsx` (nouveau fichier)
- `src/app/router.jsx` (modifié)
- `src/shared/components/Layout.jsx` (modifié)

### 3. Ajouter les fichiers

```powershell
git add src/pages/AdminDashboard.jsx src/app/router.jsx src/shared/components/Layout.jsx
```

### 4. Commiter

```powershell
git commit -m "feat: ajouter dashboard admin unifié avec intégration Django Admin"
```

### 5. Pousser

```powershell
git push origin main
```

### 6. Revenir à la racine

```powershell
cd ../..
```

---

## ✅ Fichiers créés/modifiés

### Nouveau fichier :
- `frontend/frontend/src/pages/AdminDashboard.jsx` - Dashboard admin unifié

### Fichiers modifiés :
- `frontend/frontend/src/app/router.jsx` - Ajout de la route `/admin` vers AdminDashboard
- `frontend/frontend/src/shared/components/Layout.jsx` - Mise à jour du lien Admin dans la navigation

---

## 🎯 Après le commit

Le Dashboard Admin sera accessible sur :
- `https://votre-site.vercel.app/admin` (dashboard principal)
- `https://votre-site.vercel.app/admin/intents` (page intentions)
- `https://votre-site.vercel.app/admin/moderation` (page modération)

Et Django Admin sera accessible via :
- Iframe dans le dashboard (optionnel)
- Lien pour ouvrir dans un nouvel onglet
- URL directe : `https://egoejo-production.up.railway.app/admin/`

