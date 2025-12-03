# 🔍 Où Trouver les Vraies Valeurs des Secrets

**Date** : 2025-01-27  
**Version** : 1.0.0

---

## 📋 Vercel

### 1. VERCEL_TOKEN

**Étapes** :
1. Aller sur : **https://vercel.com/account/tokens**
2. Cliquer sur **"Create Token"**
3. Donner un nom au token (ex: `egoejo-deployment`)
4. Cliquer sur **"Create"**
5. **Copier le token** (il ne sera affiché qu'une seule fois !)

**⚠️ Important** : Le token ressemble à : `vercel_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### 2. VERCEL_ORG_ID

**Méthode 1 : Via l'interface Vercel**
1. Aller sur : **https://vercel.com/[votre-org]/settings**
   - Remplacez `[votre-org]` par le nom de votre organisation
2. L'**Org ID** est visible dans l'URL ou dans les paramètres
3. Format : `team_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Méthode 2 : Via Vercel CLI**
```powershell
# Installer Vercel CLI si nécessaire
npm install -g vercel

# Se connecter
vercel login

# Lister les projets (affiche l'Org ID)
vercel projects list
```

**Méthode 3 : Via l'API Vercel**
1. Aller sur : **https://vercel.com/account/tokens**
2. Créer un token (voir VERCEL_TOKEN ci-dessus)
3. Utiliser l'API :
```powershell
# Remplacer YOUR_TOKEN par votre token
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.vercel.com/v2/teams
```

---

### 3. VERCEL_PROJECT_ID

**Méthode 1 : Via l'interface Vercel**
1. Aller sur : **https://vercel.com/[votre-org]/[votre-projet]**
   - Remplacez `[votre-org]` et `[votre-projet]` par vos valeurs
2. Cliquer sur **"Settings"**
3. L'**Project ID** est visible dans les paramètres du projet
4. Format : `prj_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Méthode 2 : Via Vercel CLI**
```powershell
# Se placer dans le dossier frontend
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Lier le projet (si pas déjà fait)
vercel link

# OU lister les projets
vercel projects list
```

**Méthode 3 : Créer un nouveau projet**
Si vous n'avez pas encore de projet :
```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
vercel
```
Suivez les instructions pour créer et lier le projet.

---

## 🚂 Railway

### 4. RAILWAY_TOKEN

**Étapes** :
1. Aller sur : **https://railway.app/account/tokens**
2. Cliquer sur **"New Token"**
3. Donner un nom au token (ex: `egoejo-deployment`)
4. Cliquer sur **"Create Token"**
5. **Copier le token** (il ne sera affiché qu'une seule fois !)

**⚠️ Important** : Le token ressemble à : `railway_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### 5. RAILWAY_SERVICE_ID

**Méthode 1 : Via l'interface Railway**
1. Aller sur : **https://railway.app/dashboard**
2. Sélectionner votre **projet** (ou créer un nouveau projet)
3. Sélectionner le **service backend** (ou créer un nouveau service)
4. Cliquer sur **"Settings"** (icône engrenage)
5. Dans **"General"**, l'**Service ID** est visible
6. Format : `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (UUID)

**Méthode 2 : Via Railway CLI**
```powershell
# Installer Railway CLI si nécessaire
npm install -g @railway/cli

# Se connecter
railway login

# Lister les services
railway service list
```

**Méthode 3 : Créer un nouveau service**
Si vous n'avez pas encore de service :
1. Aller sur : **https://railway.app/dashboard**
2. Cliquer sur **"New Project"**
3. Choisir **"Deploy from GitHub repo"** ou **"Empty Project"**
4. Ajouter un service (ex: **"New Service"** → **"GitHub Repo"**)
5. Sélectionner votre repo `egoejo`
6. Le Service ID sera visible dans les paramètres

---

## 🔐 Django Secret Key

### 6. DJANGO_SECRET_KEY

**✅ Déjà configuré !**

Vous avez déjà généré et configuré une vraie valeur :
```
XDPKsBrCrXD24_sGIli9_BeCG0HSXhiBVx6F8vbAERcFpd-qYGEWsXGk-BrOLAge8JM
```

**Si vous voulez en générer un nouveau** :
```powershell
cd C:\Users\treso\Downloads\egoejo
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

---

## 📝 Checklist

### Vercel
- [ ] **VERCEL_TOKEN** : https://vercel.com/account/tokens
- [ ] **VERCEL_ORG_ID** : https://vercel.com/[votre-org]/settings
- [ ] **VERCEL_PROJECT_ID** : https://vercel.com/[votre-org]/[votre-projet]/settings

### Railway
- [ ] **RAILWAY_TOKEN** : https://railway.app/account/tokens
- [ ] **RAILWAY_SERVICE_ID** : https://railway.app/dashboard → Projet → Service → Settings

### Django
- [x] **DJANGO_SECRET_KEY** : ✅ Déjà configuré

---

## 🚀 Après avoir trouvé les valeurs

### Configurer les secrets

```powershell
cd C:\Users\treso\Downloads\egoejo

# Vercel
gh secret set VERCEL_TOKEN --body "VOTRE-VRAI-TOKEN-VERCEL"
gh secret set VERCEL_ORG_ID --body "VOTRE-VRAI-ORG-ID"
gh secret set VERCEL_PROJECT_ID --body "VOTRE-VRAI-PROJECT-ID"

# Railway
gh secret set RAILWAY_TOKEN --body "VOTRE-VRAI-TOKEN-RAILWAY"
gh secret set RAILWAY_SERVICE_ID --body "VOTRE-VRAI-SERVICE-ID"
```

### Vérifier

```powershell
gh secret list
```

---

## 💡 Conseils

### Si vous n'avez pas encore de compte Vercel
1. Aller sur : **https://vercel.com/signup**
2. Créer un compte (gratuit)
3. Connecter votre compte GitHub
4. Suivre les étapes ci-dessus pour obtenir les valeurs

### Si vous n'avez pas encore de compte Railway
1. Aller sur : **https://railway.app/signup**
2. Créer un compte (gratuit avec $5 de crédit)
3. Connecter votre compte GitHub
4. Suivre les étapes ci-dessus pour obtenir les valeurs

### Si vous n'avez pas encore de projet
- **Vercel** : Créer un projet vide ou connecter votre repo GitHub
- **Railway** : Créer un nouveau projet et ajouter un service

---

## 📚 Documentation

- `SECRETS_CONFIGURES.md` - Résumé des secrets configurés
- `VARIABLES_PRODUCTION.md` - Variables d'environnement
- `GUIDE_PRODUCTION.md` - Guide complet de production

---

**Toutes les instructions sont ici !** ✅

