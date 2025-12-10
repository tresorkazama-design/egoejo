# 🔧 Correction du Déploiement Vercel

## ⚠️ Problème identifié

Votre site Vercel (`https://votre-site.vercel.app/`) affiche actuellement un **menu de restaurant** (sushi, yakitori, sashimi) au lieu du site **EGOEJO**.

Cela indique que :
1. **Le mauvais dossier est déployé** sur Vercel
2. **La configuration Vercel pointe vers le mauvais répertoire**

## 🔍 Structure du projet

Votre projet a **deux dossiers frontend** :
- `frontend/` - Ancien dossier (ne pas utiliser)
- `frontend/frontend/` - **Vrai dossier React avec le code EGOEJO** ✅

## ✅ Solution : Configurer Vercel correctement

### Étape 1 : Vérifier la configuration Vercel

1. Allez sur [Vercel Dashboard](https://vercel.com/dashboard)
2. Sélectionnez votre projet (`egoejo-frontend` ou similaire)
3. Allez dans **Settings** → **General**

### Étape 2 : Configurer le Root Directory

**IMPORTANT** : Le **Root Directory** doit être configuré sur :
```
frontend/frontend
```

**PAS** sur :
- `frontend` ❌
- `.` (racine) ❌

### Étape 3 : Vérifier les autres paramètres

Assurez-vous que les paramètres suivants sont corrects :

- **Framework Preset** : `Vite`
- **Root Directory** : `frontend/frontend` ✅
- **Build Command** : `npm run build`
- **Output Directory** : `dist`
- **Install Command** : `npm install`

### Étape 4 : Redéployer

1. Cliquez sur **Redeploy** dans l'onglet **Deployments**
2. Sélectionnez le dernier commit
3. Cliquez sur **Redeploy**

### Étape 5 : Vérifier le résultat

Après le redéploiement, visitez `https://votre-site.vercel.app/` et vous devriez voir :
- ✅ Le site EGOEJO avec le logo
- ✅ La navigation (Accueil, Univers, Vision, Citations, Alliances, Projets, Communauté, Votes, Rejoindre, Admin)
- ✅ **PAS** de menu de restaurant ❌

## 🔧 Alternative : Déployer depuis le CLI

Si vous préférez utiliser le CLI Vercel :

```powershell
# Aller dans le bon dossier
cd frontend/frontend

# Lier le projet Vercel (si pas déjà fait)
npx vercel link

# Déployer en production
npx vercel --prod
```

## 📝 Notes importantes

1. **Le dossier `frontend/frontend/`** contient :
   - `src/pages/Home.jsx` - Page d'accueil EGOEJO
   - `src/pages/AdminDashboard.jsx` - Dashboard admin (nouveau)
   - `vercel.json` - Configuration Vercel
   - `package.json` - Dépendances React/Vite

2. **Le dossier `frontend/`** (racine) ne doit **PAS** être déployé car il contient des fichiers obsolètes.

3. **Vérifiez que `VITE_API_URL`** est bien configuré dans les **Environment Variables** de Vercel :
   - Production : `https://egoejo-production.up.railway.app`
   - Preview : `https://egoejo-production.up.railway.app`
   - Development : `http://localhost:8000`

## 🚨 Si le problème persiste

1. **Vérifiez le domaine** : Assurez-vous que vous visitez le bon domaine Vercel
2. **Videz le cache** : Utilisez Ctrl+Shift+R pour forcer le rechargement
3. **Vérifiez les logs** : Dans Vercel Dashboard → Deployments → Logs

---

**Une fois corrigé, votre site EGOEJO devrait s'afficher correctement !** 🎉

