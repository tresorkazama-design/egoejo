# 🎯 Étapes suivantes - Déploiement Railway

## ✅ Étape 1 : Créer un nouveau projet

Dans Railway, cliquez sur le bouton **"+ New"** (en haut à droite).

Vous verrez un menu avec plusieurs options :
- **GitHub Repo** (recommandé)
- **Empty Project**
- **Template**

👉 **Sélectionnez "GitHub Repo"**

---

## 📦 Étape 2 : Connecter votre repository

1. Si c'est votre première fois, Railway vous demandera d'**autoriser l'accès à GitHub**
2. Autorisez Railway à accéder à vos repositories
3. Sélectionnez votre repository **`egoejo`**
4. Railway va automatiquement détecter la configuration

---

## 🔧 Étape 3 : Configurer le service web

Après la connexion, Railway va créer un service. Vous devrez configurer :

1. **Allez dans "Settings"** de votre service
2. **Configurez "Root Directory"** : `backend`
3. **Configurez "Dockerfile Path"** : `Dockerfile.railway`

Ou, si vous préférez, vous pouvez renommer `Dockerfile.railway` en `Dockerfile` temporairement pour que Railway le détecte automatiquement.

---

## 🗄️ Étape 4 : Ajouter PostgreSQL

1. Dans votre projet, cliquez sur **"+ New"**
2. Sélectionnez **"Database"**
3. Choisissez **"Add PostgreSQL"**
4. Railway crée automatiquement la base de données
5. ✅ Les variables d'environnement (`DATABASE_URL`, etc.) sont automatiquement ajoutées

---

## 🔴 Étape 5 : Ajouter Redis

1. Cliquez sur **"+ New"**
2. Sélectionnez **"Database"**
3. Choisissez **"Add Redis"**
4. Railway crée automatiquement le service Redis
5. ✅ La variable `REDIS_URL` est automatiquement ajoutée

---

## ⚙️ Étape 6 : Configurer les variables d'environnement

Dans votre service web, allez dans **"Variables"** et ajoutez :

### Variables obligatoires :

```bash
DJANGO_SECRET_KEY=mtOu0flMSlreGirj2T6jIxaYqysq_UVc9YY0ZIYPnGjD0jZLq2kVJQbUg_Amsivx53A
DEBUG=0
ALLOWED_HOSTS=votre-app.railway.app,*.railway.app
```

⚠️ **Important** : Remplacez `votre-app.railway.app` par le vrai nom de domaine que Railway vous donnera après le déploiement.

### Variables pour la production :

```bash
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

### Variables pour CORS (URL de votre frontend Vercel) :

```bash
CORS_ALLOWED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
CSRF_TRUSTED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
```

### Variables optionnelles :

```bash
RESEND_API_KEY=
NOTIFY_EMAIL=notifications@egoejo.org
ADMIN_TOKEN=
ACCESS_TOKEN_MINUTES=60
ACCESS_TOKEN_DAYS=7
THROTTLE_ANON=10/minute
THROTTLE_USER=100/minute
APP_BASE_URL=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
```

---

## 🚀 Étape 7 : Déployer

1. Railway déploie **automatiquement** après chaque push sur GitHub
2. Ou vous pouvez cliquer sur **"Deploy"** pour déclencher un déploiement manuel
3. Surveillez les **logs** pour voir le progrès

---

## 🌐 Étape 8 : Obtenir l'URL publique

1. Allez dans **"Settings"** → **"Networking"**
2. Railway génère automatiquement un domaine
3. Ou cliquez sur **"Generate Domain"** pour obtenir un domaine personnalisé
4. ✅ **Notez cette URL** (ex: `https://egoejo-production.up.railway.app`)

---

## 🔗 Étape 9 : Mettre à jour le frontend

Une fois le backend déployé, mettez à jour `VITE_API_URL` dans Vercel :

```powershell
cd C:\Users\treso\Downloads\egoejo\frontend\frontend
npx vercel env rm VITE_API_URL production
npx vercel env add VITE_API_URL production
# Entrez l'URL de votre backend Railway
```

Puis redéployez :
```powershell
npx vercel --prod
```

---

## ✅ Test final

Testez que tout fonctionne :

1. Vérifiez que le backend répond : `https://votre-app.railway.app/api/`
2. Testez depuis le frontend que les requêtes API fonctionnent

---

**🚀 C'est parti ! Commencez par cliquer sur "+ New" → "GitHub Repo"**

