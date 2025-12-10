# 🚀 Guide de Déploiement Frontend - EGOEJO

**Date** : 2025-12-03  
**Version** : 1.0.0

---

## 📋 Prérequis

- Compte Vercel (gratuit) : https://vercel.com/signup
- Compte GitHub connecté
- Repository GitHub du projet

---

## 🎯 Option 1 : Déploiement Automatique via GitHub (Recommandé)

### Étape 1 : Connecter le Repository à Vercel

1. **Aller sur Vercel** : https://vercel.com/dashboard
2. Cliquer sur **"Add New..."** → **"Project"**
3. **Importer** votre repository GitHub `egoejo`
4. Vercel détectera automatiquement le projet

### Étape 2 : Configurer le Projet

**Settings du projet** :
- **Framework Preset** : `Vite` (détecté automatiquement)
- **Root Directory** : `frontend/frontend`
- **Build Command** : `npm run build`
- **Output Directory** : `dist`
- **Install Command** : `npm ci`

### Étape 3 : Configurer les Variables d'Environnement

1. Dans les **Settings** du projet → **Environment Variables**
2. Ajouter les variables suivantes :

```bash
# API Backend (URL de votre backend Railway)
VITE_API_URL=https://egoejo-production.up.railway.app

# Monitoring (optionnel)
VITE_SENTRY_DSN=<votre DSN Sentry frontend>
```

**⚠️ Important** : Remplacer `https://egoejo-production.up.railway.app` par l'URL réelle de votre backend Railway.

### Étape 4 : Déployer

1. Cliquer sur **"Deploy"**
2. Attendre la fin du build
3. Vercel fournira une URL (ex: `egoejo.vercel.app`)

---

## 🎯 Option 2 : Déploiement Manuel via Vercel CLI

### Étape 1 : Installer Vercel CLI

```powershell
npm install -g vercel
```

### Étape 2 : Se connecter à Vercel

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
vercel login
```

Suivre les instructions pour se connecter.

### Étape 3 : Lier le Projet

```powershell
vercel link
```

Suivre les instructions :
- Sélectionner votre organisation
- Sélectionner le projet (ou créer un nouveau projet)

### Étape 4 : Configurer les Variables d'Environnement

```powershell
# Via CLI
vercel env add VITE_API_URL production
# Entrer : https://egoejo-production.up.railway.app

# OU via l'interface web
# Aller sur : https://vercel.com/[votre-org]/[votre-projet]/settings/environment-variables
```

### Étape 5 : Déployer

```powershell
# Déploiement en production
vercel --prod

# OU déploiement de preview
vercel
```

---

## 🔧 Configuration Avancée

### Fichier `vercel.json` (Optionnel)

Créer `frontend/frontend/vercel.json` :

```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "devCommand": "npm run dev",
  "installCommand": "npm ci",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "headers": [
    {
      "source": "/assets/(.*)",
      "headers": [
        {
          "key": "Cache-Control",
          "value": "public, max-age=31536000, immutable"
        }
      ]
    }
  ]
}
```

### Variables d'Environnement par Environnement

Dans Vercel, vous pouvez configurer des variables différentes pour :
- **Production** : Variables pour `vercel.app` et votre domaine personnalisé
- **Preview** : Variables pour les branches et PR
- **Development** : Variables pour `vercel dev`

**Exemple** :
- **Production** : `VITE_API_URL=https://api.egoejo.org`
- **Preview** : `VITE_API_URL=https://egoejo-production.up.railway.app`

---

## ✅ Vérification Post-Déploiement

### 1. Vérifier que le Site Fonctionne

```bash
curl https://egoejo.vercel.app
```

**Résultat attendu** : HTML de l'application React

### 2. Vérifier les Variables d'Environnement

Dans le code frontend, vérifier que `VITE_API_URL` est bien utilisé :

```javascript
// src/utils/api.js
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

### 3. Tester la Connexion Backend

1. Ouvrir : https://egoejo.vercel.app
2. Ouvrir la console du navigateur (F12)
3. Vérifier qu'il n'y a pas d'erreur CORS
4. Tester une requête API (ex: login)

---

## 🔒 Sécurité

### CORS Configuration

Assurez-vous que le backend Railway autorise les requêtes depuis Vercel :

**Dans Railway (backend)** → Variables :
```bash
CORS_ALLOWED_ORIGINS=https://egoejo.vercel.app,https://www.egoejo.org
CSRF_TRUSTED_ORIGINS=https://egoejo.vercel.app,https://www.egoejo.org
```

### Headers de Sécurité

Vercel ajoute automatiquement :
- HTTPS forcé
- Headers de sécurité (HSTS, etc.)

---

## 🚀 Déploiement Automatique via GitHub Actions

Si vous avez configuré GitHub Actions (voir `.github/workflows/cd.yml`), le déploiement se fait automatiquement :

1. **Push sur `main`** :
```powershell
cd C:\Users\treso\Downloads\egoejo
git add .
git commit -m "feat: mise à jour frontend"
git push origin main
```

2. **GitHub Actions** :
   - Exécute les tests
   - Build le frontend
   - Déploie sur Vercel

3. **Vérification** :
   - Aller sur : https://github.com/tresorkazama-design/egoejo/actions
   - Vérifier que le workflow `CD` a réussi

---

## 📋 Checklist

### Configuration Vercel
- [ ] Repository GitHub connecté
- [ ] Framework détecté (Vite)
- [ ] Root Directory : `frontend/frontend`
- [ ] Build Command : `npm run build`
- [ ] Output Directory : `dist`

### Variables d'Environnement
- [ ] `VITE_API_URL` configuré (URL backend Railway)
- [ ] `VITE_SENTRY_DSN` configuré (optionnel)

### Déploiement
- [ ] Premier déploiement réussi
- [ ] URL Vercel accessible
- [ ] Site fonctionne correctement
- [ ] Connexion backend fonctionne

### CORS
- [ ] Backend autorise les requêtes depuis Vercel
- [ ] Pas d'erreur CORS dans la console

---

## 🐛 Troubleshooting

### Erreur : Build Failed

**Cause** : Erreur lors du build

**Solution** :
1. Vérifier les logs de build dans Vercel
2. Tester localement : `npm run build`
3. Vérifier que toutes les dépendances sont dans `package.json`

### Erreur : Variables d'Environnement Non Disponibles

**Cause** : Variables non configurées ou mal nommées

**Solution** :
1. Vérifier que les variables commencent par `VITE_`
2. Redéployer après avoir ajouté les variables
3. Vérifier l'environnement (Production/Preview/Development)

### Erreur : CORS

**Cause** : Backend n'autorise pas les requêtes depuis Vercel

**Solution** :
1. Ajouter l'URL Vercel dans `CORS_ALLOWED_ORIGINS` (Railway)
2. Redéployer le backend
3. Vérifier que `VITE_API_URL` est correct

---

## 📚 Documentation

- `GUIDE_PRODUCTION.md` - Guide complet de production
- `VARIABLES_PRODUCTION.md` - Variables d'environnement
- `GUIDE_DEPLOIEMENT.md` - Guide de déploiement général

---

## 🎉 Félicitations !

**Votre frontend est maintenant déployé sur Vercel !** ✅

**URL** : https://egoejo.vercel.app (ou votre domaine personnalisé)

---

**Prêt pour la production !** 🚀

