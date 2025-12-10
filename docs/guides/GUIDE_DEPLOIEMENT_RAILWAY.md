# 🚀 Guide de déploiement du backend sur Railway

## 📋 Prérequis
- ✅ Compte GitHub (déjà connecté)
- ✅ Compte Railway : https://railway.app (inscription gratuite)
- ✅ Backend configuré et prêt (Dockerfile, requirements.txt, etc.)

---

## 🎯 Étape 1 : Créer un compte Railway (si pas déjà fait)

1. Allez sur https://railway.app
2. Cliquez sur "Login" puis "Sign Up with GitHub"
3. Autorisez Railway à accéder à votre compte GitHub

---

## 📦 Étape 2 : Créer un nouveau projet Railway

1. **Dans Railway**, cliquez sur **"New Project"**
2. Sélectionnez **"Deploy from GitHub repo"**
3. **Autorisez Railway** à accéder à votre repository GitHub (si demandé)
4. **Choisissez votre repository** `egoejo`
5. Railway va détecter automatiquement le Dockerfile

⚠️ **Important** : Railway peut ne pas détecter automatiquement le Dockerfile dans `backend/`. Vous devrez peut-être configurer le "Root Directory" plus tard.

---

## 🗄️ Étape 3 : Ajouter PostgreSQL (base de données)

1. Dans votre projet Railway, cliquez sur **"+ New"**
2. Sélectionnez **"Database"** → **"Add PostgreSQL"**
3. Railway crée automatiquement une base PostgreSQL
4. **Notez les variables d'environnement créées** :
   - `DATABASE_URL` (ex: `postgresql://postgres:password@host:port/railway`)
   - `PGHOST`
   - `PGPORT`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGDATABASE`

✅ Ces variables seront automatiquement disponibles pour tous les services du projet.

---

## 🔴 Étape 4 : Ajouter Redis (cache/WebSockets)

1. Cliquez sur **"+ New"**
2. Sélectionnez **"Database"** → **"Add Redis"**
3. Railway crée automatiquement un service Redis
4. **Notez la variable `REDIS_URL`** créée (ex: `redis://default:password@host:port`)

✅ Cette variable sera automatiquement disponible pour tous les services.

---

## ⚙️ Étape 5 : Configurer le service Web

### 5.1 Configurer le Root Directory

1. Cliquez sur votre service **"web"** (ou le service principal)
2. Allez dans **"Settings"** → **"Source"**
3. Définissez **"Root Directory"** sur `backend`
4. Définissez **"Dockerfile Path"** sur `Dockerfile.railway` (ou créez un symlink)

### 5.2 Configurer les variables d'environnement

Allez dans **"Variables"** de votre service web et ajoutez :

#### Variables obligatoires :

```bash
DJANGO_SECRET_KEY=votre-cle-secrete-tres-secure-changez-moi
DEBUG=0
ALLOWED_HOSTS=votre-app.railway.app,*.railway.app
```

**Pour générer une clé secrète Django sécurisée** :
```powershell
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

#### Variables pour SSL (production) :

```bash
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

#### Variables pour CORS (frontend Vercel) :

```bash
CORS_ALLOWED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app,https://egoejo.vercel.app
CSRF_TRUSTED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app,https://egoejo.vercel.app
```

⚠️ **Important** : Remplacez les URLs par les vraies URLs de votre frontend Vercel.

#### Variables optionnelles :

```bash
RESEND_API_KEY=votre-cle-resend-si-vous-en-avez-une
NOTIFY_EMAIL=notifications@egoejo.org
ADMIN_TOKEN=votre-token-admin-securise
ACCESS_TOKEN_MINUTES=60
ACCESS_TOKEN_DAYS=7
THROTTLE_ANON=10/minute
THROTTLE_USER=100/minute
APP_BASE_URL=https://votre-frontend.vercel.app
```

#### Variables automatiques (ajoutées par Railway) :

Ces variables sont **automatiquement ajoutées** par Railway, ne les ajoutez pas manuellement :
- ✅ `DATABASE_URL` (PostgreSQL)
- ✅ `REDIS_URL` (Redis)
- ✅ `PORT` (port sur lequel écouter)

---

## 🚀 Étape 6 : Déployer

### 6.1 Vérifier la configuration

