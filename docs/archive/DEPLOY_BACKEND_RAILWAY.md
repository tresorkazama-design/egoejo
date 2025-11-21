# Guide de déploiement du backend sur Railway

## 🚀 Railway - Déploiement étape par étape

Railway est une plateforme cloud qui supporte Docker et offre PostgreSQL et Redis comme services gérés.

### Prérequis
- Compte GitHub (pour connecter Railway)
- Compte Railway : https://railway.app (inscription gratuite)

---

## 📋 Étape 1 : Préparer le backend

### 1.1 Vérifier les fichiers nécessaires
Les fichiers suivants doivent exister :
- ✅ `backend/Dockerfile` (déjà présent)
- ✅ `backend/requirements.txt` (déjà présent)
- ✅ `railway.json` (créé dans la racine)

### 1.2 Mettre à jour le Dockerfile pour Railway
Railway utilise la variable `PORT` automatiquement, mais nous devons nous assurer que notre application l'utilise.

Le Dockerfile actuel utilise le port 8000 en dur. Nous allons créer une version adaptée pour Railway.

---

## 📤 Étape 2 : Créer un projet Railway

### 2.1 Se connecter à Railway
1. Allez sur https://railway.app
2. Cliquez sur "Login" puis "Sign Up with GitHub"
3. Autorisez Railway à accéder à votre compte GitHub

### 2.2 Créer un nouveau projet
1. Cliquez sur "New Project"
2. Sélectionnez "Deploy from GitHub repo"
3. Choisissez votre repository `egoejo`
4. Railway va détecter automatiquement le Dockerfile

### 2.3 Configurer les services
Railway va créer un service "web" automatiquement. Nous devons aussi ajouter :
- **PostgreSQL** (base de données)
- **Redis** (cache/WebSockets)

---

## ⚙️ Étape 3 : Configurer les services

### 3.1 Ajouter PostgreSQL
1. Dans votre projet Railway, cliquez sur "+ New"
2. Sélectionnez "Database" → "Add PostgreSQL"
3. Railway crée automatiquement une base PostgreSQL
4. Notez les variables d'environnement créées (DATABASE_URL, PGUSER, PGPASSWORD, etc.)

### 3.2 Ajouter Redis
1. Cliquez sur "+ New"
2. Sélectionnez "Database" → "Add Redis"
3. Railway crée automatiquement un service Redis
4. Notez la variable REDIS_URL créée

---

## 🔧 Étape 4 : Configurer les variables d'environnement

Dans Railway, allez dans "Variables" de votre service web et ajoutez :

### Variables obligatoires :
```
DJANGO_SECRET_KEY=votre-cle-secrete-tres-secure-changez-moi
DEBUG=0
ALLOWED_HOSTS=votre-app.railway.app,*.railway.app
```

### Variables pour la base de données (ajoutées automatiquement par Railway PostgreSQL) :
```
DATABASE_URL=postgresql://... (automatique)
DB_NAME=postgres (vérifier dans les variables)
DB_USER=postgres (vérifier dans les variables)
DB_PASSWORD=... (vérifier dans les variables)
DB_HOST=... (vérifier dans les variables)
DB_PORT=5432
```

### Variables pour Redis (ajoutées automatiquement par Railway Redis) :
```
REDIS_URL=redis://... (automatique)
```

### Variables pour CORS (URL de votre frontend Vercel) :
```
CORS_ALLOWED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app,https://egoejo.vercel.app
CSRF_TRUSTED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app,https://egoejo.vercel.app
```

### Variables pour SSL (production) :
```
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

### Variables optionnelles :
```
RESEND_API_KEY=votre-cle-resend-si-vous-en-avez-une
NOTIFY_EMAIL=notifications@egoejo.org
ADMIN_TOKEN=votre-token-admin-securise
ACCESS_TOKEN_MINUTES=60
ACCESS_TOKEN_DAYS=7
THROTTLE_ANON=10/minute
THROTTLE_USER=100/minute
APP_BASE_URL=https://votre-frontend.vercel.app
```

---

## 🔄 Étape 5 : Adapter le code pour Railway

### 5.1 Mettre à jour le Dockerfile pour utiliser PORT
Railway expose le port via la variable `PORT`. Nous devons adapter la commande de démarrage.

Le Dockerfile actuel utilise Gunicorn, mais notre app utilise Daphne (ASGI). Créons un fichier `railway.toml` pour configurer la commande de démarrage.

### 5.2 Créer railway.toml (optionnel)
Railway peut aussi utiliser un fichier `railway.toml` à la racine pour configurer le déploiement.

---

## 🚀 Étape 6 : Déployer

### 6.1 Configurer le build
1. Dans Railway, allez dans "Settings" de votre service web
2. Vérifiez que "Root Directory" est défini sur `backend`
3. Railway devrait détecter automatiquement le Dockerfile

### 6.2 Configurer la commande de démarrage
Dans "Settings" → "Deploy", configurez :

**Start Command** (si vous n'utilisez pas le Dockerfile) :
```bash
sh -c "python manage.py migrate && daphne -b 0.0.0.0 -p $PORT config.asgi:application"
```

Mais comme nous utilisons Docker, la commande dans le Dockerfile sera utilisée.

### 6.3 Déployer
1. Railway déploie automatiquement quand vous poussez sur GitHub
2. Ou cliquez sur "Deploy" pour déclencher un déploiement manuel

---

## ✅ Étape 7 : Vérifier le déploiement

### 7.1 Vérifier les logs
1. Allez dans "Deployments" dans Railway
2. Cliquez sur le dernier déploiement
3. Vérifiez les logs pour voir si tout s'est bien passé

### 7.2 Tester l'API
Railway vous donne une URL publique (ex: `https://votre-app.railway.app`).

Testez :
```bash
curl https://votre-app.railway.app/api/
```

### 7.3 Configurer le domaine personnalisé (optionnel)
1. Dans "Settings" → "Domains"
2. Cliquez sur "Generate Domain" pour avoir un domaine Railway
3. Ou ajoutez un domaine personnalisé si vous en avez un

---

## 🔗 Étape 8 : Mettre à jour le frontend

Une fois le backend déployé, mettez à jour `VITE_API_URL` dans Vercel :

```bash
cd frontend/frontend
npx vercel env rm VITE_API_URL production
npx vercel env add VITE_API_URL production
# Entrez : https://votre-app.railway.app
```

Puis redéployez le frontend :
```bash
npx vercel --prod
```

---

## 🐛 Résolution de problèmes

### Problème : Port non configuré
**Solution** : Assurez-vous que la variable `PORT` est utilisée dans la commande de démarrage.

### Problème : Base de données non accessible
**Solution** : Vérifiez que toutes les variables d'environnement de la base de données sont configurées.

### Problème : CORS bloque les requêtes
**Solution** : Vérifiez que `CORS_ALLOWED_ORIGINS` contient l'URL de votre frontend Vercel.

### Problème : Static files non servis
**Solution** : Assurez-vous que WhiteNoise est configuré (déjà présent dans `settings.py`).

---

## 📚 Ressources

- Documentation Railway : https://docs.railway.app
- Guide Django sur Railway : https://docs.railway.app/guides/django
- Support Railway : https://railway.app/help

---

## 🎯 Checklist finale

- [ ] Compte Railway créé
- [ ] Projet créé sur Railway
- [ ] Service PostgreSQL ajouté
- [ ] Service Redis ajouté
- [ ] Variables d'environnement configurées
- [ ] Backend déployé et accessible
- [ ] `VITE_API_URL` mis à jour dans Vercel
- [ ] Frontend redéployé
- [ ] Test de connexion frontend → backend réussi

