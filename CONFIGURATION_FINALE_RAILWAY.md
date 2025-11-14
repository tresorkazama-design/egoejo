# ✅ Configuration finale - Backend Railway

## 🌐 URL de votre backend Railway
**URL publique** : `https://egoejo-production.up.railway.app`

---

## ⚙️ Configuration des variables d'environnement dans Railway

Dans votre service "egoejo" sur Railway :

### 1. Allez dans l'onglet "Variables"

### 2. Ajoutez/modifiez ces variables :

#### Variables obligatoires :
```bash
DJANGO_SECRET_KEY=mtOu0flMSlreGirj2T6jIxaYqysq_UVc9YY0ZIYPnGjD0jZLq2kVJQbUg_Amsivx53A
DEBUG=0
ALLOWED_HOSTS=egoejo-production.up.railway.app,*.railway.app
```

#### Variables pour la production (SSL) :
```bash
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

#### Variables pour CORS (Frontend Vercel) :
```bash
CORS_ALLOWED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
CSRF_TRUSTED_ORIGINS=https://frontend-bwrs98104-kazamas-projects-67d737b9.vercel.app
```

#### Variables optionnelles :
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

#### Variables automatiques (déjà ajoutées par Railway) :
- ✅ `DATABASE_URL` (ajoutée automatiquement par PostgreSQL)
- ✅ `REDIS_URL` (ajoutée automatiquement par Redis)
- ✅ `PORT` (ajoutée automatiquement par Railway)

---

## 🔄 Après avoir configuré les variables

Railway va automatiquement redéployer votre service avec les nouvelles variables.

---

## ✅ Test de votre backend

Testez que votre backend répond :

```powershell
Invoke-WebRequest -Uri "https://egoejo-production.up.railway.app/api/" -UseBasicParsing
```

Vous devriez recevoir une réponse (peut-être une erreur 404 ou 405, mais cela signifie que le serveur répond).

---

## 🔗 Prochaine étape : Mettre à jour le frontend Vercel

Une fois les variables configurées dans Railway, mettez à jour `VITE_API_URL` dans Vercel.