1. Allez dans **"Settings"** de votre service web
2. Vérifiez que :
   - **Root Directory** : `backend`
   - **Build Command** : (automatique avec Dockerfile)
   - **Start Command** : (automatique avec Dockerfile)

### 6.2 Déclencher le déploiement

1. Railway déploie automatiquement quand vous **poussez sur GitHub**
2. Ou cliquez sur **"Deploy"** dans Railway pour déclencher un déploiement manuel

### 6.3 Surveiller les logs

1. Allez dans **"Deployments"** dans Railway
2. Cliquez sur le dernier déploiement
3. Vérifiez les logs pour voir si tout s'est bien passé

✅ Recherchez des messages comme :
- `✅ Base de données disponible !`
- `Operations to perform:`
- `Running migrations:`
- `Starting server...`

---

## 🌐 Étape 7 : Obtenir l'URL publique

1. Allez dans **"Settings"** → **"Networking"**
2. Railway vous donne une **URL publique** (ex: `https://egoejo-production.up.railway.app`)
3. Cliquez sur **"Generate Domain"** pour avoir un domaine Railway personnalisé

✅ **Notez cette URL** : vous en aurez besoin pour configurer le frontend.

---

## ✅ Étape 8 : Tester l'API

Testez votre API déployée :

```powershell
# Test endpoint principal
Invoke-WebRequest -Uri "https://votre-app.railway.app/api/" -UseBasicParsing

# Test endpoint spécifique
Invoke-WebRequest -Uri "https://votre-app.railway.app/api/intents/rejoindre/" -Method GET -UseBasicParsing
```

Ou dans votre navigateur :
```
https://votre-app.railway.app/api/
https://votre-app.railway.app/admin/
```

---

## 🔗 Étape 9 : Mettre à jour le frontend Vercel

Une fois le backend déployé et accessible, mettez à jour `VITE_API_URL` dans Vercel :

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend

# Supprimer l'ancienne valeur
npx vercel env rm VITE_API_URL production

# Ajouter la nouvelle URL
npx vercel env add VITE_API_URL production
# Entrez : https://votre-app.railway.app
```

Puis redéployez le frontend :

```powershell
npx vercel --prod
```

---

## 🔄 Étape 10 : Mettre à jour CORS dans le backend

Mettez à jour les variables d'environnement dans Railway pour inclure toutes les URLs de votre frontend :

```bash
CORS_ALLOWED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app,https://egoejo.vercel.app,https://votre-domaine.com
CSRF_TRUSTED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app,https://egoejo.vercel.app,https://votre-domaine.com
```

Puis redéployez le backend (Railway redéploie automatiquement quand vous modifiez les variables).

---

## 🐛 Résolution de problèmes courants

### ❌ Erreur : "DJANGO_SECRET_KEY must be set"
**Solution** : Vérifiez que la variable `DJANGO_SECRET_KEY` est bien configurée dans Railway.

### ❌ Erreur : "Database connection failed"
**Solution** : Vérifiez que le service PostgreSQL est bien ajouté et que `DATABASE_URL` est automatiquement disponible.

### ❌ Erreur : "CORS blocked"
**Solution** : Vérifiez que `CORS_ALLOWED_ORIGINS` contient l'URL exacte de votre frontend Vercel (avec `https://`).

### ❌ Erreur : "Static files not found"
**Solution** : Vérifiez que WhiteNoise est bien configuré dans `settings.py` (déjà présent).

### ❌ Erreur : "Port already in use"
**Solution** : Vérifiez que la commande de démarrage utilise bien `$PORT` au lieu d'un port fixe.

---

## 📚 Ressources

- **Documentation Railway** : https://docs.railway.app
- **Guide Django sur Railway** : https://docs.railway.app/guides/django
- **Support Railway** : https://railway.app/help
- **Discord Railway** : https://discord.gg/railway

---

## 🎯 Checklist finale

- [ ] Compte Railway créé
- [ ] Projet créé sur Railway
- [ ] Service PostgreSQL ajouté
- [ ] Service Redis ajouté
- [ ] Variables d'environnement configurées
- [ ] Backend déployé et accessible
- [ ] URL publique obtenue
- [ ] `VITE_API_URL` mis à jour dans Vercel
- [ ] CORS configuré dans le backend
- [ ] Frontend redéployé
- [ ] Test de connexion frontend → backend réussi

---

**🎉 Félicitations ! Votre backend est maintenant déployé sur Railway !**

