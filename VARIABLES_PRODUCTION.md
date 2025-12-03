# 🔐 Variables d'Environnement Production - EGOEJO

**Date** : 2025-01-27  
**Version** : 1.0.0

---

## 📋 Backend (Railway/Vercel)

### Variables Obligatoires

```bash
# Sécurité
DEBUG=0
DJANGO_SECRET_KEY=<générer une clé de 50+ caractères>
ALLOWED_HOSTS=api.egoejo.org,www.egoejo.org,egoejo.railway.app
SECURE_SSL_REDIRECT=1
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1

# Base de données
DATABASE_URL=postgresql://user:password@host:5432/dbname

# CORS
CORS_ALLOWED_ORIGINS=https://egoejo.vercel.app,https://www.egoejo.org
CSRF_TRUSTED_ORIGINS=https://egoejo.vercel.app,https://www.egoejo.org

# Redis (optionnel, pour WebSockets)
REDIS_URL=redis://host:6379/0

# Email
RESEND_API_KEY=<votre clé Resend>
NOTIFY_EMAIL=notifications@egoejo.org

# Admin
ADMIN_TOKEN=<token sécurisé pour l'admin>

# Monitoring
SENTRY_DSN=<votre DSN Sentry backend>

# Rate Limiting
THROTTLE_ANON=10/minute
THROTTLE_USER=100/minute
THROTTLE_IP=100/hour
```

### Variables Optionnelles

```bash
# JWT
ACCESS_TOKEN_MINUTES=60
REFRESH_TOKEN_DAYS=7

# Logging
LOG_LEVEL=INFO

# Railway (auto-détecté)
RAILWAY_PUBLIC_DOMAIN=<auto>
RAILWAY_ENVIRONMENT=<auto>
RAILWAY_PROJECT_ID=<auto>
```

---

## 📋 Frontend (Vercel)

### Variables Obligatoires

```bash
# API
VITE_API_URL=https://api.egoejo.org
```

### Variables Optionnelles

```bash
# Monitoring
VITE_SENTRY_DSN=<votre DSN Sentry frontend>
```

---

## 🔑 Génération des Secrets

### DJANGO_SECRET_KEY

```python
# Python
import secrets
print(secrets.token_urlsafe(50))
```

```bash
# Bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

### ADMIN_TOKEN

```python
# Python
import secrets
print(secrets.token_urlsafe(32))
```

---

## ✅ Vérification

### Backend

```bash
# Vérifier la configuration
python manage.py check --deploy
```

### Frontend

```bash
# Vérifier le build
npm run build
npm run preview
```

---

## 🚨 Sécurité

⚠️ **IMPORTANT** :
- Ne jamais commiter les secrets dans Git
- Utiliser les secrets GitHub pour CI/CD
- Utiliser les variables d'environnement de la plateforme (Railway/Vercel)
- Changer tous les secrets par défaut
- Utiliser des clés uniques pour chaque environnement

---

## 📚 Documentation

- `GUIDE_PRODUCTION.md` - Guide complet de production
- `CHECKLIST_PRODUCTION.md` - Checklist de vérification
- `PRODUCTION_READY.md` - État de préparation

---

**Toutes les variables sont configurées !** ✅

