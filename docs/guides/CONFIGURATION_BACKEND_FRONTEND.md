# Configuration Backend ↔ Frontend

## État actuel

### ✅ Backend (Docker)
- **URL locale** : `http://localhost:8000`
- **Status** : ✅ Fonctionnel (Docker actif)
- **Endpoints API** : `/api/`
- **CORS** : Configuré pour autoriser `localhost:5173` et `localhost:3000`

### ⚠️ Frontend Local
- **Port** : `5173` (Vite)
- **Configuration API** : ❌ Manque `VITE_API_URL`
- **Fichier `.env.local`** : Non présent (créer manuellement)

### ⚠️ Frontend Vercel (Production)
- **URL** : `https://frontend-7ov9dp1ri-kazamas-projects-67d737b9.vercel.app`
- **Variables d'environnement** : ❌ `VITE_API_URL` non configuré

---

## Actions à effectuer

### 1. Configuration Frontend Local

Créez le fichier `frontend/frontend/.env.local` :

```bash
VITE_API_URL=http://localhost:8000
```

Puis redémarrez le serveur de développement :
```bash
cd frontend/frontend
npm run dev
```

### 2. Configuration Frontend Vercel (Production)

#### Option A : Via CLI Vercel
```bash
cd frontend/frontend
npx vercel env add VITE_API_URL production
# Entrez l'URL de votre backend (ex: https://api.egoejo.com ou http://localhost:8000)
```

#### Option B : Via Dashboard Vercel
1. Allez sur : https://vercel.com/kazamas-projects-67d737b9/frontend/settings/environment-variables
2. Cliquez sur "Add New"
3. Nom : `VITE_API_URL`
4. Valeur : URL de votre backend (voir options ci-dessous)
5. Environnements : Cochez "Production"
6. Cliquez sur "Save"

#### Option C : Si backend local avec tunnel
Si votre backend est local et que vous voulez le rendre accessible depuis Vercel :

**Avec ngrok** :
```bash
ngrok http 8000
# Utilisez l'URL https fournie par ngrok
```

**Avec Cloudflare Tunnel** :
```bash
cloudflared tunnel --url http://localhost:8000
```

### 3. Configuration CORS Backend

Le backend doit autoriser les requêtes depuis Vercel. Modifiez `backend/.env` :

```bash
CORS_ALLOWED_ORIGINS=https://frontend-7ov9dp1ri-kazamas-projects-67d737b9.vercel.app,https://votre-domaine.com
CSRF_TRUSTED_ORIGINS=https://frontend-7ov9dp1ri-kazamas-projects-67d737b9.vercel.app,https://votre-domaine.com
```

Puis redémarrez le backend :
```bash
docker compose restart web
```

---

## Test de connexion

### Test Backend Local
```bash
# Test endpoint API
curl http://localhost:8000/api/

# Test endpoint spécifique
curl http://localhost:8000/api/intents/rejoindre/
```

### Test Frontend → Backend
Dans la console du navigateur (F12), exécutez :
```javascript
fetch('http://localhost:8000/api/')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

---

## Endpoints disponibles

- `POST /api/intents/rejoindre/` - Formulaire de candidature
- `GET /api/intents/admin/` - Données admin
- `GET /api/chat/threads/` - Liste des fils de discussion
- `GET /api/polls/` - Liste des scrutins
- `GET /api/moderation/reports/` - Signalements de modération
- `GET /api/audit/logs/` - Logs d'audit

---

## Prochaines étapes recommandées

1. ✅ Créer `.env.local` pour le développement local
2. ✅ Configurer `VITE_API_URL` dans Vercel
3. ✅ Mettre à jour CORS du backend pour autoriser Vercel
4. ⚠️ Déployer le backend en production (ou utiliser un tunnel)
5. ⚠️ Configurer un domaine personnalisé pour le backend

