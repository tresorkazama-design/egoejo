# 🚀 Guide de Déploiement - EGOEJO

Guide complet pour déployer EGOEJO en production.

---

## 📋 Prérequis

- Compte GitHub
- Compte Vercel (frontend)
- Compte Railway (backend)
- PostgreSQL (fourni par Railway)
- Redis (optionnel, pour WebSockets)

---

## 🎯 Déploiement Frontend (Vercel)

### 1. Préparation

```bash
cd frontend/frontend
npm run build
```

Vérifier que le build fonctionne sans erreurs.

### 2. Configuration Vercel

1. **Connecter le dépôt GitHub** à Vercel
2. **Configurer les variables d'environnement** :
   - `VITE_API_URL` : URL de l'API backend (ex: `https://api.egoejo.org`)
   - `VITE_SENTRY_DSN` : (optionnel) DSN Sentry

3. **Settings de build** :
   - Framework Preset : Vite
   - Build Command : `npm run build`
   - Output Directory : `dist`
   - Install Command : `npm ci`

### 3. Déploiement

Le déploiement est automatique via GitHub Actions (CD) ou manuel via Vercel Dashboard.

---

## 🔧 Déploiement Backend (Railway)

### 1. Préparation

```bash
cd backend
pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate
```

### 2. Configuration Railway

1. **Créer un nouveau projet** sur Railway
2. **Connecter le dépôt GitHub**
3. **Configurer les variables d'environnement** :

**Obligatoires** :
```
DJANGO_SECRET_KEY=<générer une clé secrète>
DEBUG=0
SECURE_SSL_REDIRECT=1
```

**Base de données** :
```
DATABASE_URL=<fourni automatiquement par Railway>
```

**CORS** :
```
CORS_ALLOWED_ORIGINS=https://egoejo.vercel.app,https://www.egoejo.org
CSRF_TRUSTED_ORIGINS=https://egoejo.vercel.app,https://www.egoejo.org
```

**Redis (optionnel)** :
```
REDIS_URL=<fourni par Railway Redis>
```

**Autres** :
```
ADMIN_TOKEN=<token pour l'admin>
RESEND_API_KEY=<pour les emails>
```

### 3. Configuration du Service

- **Start Command** : `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
- **Health Check Path** : `/health/`

### 4. Déploiement

Le déploiement est automatique via GitHub Actions (CD) ou manuel via Railway.

---

## 🔐 Sécurité en Production

### Checklist

- [ ] `DEBUG=0` en production
- [ ] `DJANGO_SECRET_KEY` unique et secret
- [ ] `SECURE_SSL_REDIRECT=1`
- [ ] CORS configuré avec les bonnes origines
- [ ] `ADMIN_TOKEN` configuré et sécurisé
- [ ] Secrets jamais commités
- [ ] HTTPS activé partout
- [ ] Rate limiting activé
- [ ] CSP configuré
- [ ] Backups automatiques configurés

---

## 📊 Monitoring Post-Déploiement

### Vérifications

1. **Health Checks** :
```bash
curl https://api.egoejo.org/health/
curl https://api.egoejo.org/api/health/
```

2. **Frontend** :
```bash
curl https://egoejo.vercel.app
```

3. **Lighthouse** :
```bash
npm run test:lighthouse
```

### Métriques à Surveiller

- Temps de réponse API
- Taux d'erreur
- Utilisation CPU/Mémoire
- Taille de la base de données
- Nombre de requêtes/minute

---

## 🔄 Rollback

### Frontend (Vercel)

1. Aller dans le Dashboard Vercel
2. Sélectionner le déploiement précédent
3. Cliquer sur "Promote to Production"

### Backend (Railway)

1. Aller dans le Dashboard Railway
2. Ouvrir les déploiements
3. Sélectionner un déploiement précédent
4. Cliquer sur "Redeploy"

---

## 🆘 Troubleshooting

### Problèmes Courants

1. **CORS Errors** :
   - Vérifier `CORS_ALLOWED_ORIGINS`
   - Vérifier que l'URL frontend est correcte

2. **Database Connection** :
   - Vérifier `DATABASE_URL`
   - Vérifier les migrations

3. **Static Files** :
   - Exécuter `collectstatic`
   - Vérifier WhiteNoise

4. **WebSockets** :
   - Vérifier `REDIS_URL`
   - Vérifier la configuration Channels

---

**Le déploiement est maintenant automatisé via CI/CD !** 🚀

