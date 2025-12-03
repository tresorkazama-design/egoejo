# ⚡ Guide Rapide - Déploiement Frontend

**Version rapide** pour déployer le frontend sur Vercel.

---

## 🚀 Déploiement Automatique (Recommandé)

### 1. Connecter GitHub à Vercel

1. Aller sur : **https://vercel.com/dashboard**
2. **Add New...** → **Project**
3. **Import** repository `egoejo`
4. Configurer :
   - **Root Directory** : `frontend/frontend`
   - **Build Command** : `npm run build`
   - **Output Directory** : `dist`

### 2. Configurer les Variables

**Settings** → **Environment Variables** :

```bash
VITE_API_URL=https://egoejo-production.up.railway.app
```

⚠️ Remplacer par l'URL réelle de votre backend Railway.

### 3. Déployer

Cliquer sur **"Deploy"** → Attendre → ✅

---

## 🔧 Déploiement Manuel (CLI)

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Installer Vercel CLI
npm install -g vercel

# Se connecter
vercel login

# Lier le projet
vercel link

# Configurer les variables
vercel env add VITE_API_URL production
# Entrer : https://egoejo-production.up.railway.app

# Déployer
vercel --prod
```

---

## ✅ Vérification

```bash
# Tester le site
curl https://egoejo.vercel.app

# Vérifier la console du navigateur (F12)
# Pas d'erreur CORS
```

---

## 📋 Checklist

- [ ] Repository connecté à Vercel
- [ ] Root Directory : `frontend/frontend`
- [ ] `VITE_API_URL` configuré
- [ ] Déploiement réussi
- [ ] Site accessible
- [ ] CORS configuré (backend)

---

**Guide détaillé** : `GUIDE_DEPLOIEMENT_FRONTEND.md`

