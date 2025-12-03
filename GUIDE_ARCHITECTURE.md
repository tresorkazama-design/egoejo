# 🏗️ Guide d'Architecture - EGOEJO

Ce document décrit l'architecture complète du projet EGOEJO.

---

## 📐 Vue d'Ensemble

EGOEJO est une application full-stack avec :
- **Frontend** : React 19 + Vite (SPA)
- **Backend** : Django 5 + Django REST Framework (API REST)
- **Base de données** : PostgreSQL (production) / SQLite (développement)
- **Temps réel** : WebSockets via Django Channels + Redis
- **Déploiement** : Vercel (frontend) + Railway (backend)

---

## 🎨 Architecture Frontend

### Structure

```
frontend/frontend/src/
├── app/              # Pages et routing
│   ├── pages/        # Composants de pages
│   └── router.jsx    # Configuration du routing
├── components/       # Composants réutilisables
├── contexts/         # Contextes React (Auth, Language, Notifications)
├── hooks/            # Hooks personnalisés
├── utils/            # Utilitaires (API, i18n, logger, analytics)
├── styles/           # Styles globaux
└── locales/          # Fichiers de traduction
```

### Patterns Utilisés

1. **Lazy Loading** : Toutes les pages sont lazy-loaded
2. **Code Splitting** : Chunks séparés (react, three, gsap, vendor)
3. **Context API** : Pour l'état global (auth, language, notifications)
4. **Custom Hooks** : Pour la logique réutilisable
5. **Error Boundaries** : Pour gérer les erreurs React

### Flux de Données

```
User Action → Component → Hook/Context → API → Backend
                                      ↓
                                   Response
                                      ↓
                              Update State → Re-render
```

---

## 🔧 Architecture Backend

### Structure

```
backend/
├── config/           # Configuration Django
│   ├── settings.py   # Settings principaux
│   ├── urls.py       # URLs racine
│   └── asgi.py       # ASGI pour WebSockets
├── core/             # Application principale
│   ├── api/          # Endpoints API REST
│   ├── models/       # Modèles de données
│   ├── serializers/  # Sérialiseurs DRF
│   ├── consumers.py  # WebSocket consumers
│   └── urls.py       # URLs de l'API
└── manage.py         # CLI Django
```

### Patterns Utilisés

1. **REST API** : Endpoints RESTful standardisés
2. **ViewSets** : Pour les CRUD operations
3. **Serializers** : Pour la validation et sérialisation
4. **Permissions** : Système de permissions DRF
5. **Throttling** : Rate limiting par utilisateur et IP

### Flux de Requête

```
Client → CORS Middleware → Security Middleware → CSP Middleware
    → Auth Middleware → View → Serializer → Model → Database
                                                    ↓
                                              Response ←
```

---

## 🔌 Communication Frontend ↔ Backend

### REST API

**Base URL** : `http://localhost:8000/api` (dev) ou `https://api.egoejo.org/api` (prod)

**Authentification** : JWT Bearer Token
```
Authorization: Bearer <access_token>
```

**Endpoints Principaux** :
- `GET /api/projets/` - Liste des projets
- `POST /api/auth/login/` - Connexion
- `POST /api/auth/refresh/` - Refresh token (avec rotation)
- `GET /api/chat/threads/` - Threads de chat
- `POST /api/chat/messages/` - Envoyer un message

### WebSockets

**URL** : `ws://localhost:8000/ws/chat/<thread_id>/?token=<jwt_token>`

**Protocole** :
```json
// Client → Server
{ "type": "chat_message", "content": "Hello" }

// Server → Client
{ "type": "chat_message", "payload": { "id": 1, "content": "Hello", ... } }
```

---

## 🗄️ Base de Données

### Modèles Principaux

- **User** : Utilisateurs Django
- **Projet** : Projets du collectif
- **ChatThread** : Threads de discussion
- **ChatMessage** : Messages dans les threads
- **Poll** : Sondages communautaires
- **Intent** : Intentions de rejoindre

### Relations

- Projet → User (auteur)
- ChatThread → Projet (optionnel, pour chats liés aux projets)
- ChatMessage → ChatThread
- Poll → User (créateur)

---

## 🔐 Sécurité

### Backend

1. **Authentification** : JWT avec refresh tokens
2. **Autorisation** : Permissions DRF
3. **Rate Limiting** : Par utilisateur et par IP
4. **CSP** : Content Security Policy
5. **CORS** : Origines autorisées uniquement
6. **HTTPS** : Forcé en production
7. **HSTS** : Headers de sécurité

### Frontend

1. **Validation** : Côté client et serveur
2. **XSS Protection** : Échappement automatique React
3. **CSRF** : Tokens CSRF pour les formulaires
4. **Secrets** : Jamais commités, variables d'environnement

---

## ⚡ Performance

### Frontend

1. **Lazy Loading** : Routes et images
2. **Code Splitting** : Chunks optimisés
3. **Caching** : Service Worker (PWA)
4. **Compression** : Terser avec tree shaking
5. **Images** : Lazy loading avec IntersectionObserver

### Backend

1. **Database** : `select_related()` et `prefetch_related()`
2. **Caching** : Redis pour le cache
3. **Pagination** : Sur toutes les listes
4. **Connection Pooling** : Pour PostgreSQL

---

## 📊 Monitoring & Analytics

### Monitoring

- **Sentry** : Erreurs et performance
- **Health Checks** : `/api/health/`
- **Logging** : Système de logging professionnel

### Analytics

- **Page Views** : Tracking automatique
- **Events** : Système d'analytics centralisé
- **Conversions** : Tracking des conversions

---

## 🚀 Déploiement

### Frontend (Vercel)

1. Build automatique sur push
2. Preview pour chaque PR
3. CDN global
4. SSL automatique

### Backend (Railway)

1. Déploiement depuis Git
2. Variables d'environnement sécurisées
3. PostgreSQL géré
4. Redis optionnel

---

## 🔄 CI/CD

### Continuous Integration

1. **Tests** : Frontend et backend
2. **Linting** : ESLint et Bandit
3. **Security** : npm audit et safety
4. **Build** : Vérification du build

### Continuous Deployment

1. **Frontend** : Auto-deploy sur `main`
2. **Backend** : Auto-deploy sur `main`
3. **Lighthouse** : Vérification performance post-deploy

---

## 📚 Technologies Clés

### Frontend
- React 19.2.0
- Vite 7.1.11
- React Router 7.9.4
- Three.js 0.180.0
- GSAP 3.13.0

### Backend
- Django 5.0+
- Django REST Framework 3.15.0+
- Channels 4.0.0
- PostgreSQL / SQLite
- Redis (optionnel)

---

## 🎯 Principes d'Architecture

1. **Séparation des Responsabilités** : Frontend/Backend clairement séparés
2. **API First** : Backend comme API indépendante
3. **Stateless** : Pas de session serveur (JWT)
4. **Scalable** : Architecture prête pour la montée en charge
5. **Maintainable** : Code modulaire et documenté

---

**Cette architecture permet une évolutivité et une maintenabilité optimales.** 🏗️

