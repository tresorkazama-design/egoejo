# 🔧 Configurer VITE_API_URL - Frontend EGOEJO

**Status** : ✅ Projet lié à Vercel, mais `VITE_API_URL` manque

---

## ✅ Étape 1 : Ajouter dans `.env.local` (Développement Local)

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Ajouter VITE_API_URL dans .env.local
Add-Content .env.local "`nVITE_API_URL=https://egoejo-production.up.railway.app"
```

**OU** éditer manuellement `.env.local` et ajouter :

```bash
# API Backend (URL de votre backend Railway)
VITE_API_URL=https://egoejo-production.up.railway.app
```

**⚠️ Important** : Remplacer `https://egoejo-production.up.railway.app` par l'URL réelle de votre backend Railway.

---

## ✅ Étape 2 : Configurer dans Vercel (Production)

### Option A : Via l'Interface Web (Recommandé)

1. **Aller sur** : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/environment-variables
2. **Cliquer sur** "Add New"
3. **Remplir** :
   - **Key** : `VITE_API_URL`
   - **Value** : `https://egoejo-production.up.railway.app`
   - **Environments** : ✅ Production, ✅ Preview, ✅ Development
4. **Cliquer sur** "Save"

### Option B : Via CLI

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Pour la production
vercel env add VITE_API_URL production
# Entrer : https://egoejo-production.up.railway.app

# Pour preview (branches)
vercel env add VITE_API_URL preview
# Entrer : https://egoejo-production.up.railway.app

# Pour development
vercel env add VITE_API_URL development
# Entrer : http://localhost:8000/api
```

---

## ✅ Étape 3 : Vérifier la Configuration

### Vérifier le Code

Le code utilise bien `VITE_API_URL` :

**Fichier** : `frontend/frontend/src/utils/api.js`
```javascript
export const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : 'http://localhost:8000/api';
```

✅ **C'est correct !**

### Vérifier `.env.local`

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
Get-Content .env.local
```

**Devrait contenir** :
```bash
VERCEL_OIDC_TOKEN=...
VITE_API_URL=https://egoejo-production.up.railway.app
```

### Vérifier dans Vercel

1. Aller sur : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/environment-variables
2. Vérifier que `VITE_API_URL` est listé
3. Vérifier les environnements (Production/Preview/Development)

---

## 🚀 Étape 4 : Déployer

### Option A : Déploiement en Production

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
vercel --prod
```

### Option B : Déploiement Preview (Test)

```powershell
vercel
```

### Option C : Via GitHub (Automatique)

```powershell
cd C:\Users\treso\Downloads\egoejo
git add .
git commit -m "feat: configuration VITE_API_URL"
git push origin main
```

---

## ✅ Vérification Post-Déploiement

### 1. Tester le Site

```bash
# Tester le site (remplacer par votre URL Vercel)
curl https://frontend-*.vercel.app
```

### 2. Vérifier la Console du Navigateur

1. Ouvrir le site dans le navigateur
2. Ouvrir la console (F12)
3. Vérifier qu'il n'y a pas d'erreur
4. Vérifier que les requêtes API utilisent la bonne URL

### 3. Tester une Requête API

1. Ouvrir le site
2. Tester une fonctionnalité (ex: login)
3. Vérifier dans la console que la requête va vers :
   - `https://egoejo-production.up.railway.app/api/...`

---

## 🔒 Étape 5 : Configurer CORS dans le Backend

Assurez-vous que le backend Railway autorise les requêtes depuis Vercel :

**Dans Railway (backend)** → Variables :
```bash
CORS_ALLOWED_ORIGINS=https://frontend-*.vercel.app,https://egoejo.vercel.app
CSRF_TRUSTED_ORIGINS=https://frontend-*.vercel.app,https://egoejo.vercel.app
```

**Format Railway** : Utiliser `${{Variable}}` pour référencer d'autres services.

---

## 📋 Checklist

- [ ] `VITE_API_URL` ajouté dans `.env.local`
- [ ] `VITE_API_URL` configuré dans Vercel (Production)
- [ ] `VITE_API_URL` configuré dans Vercel (Preview)
- [ ] `VITE_API_URL` configuré dans Vercel (Development)
- [ ] Déploiement réussi
- [ ] Site accessible
- [ ] Connexion backend fonctionne
- [ ] CORS configuré dans le backend

---

## 🐛 Troubleshooting

### Erreur : Variable non définie

**Cause** : `VITE_API_URL` non configuré

**Solution** :
1. Vérifier que la variable est dans `.env.local` (dev local)
2. Vérifier que la variable est dans Vercel (production)
3. Redéployer après avoir ajouté la variable

### Erreur : CORS

**Cause** : Backend n'autorise pas Vercel

**Solution** :
1. Ajouter l'URL Vercel dans `CORS_ALLOWED_ORIGINS` (Railway)
2. Redéployer le backend

---

## 📚 Documentation

- `SUITE_DEPLOIEMENT_FRONTEND.md` - Guide complet de la suite
- `GUIDE_DEPLOIEMENT_FRONTEND.md` - Guide complet de déploiement
- `GUIDE_RAPIDE_FRONTEND.md` - Version rapide

---

**Une fois `VITE_API_URL` configuré, vous pouvez déployer !** ✅

