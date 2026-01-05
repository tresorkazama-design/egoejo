# 🚀 Guide de Migration Infrastructure - EGOEJO

**Objectif** : Éviter le vendor lock-in en documentant la migration depuis Railway/Vercel vers Docker standard.

**Date** : 2025-01-27  
**Version** : 1.0.0

---

## 📋 Table des Matières

1. [Vue d'ensemble](#vue-densemble)
2. [Migration Backend : Railway → Docker](#migration-backend--railway--docker)
3. [Migration Frontend : Vercel → Nginx](#migration-frontend--vercel--nginx)
4. [Configuration Docker Compose](#configuration-docker-compose)
5. [Variables d'Environnement](#variables-denvironnement)
6. [Déploiement sur Hébergeur Standard](#déploiement-sur-hébergeur-standard)
7. [Checklist de Migration](#checklist-de-migration)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Vue d'ensemble

### Architecture Actuelle (Railway + Vercel)

```
┌─────────────┐         ┌─────────────┐
│   Railway   │         │   Vercel    │
│  (Backend)  │◄────────┤  (Frontend) │
│             │   API   │             │
│  Django     │         │   React     │
│  PostgreSQL │         │   Static    │
│  Redis      │         │             │
└─────────────┘         └─────────────┘
```

### Architecture Cible (Docker Compose)

```
┌─────────────────────────────────────────┐
│         Docker Compose Stack             │
│  ┌──────────┐  ┌──────────┐            │
│  │  Nginx   │  │  Django   │            │
│  │ (Frontend│  │  (Backend) │            │
│  │  Static) │  │           │            │
│  └──────────┘  └──────────┘            │
│       │              │                   │
│  ┌──────────┐  ┌──────────┐            │
│  │PostgreSQL│  │  Redis   │            │
│  └──────────┘  └──────────┘            │
│       │              │                   │
│  ┌──────────┐  ┌──────────┐            │
│  │  Celery  │  │  Beat    │            │
│  │  Worker  │  │          │            │
│  └──────────┘  └──────────┘            │
└─────────────────────────────────────────┘
```

---

## 🔄 Migration Backend : Railway → Docker

### Étape 1 : Exporter les Variables d'Environnement

**Depuis Railway** :

1. Allez dans votre projet Railway
2. Ouvrez le service backend
3. Allez dans l'onglet **"Variables"**
4. Exportez toutes les variables dans un fichier `.env.production`

**Exemple** :

```bash
# backend/.env.production
DJANGO_SECRET_KEY=votre-cle-secrete
DEBUG=0
ALLOWED_HOSTS=egoejo.org,www.egoejo.org
DATABASE_URL=postgresql://user:password@db:5432/egoejo
REDIS_URL=redis://cache:6379/0
CORS_ALLOWED_ORIGINS=https://egoejo.org
CSRF_TRUSTED_ORIGINS=https://egoejo.org
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
RESEND_API_KEY=votre-cle-resend
NOTIFY_EMAIL=notifications@egoejo.org
ADMIN_TOKEN=votre-token-admin
```

### Étape 2 : Exporter la Base de Données

**Depuis Railway** :

```bash
# Depuis votre machine locale
pg_dump $DATABASE_URL > backup_railway.sql
```

**Ou via Railway CLI** :

```bash
railway connect postgres
pg_dump > backup_railway.sql
```

### Étape 3 : Adapter le Dockerfile

Le `Dockerfile` existant est déjà compatible. Vérifiez qu'il contient :

```dockerfile
FROM python:3.11-slim
# ... (voir backend/Dockerfile)
CMD sh -c "python manage.py migrate && daphne -b 0.0.0.0 -p ${PORT:-8000} config.asgi:application"
```

### Étape 4 : Supprimer les Dépendances Railway

**Dans `backend/config/settings.py`** :

Les variables Railway sont déjà gérées de manière optionnelle :

```python
# ✅ Déjà compatible - fonctionne avec ou sans Railway
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)
```

**Aucune modification nécessaire** - le code fonctionne avec ou sans Railway.

---

## 🌐 Migration Frontend : Vercel → Nginx

### Étape 1 : Build le Frontend

**Localement** :

```bash
cd frontend/frontend
npm install
npm run build
```

**Résultat** : `frontend/frontend/dist/` contient les fichiers statiques.

### Étape 2 : Configurer Nginx

Le fichier `nginx/conf.d/egoejo.conf` est déjà configuré pour servir le frontend :

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

### Étape 3 : Adapter les Variables d'Environnement

**Dans Vercel** :

1. Allez dans votre projet Vercel
2. Ouvrez **"Settings"** → **"Environment Variables"**
3. Notez la valeur de `VITE_API_URL`

**Dans Docker** :

Mettez à jour `nginx/conf.d/egoejo.conf` pour pointer vers votre backend :

```nginx
location /api/ {
    proxy_pass http://django_backend;
}
```

**Dans le build frontend** :

Le `VITE_API_URL` est utilisé au build time. Rebuild le frontend avec la nouvelle URL :

```bash
cd frontend/frontend
VITE_API_URL=https://api.egoejo.org npm run build
```

---

## 🐳 Configuration Docker Compose

### Fichier : `docker-compose.prod.yml`

Le fichier `docker-compose.prod.yml` contient :

- **web** : Backend Django (ASGI avec Daphne)
- **worker** : Celery worker (tâches asynchrones)
- **beat** : Celery beat (tâches périodiques)
- **db** : PostgreSQL 16
- **cache** : Redis 7
- **nginx** : Reverse proxy + frontend statique

### Démarrage

```bash
# 1. Créer le fichier .env.production
cp backend/.env.template backend/.env.production
# Éditer backend/.env.production avec vos valeurs

# 2. Build le frontend
cd frontend/frontend
npm run build

# 3. Démarrer les services
docker-compose -f docker-compose.prod.yml up -d

# 4. Vérifier les logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Arrêt

```bash
docker-compose -f docker-compose.prod.yml down
```

### Backup de la Base de Données

```bash
# Backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U egoejo egoejo > backup.sql

# Restore
docker-compose -f docker-compose.prod.yml exec -T db psql -U egoejo egoejo < backup.sql
```

---

## 🔐 Variables d'Environnement

### Fichier : `backend/.env.production`

**Variables Obligatoires** :

```bash
# Sécurité
DJANGO_SECRET_KEY=<générer une clé de 50+ caractères>
DEBUG=0
ALLOWED_HOSTS=egoejo.org,www.egoejo.org

# Base de données (utilisées par docker-compose.prod.yml)
DB_NAME=egoejo
DB_USER=egoejo
DB_PASSWORD=<mot de passe sécurisé>

# Redis (utilisé par docker-compose.prod.yml)
REDIS_URL=redis://cache:6379/0

# CORS
CORS_ALLOWED_ORIGINS=https://egoejo.org
CSRF_TRUSTED_ORIGINS=https://egoejo.org

# SSL
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

**Variables Optionnelles** :

```bash
# Email
RESEND_API_KEY=<votre clé Resend>
NOTIFY_EMAIL=notifications@egoejo.org

# Admin
ADMIN_TOKEN=<token sécurisé>

# Monitoring
SENTRY_DSN=<votre DSN Sentry>

# Rate Limiting
THROTTLE_ANON=10/minute
THROTTLE_USER=100/minute
```

### Génération des Secrets

```bash
# DJANGO_SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(50))"

# ADMIN_TOKEN
python -c "import secrets; print(secrets.token_urlsafe(32))"

# DB_PASSWORD
openssl rand -base64 32
```

---

## 🚀 Déploiement sur Hébergeur Standard

### Option 1 : VPS (DigitalOcean, Hetzner, OVH)

**Prérequis** :
- VPS avec Docker et Docker Compose installés
- Domaine pointant vers l'IP du VPS
- Certificat SSL (Let's Encrypt)

**Étapes** :

```bash
# 1. Cloner le dépôt
git clone https://github.com/votre-org/egoejo.git
cd egoejo

# 2. Configurer .env.production
cp backend/.env.template backend/.env.production
# Éditer backend/.env.production

# 3. Build le frontend
cd frontend/frontend
npm run build
cd ../..

# 4. Démarrer les services
docker-compose -f docker-compose.prod.yml up -d

# 5. Configurer SSL (Let's Encrypt)
# Installer certbot
sudo apt-get install certbot python3-certbot-nginx

# Générer les certificats
sudo certbot --nginx -d egoejo.org -d www.egoejo.org

# Mettre à jour nginx/conf.d/egoejo.conf pour utiliser SSL
```

### Option 2 : AWS ECS / Fargate

**Prérequis** :
- Compte AWS
- ECR (Elastic Container Registry)
- ECS Cluster
- RDS (PostgreSQL)
- ElastiCache (Redis)

**Étapes** :

1. **Build et Push les Images** :

```bash
# Build
docker build -t egoejo-backend:latest ./backend
docker build -t egoejo-nginx:latest ./nginx

# Tag pour ECR
docker tag egoejo-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/egoejo-backend:latest
docker tag egoejo-nginx:latest <account-id>.dkr.ecr.<region>.amazonaws.com/egoejo-nginx:latest

# Push
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/egoejo-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/egoejo-nginx:latest
```

2. **Créer les Services ECS** :

- Task Definition pour backend
- Task Definition pour nginx
- Service ECS pour chaque task
- Load Balancer (ALB) pour le trafic

3. **Configurer RDS et ElastiCache** :

- Créer une instance RDS PostgreSQL
- Créer un cluster ElastiCache Redis
- Mettre à jour les variables d'environnement

### Option 3 : Kubernetes

**Prérequis** :
- Cluster Kubernetes (GKE, EKS, AKS, ou self-hosted)
- kubectl configuré

**Étapes** :

1. **Créer les Manifests** :

```bash
# Créer les fichiers Kubernetes
kubectl create namespace egoejo

# Déployer PostgreSQL (ou utiliser un service managé)
kubectl apply -f k8s/postgresql.yaml

# Déployer Redis (ou utiliser un service managé)
kubectl apply -f k8s/redis.yaml

# Déployer le backend
kubectl apply -f k8s/backend.yaml

# Déployer le frontend (Nginx)
kubectl apply -f k8s/nginx.yaml
```

2. **Configurer Ingress** :

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: egoejo-ingress
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - egoejo.org
      secretName: egoejo-tls
  rules:
    - host: egoejo.org
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: nginx
                port:
                  number: 80
```

---

## ✅ Checklist de Migration

### Pré-Migration

- [ ] Exporter toutes les variables d'environnement depuis Railway
- [ ] Exporter la base de données depuis Railway
- [ ] Exporter les fichiers média (si stockés sur Railway)
- [ ] Noter l'URL du frontend Vercel
- [ ] Noter l'URL du backend Railway

### Migration Backend

- [ ] Créer `backend/.env.production` avec les variables exportées
- [ ] Adapter `ALLOWED_HOSTS` pour le nouveau domaine
- [ ] Adapter `CORS_ALLOWED_ORIGINS` pour le nouveau domaine
- [ ] Tester `docker-compose.prod.yml` localement
- [ ] Importer la base de données dans le nouveau PostgreSQL
- [ ] Vérifier que les migrations Django fonctionnent

### Migration Frontend

- [ ] Build le frontend avec la nouvelle `VITE_API_URL`
- [ ] Tester le build localement (`npm run preview`)
- [ ] Vérifier que Nginx sert correctement le frontend
- [ ] Tester les routes React (SPA)

### Post-Migration

- [ ] Configurer SSL (Let's Encrypt)
- [ ] Configurer le monitoring (Sentry, logs)
- [ ] Configurer les backups automatiques
- [ ] Tester tous les endpoints API
- [ ] Tester les WebSockets
- [ ] Tester les tâches Celery
- [ ] Vérifier les emails (Resend)
- [ ] Mettre à jour le DNS
- [ ] Rediriger l'ancien domaine vers le nouveau (optionnel)

---

## 🔧 Troubleshooting

### Problème : Backend ne démarre pas

**Solution** :

```bash
# Vérifier les logs
docker-compose -f docker-compose.prod.yml logs web

# Vérifier les variables d'environnement
docker-compose -f docker-compose.prod.yml exec web env | grep DJANGO

# Vérifier la connexion à la base de données
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
```

### Problème : Frontend ne charge pas

**Solution** :

```bash
# Vérifier que le build existe
ls -la frontend/frontend/dist/

# Vérifier les logs Nginx
docker-compose -f docker-compose.prod.yml logs nginx

# Vérifier la configuration Nginx
docker-compose -f docker-compose.prod.yml exec nginx nginx -t
```

### Problème : WebSockets ne fonctionnent pas

**Solution** :

1. Vérifier que Redis est démarré :
```bash
docker-compose -f docker-compose.prod.yml ps cache
```

2. Vérifier la configuration Nginx pour WebSockets :
```nginx
location /ws/ {
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Problème : Celery ne fonctionne pas

**Solution** :

```bash
# Vérifier les logs du worker
docker-compose -f docker-compose.prod.yml logs worker

# Vérifier les logs de beat
docker-compose -f docker-compose.prod.yml logs beat

# Vérifier la connexion Redis
docker-compose -f docker-compose.prod.yml exec worker python -c "from django.core.cache import cache; print(cache.get('test'))"
```

---

## 📚 Ressources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

---

## 🎯 Objectif Atteint

✅ **Le projet est maintenant migrable, pas migré.**

- ✅ Configuration Docker standard (pas de dépendance Railway)
- ✅ Frontend servable via Nginx (pas de dépendance Vercel)
- ✅ Documentation complète pour équipe externe
- ✅ Procédures de migration claires et testables

**Le projet peut être déployé sur n'importe quel hébergeur supportant Docker Compose.**

---

**Fin du Guide de Migration**

*Dernière mise à jour : 2025-01-27*

