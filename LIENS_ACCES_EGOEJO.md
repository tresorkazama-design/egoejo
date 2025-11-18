# 🔗 Liens d'accès - Projet EGOEJO

> **📌 Note** : Si votre domaine Vercel est différent, remplacez `egoejo.vercel.app` par votre vrai domaine dans les liens ci-dessous.  
> **Pour trouver votre domaine Vercel** : Vercel Dashboard → Votre projet → Settings → Domains

## 🚀 Liens Rapides (Accès Direct)

### Production
- **🌐 Site Principal** : [https://egoejo.vercel.app/](https://egoejo.vercel.app/)
- **🎛️ Dashboard Admin** : [https://egoejo.vercel.app/admin](https://egoejo.vercel.app/admin)
- **🔧 Django Admin** : [https://egoejo-production.up.railway.app/admin/](https://egoejo-production.up.railway.app/admin/)
- **🔌 API Root** : [https://egoejo-production.up.railway.app/api/](https://egoejo-production.up.railway.app/api/)
- **💚 Health Check** : [https://egoejo-production.up.railway.app/api/health/](https://egoejo-production.up.railway.app/api/health/)

### Développement Local
- **🌐 Frontend Local** : [http://localhost:5173/](http://localhost:5173/)
- **🔌 API Local** : [http://localhost:8000/api/](http://localhost:8000/api/)
- **🔧 Django Admin Local** : [http://localhost:8000/admin/](http://localhost:8000/admin/)

---

## 📍 URLs de Production

### Frontend (Vercel)

#### Site principal
- **URL principale** : `https://egoejo.vercel.app/`
  - Page d'accueil EGOEJO
  - Navigation : Accueil, Univers, Vision, Citations, Alliances, Projets, Communauté, Votes, Rejoindre, Admin

#### Pages principales
- **Accueil** : `https://egoejo.vercel.app/`
- **Univers** : `https://egoejo.vercel.app/univers`
- **Vision** : `https://egoejo.vercel.app/vision`
- **Citations** : `https://egoejo.vercel.app/citations`
- **Alliances** : `https://egoejo.vercel.app/alliances`
- **Projets** : `https://egoejo.vercel.app/projets`
- **Communauté** : `https://egoejo.vercel.app/communaute`
- **Votes** : `https://egoejo.vercel.app/votes`
- **Rejoindre** : `https://egoejo.vercel.app/rejoindre`

#### Administration Frontend
- **Dashboard Admin** : `https://egoejo.vercel.app/admin`
  - Vue d'ensemble avec statistiques
  - Accès aux outils admin
  - Intégration Django Admin (iframe)
  
- **Page Intentions** : `https://egoejo.vercel.app/admin/intents`
  - Gérer les intentions de rejoindre
  - Filtrer par date, profil, recherche
  - Exporter en CSV
  - Supprimer des intentions

- **Page Modération** : `https://egoejo.vercel.app/admin/moderation`
  - Gérer les signalements
  - Voir les logs d'audit
  - Traiter les signalements

---

### Backend (Railway)

#### API REST
- **Root API** : `https://egoejo-production.up.railway.app/api/`
  - Informations sur l'API et endpoints disponibles

- **Health Check** : `https://egoejo-production.up.railway.app/api/health/`
  - Vérifier l'état du backend et de la base de données

#### Endpoints API

##### Intentions
- **Rejoindre** : `POST https://egoejo-production.up.railway.app/api/intents/rejoindre/`
- **Admin Data** : `GET https://egoejo-production.up.railway.app/api/intents/admin/`
- **Export CSV** : `GET https://egoejo-production.up.railway.app/api/intents/export/`
- **Supprimer** : `DELETE https://egoejo-production.up.railway.app/api/intents/{id}/delete/`

##### Chat
- **Threads** : `GET/POST https://egoejo-production.up.railway.app/api/chat/threads/`
- **Thread Detail** : `GET https://egoejo-production.up.railway.app/api/chat/threads/{id}/`
- **Messages** : `GET/POST https://egoejo-production.up.railway.app/api/chat/messages/`

##### Votes (Polls)
- **Liste** : `GET/POST https://egoejo-production.up.railway.app/api/polls/`
- **Détail** : `GET https://egoejo-production.up.railway.app/api/polls/{id}/`
- **Voter** : `POST https://egoejo-production.up.railway.app/api/polls/{id}/vote/`
- **Ouvrir** : `POST https://egoejo-production.up.railway.app/api/polls/{id}/open/`
- **Fermer** : `POST https://egoejo-production.up.railway.app/api/polls/{id}/close/`

##### Modération
- **Signalements** : `GET/POST https://egoejo-production.up.railway.app/api/moderation/reports/`
- **Détail signalement** : `GET https://egoejo-production.up.railway.app/api/moderation/reports/{id}/`
- **Logs d'audit** : `GET https://egoejo-production.up.railway.app/api/audit/logs/`

##### Projets & Cagnottes
- **Projets** : `GET/POST https://egoejo-production.up.railway.app/api/projets/`
- **Cagnottes** : `GET/POST https://egoejo-production.up.railway.app/api/cagnottes/`
- **Contribuer** : `POST https://egoejo-production.up.railway.app/api/cagnottes/{id}/contribute/`

#### Django Admin
- **Interface complète** : `https://egoejo-production.up.railway.app/admin/`
  - Gérer tous les modèles Django
  - Nécessite un superutilisateur Django
  - Interface d'administration complète

---

## 🏠 URLs de Développement Local

### Frontend (Vite)
- **URL locale** : `http://localhost:5173/`
  - Serveur de développement Vite
  - Hot reload activé

### Backend (Docker/Django)
- **API locale** : `http://localhost:8000/api/`
- **Django Admin local** : `http://localhost:8000/admin/`
- **Health Check local** : `http://localhost:8000/api/health/`

---

## 🔐 Authentification

### Frontend Admin
- **Méthode** : Token Bearer (`ADMIN_TOKEN`)
- **Stockage** : `localStorage.getItem("ADMIN_TOKEN")`
- **Configuration** : Variable d'environnement côté backend

### Django Admin
- **Méthode** : Superutilisateur Django
- **Création** : `python manage.py createsuperuser`
- **Connexion** : Nom d'utilisateur + mot de passe

---

## 📊 Tableaux de bord

### Frontend Admin Dashboard
- **URL** : `https://egoejo.vercel.app/admin`
- **Fonctionnalités** :
  - Statistiques (intentions, signalements, etc.)
  - Liens vers les outils admin
  - Intégration Django Admin (iframe)
  - Actions rapides

### Django Admin
- **URL** : `https://egoejo-production.up.railway.app/admin/`
- **Fonctionnalités** :
  - Gestion complète de tous les modèles
  - Filtres et recherche avancée
  - Exports (CSV, etc.)
  - Actions en masse
  - Gestion des utilisateurs

---

## 🔗 WebSockets (temps réel)

### Chat
- **URL** : `wss://egoejo-production.up.railway.app/ws/chat/{thread_id}/`
- **Protocole** : WebSocket
- **Usage** : Messages en temps réel dans les fils de discussion

### Votes (Polls)
- **URL** : `wss://egoejo-production.up.railway.app/ws/polls/{poll_id}/`
- **Protocole** : WebSocket
- **Usage** : Mises à jour en temps réel des scrutins

---

## 🛠️ Outils de développement

### Vercel Dashboard
- **URL** : `https://vercel.com/dashboard`
- **Usage** : Gérer les déploiements frontend, voir les logs, configurer les variables d'environnement

### Railway Dashboard
- **URL** : `https://railway.app/dashboard`
- **Usage** : Gérer le backend, voir les logs, configurer les variables d'environnement, gérer la base de données PostgreSQL

### GitHub Repository
- **URL** : `https://github.com/tresorkazama-design/egoejo`
- **Usage** : Code source, historique des commits, gestion des issues

---

## 📝 Variables d'environnement importantes

### Frontend (Vercel)
- `VITE_API_URL` : `https://egoejo-production.up.railway.app`
  - URL du backend pour les requêtes API

### Backend (Railway)
- `DATABASE_URL` : URL de connexion PostgreSQL (fournie par Railway)
- `DJANGO_SECRET_KEY` : Clé secrète Django
- `ALLOWED_HOSTS` : Domaines autorisés
- `RAILWAY_PUBLIC_DOMAIN` : Domaine public Railway (automatique)
- `REDIS_URL` : URL Redis pour WebSockets (si disponible)

---

## ✅ Checklist d'accès

- [ ] Frontend accessible sur Vercel : `https://egoejo.vercel.app/`
- [ ] Backend accessible sur Railway : `https://egoejo-production.up.railway.app/api/`
- [ ] Health check OK : `https://egoejo-production.up.railway.app/api/health/`
- [ ] Django Admin accessible : `https://egoejo-production.up.railway.app/admin/`
- [ ] Dashboard Admin Frontend accessible : `https://egoejo.vercel.app/admin`
- [ ] API endpoints fonctionnels
- [ ] WebSockets connectés (si configuré)

---

## 🚨 En cas de problème

### Frontend inaccessible
1. Vérifier le déploiement dans Vercel Dashboard
2. Vérifier les logs de déploiement
3. Vérifier que le Root Directory est `frontend` (pas `frontend/frontend`)
4. Vérifier que `VITE_API_URL` pointe vers le backend Railway

### Backend inaccessible
1. Vérifier le service Railway
2. Vérifier les logs Railway
3. Vérifier que `/api/health/` répond

### Django Admin inaccessible
1. Vérifier que le superutilisateur existe
2. Vérifier les logs Railway
3. Vérifier que les static files sont collectés (`collectstatic`)

---

**Dernière mise à jour** : Janvier 2025

