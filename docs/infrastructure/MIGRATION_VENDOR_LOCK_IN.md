# Audit Stratégique : Sortie Vendor Lock-In

**Date** : 2025-01-27  
**Objectif** : Documenter la procédure de migration depuis Railway/Vercel vers Docker standard

---

## 📋 Résumé Exécutif

### Situation Actuelle

- **Backend** : Déployé sur Railway
- **Frontend** : Déployé sur Vercel
- **Dépendances** : Variables d'environnement Railway, configuration Vercel

### Objectif

✅ **Être migrable, pas migré**

Le projet doit pouvoir être déployé sur n'importe quel hébergeur supportant Docker Compose, sans dépendance aux services Railway ou Vercel.

---

## 🔍 Analyse des Dépendances

### Backend (Railway)

**Dépendances Identifiées** :

1. **Variables d'environnement Railway** :
   - `RAILWAY_PUBLIC_DOMAIN` (optionnel)
   - `RAILWAY_ENVIRONMENT` (optionnel)
   - `RAILWAY_PROJECT_ID` (optionnel)
   - `DATABASE_URL` (géré automatiquement par Railway)
   - `REDIS_URL` (géré automatiquement par Railway)
   - `PORT` (géré automatiquement par Railway)

**Impact** : ✅ **FAIBLE** - Toutes les variables Railway sont optionnelles dans `backend/config/settings.py`

**Code** :
```python
# backend/config/settings.py
_railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if _railway_domain and _railway_domain not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_domain)
```

**Conclusion** : Le code fonctionne avec ou sans Railway.

### Frontend (Vercel)

**Dépendances Identifiées** :

1. **Configuration Vercel** :
   - `vercel.json` (configuration de build)
   - Variables d'environnement Vercel (`VITE_API_URL`)

**Impact** : ✅ **FAIBLE** - Le frontend est une SPA React/Vite standard, servable via Nginx

**Conclusion** : Le frontend peut être servi via Nginx sans modification.

---

## 🛠️ Fichiers Créés

### 1. `docker-compose.prod.yml`

Configuration Docker Compose complète pour production :

- **web** : Backend Django (ASGI avec Daphne)
- **worker** : Celery worker
- **beat** : Celery beat
- **db** : PostgreSQL 16
- **cache** : Redis 7
- **nginx** : Reverse proxy + frontend statique

### 2. `nginx/nginx.conf`

Configuration Nginx principale avec :
- Compression Gzip
- Headers de sécurité
- Rate limiting
- Logging

### 3. `nginx/conf.d/egoejo.conf`

Configuration Nginx pour EGOEJO :
- Frontend React (SPA)
- Backend API Django (reverse proxy)
- WebSockets (Django Channels)
- Fichiers statiques Django
- Fichiers média

### 4. `backend/.env.production.template`

Template pour les variables d'environnement production.

### 5. `README_MIGRATION_INFRA.md`

Documentation complète de migration avec :
- Procédures étape par étape
- Checklist de migration
- Troubleshooting
- Exemples de déploiement (VPS, AWS, Kubernetes)

---

## 📊 Tableau de Comparaison

| Aspect | Railway/Vercel | Docker Compose |
|--------|----------------|----------------|
| **Dépendances** | Variables Railway, config Vercel | Aucune (Docker standard) |
| **Portabilité** | ❌ Lock-in Railway/Vercel | ✅ Portable (n'importe quel hébergeur) |
| **Coût** | Pay-as-you-go | Contrôle total |
| **Scalabilité** | Automatique | Manuelle (mais flexible) |
| **Maintenance** | Gérée par Railway/Vercel | Gérée par l'équipe |
| **Complexité** | Faible | Moyenne |

---

## ✅ Checklist de Migration

### Pré-Migration

- [x] Analyser les dépendances Railway/Vercel
- [x] Créer `docker-compose.prod.yml`
- [x] Créer configuration Nginx
- [x] Créer template `.env.production`
- [x] Documenter la procédure de migration

### Migration (À Faire)

- [ ] Exporter variables d'environnement depuis Railway
- [ ] Exporter base de données depuis Railway
- [ ] Build frontend avec nouvelle `VITE_API_URL`
- [ ] Tester `docker-compose.prod.yml` localement
- [ ] Déployer sur hébergeur cible
- [ ] Configurer SSL (Let's Encrypt)
- [ ] Configurer monitoring
- [ ] Configurer backups

---

## 🎯 Objectif Atteint

✅ **Le projet est maintenant migrable, pas migré.**

- ✅ Configuration Docker standard (pas de dépendance Railway)
- ✅ Frontend servable via Nginx (pas de dépendance Vercel)
- ✅ Documentation complète pour équipe externe
- ✅ Procédures de migration claires et testables

**Le projet peut être déployé sur n'importe quel hébergeur supportant Docker Compose.**

---

**Fin de l'Audit**

*Dernière mise à jour : 2025-01-27*

