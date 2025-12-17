# 🔧 Variables d'Environnement SAKA - Configuration Production

**Date** : 17 Décembre 2025  
**Objectif** : Activer le protocole SAKA en production

---

## 🎯 Variables à Définir

### Variables Obligatoires pour Activer SAKA

```bash
# Activation du protocole SAKA
ENABLE_SAKA=True

# Activation du compostage progressif (10% après 90 jours d'inactivité)
SAKA_COMPOST_ENABLED=True

# Activation de la redistribution du Silo (5% mensuellement)
SAKA_SILO_REDIS_ENABLED=True
```

### Variables Optionnelles (avec valeurs par défaut)

```bash
# Jours d'inactivité avant compostage (défaut: 90)
SAKA_COMPOST_INACTIVITY_DAYS=90

# Taux de compostage (défaut: 0.10 = 10%)
SAKA_COMPOST_RATE=0.10

# Solde minimum pour compostage (défaut: 20 SAKA)
SAKA_COMPOST_MIN_BALANCE=20

# Taux de redistribution du Silo (défaut: 0.05 = 5%)
SAKA_SILO_REDIS_RATE=0.05

# Activité minimum pour être éligible à la redistribution (défaut: 1)
SAKA_SILO_REDIS_MIN_WALLET_ACTIVITY=1
```

---

## 🚀 Configuration par Plateforme

### Railway

1. **Aller dans le projet** : https://railway.app
2. **Sélectionner le service backend**
3. **Onglet "Variables"**
4. **Ajouter les variables** :
   ```
   ENABLE_SAKA=True
   SAKA_COMPOST_ENABLED=True
   SAKA_SILO_REDIS_ENABLED=True
   ```
5. **Redeployer** le service

### Vercel

1. **Aller dans le projet** : https://vercel.com
2. **Settings → Environment Variables**
3. **Ajouter les variables** pour **Production**, **Preview**, et **Development** :
   ```
   ENABLE_SAKA=True
   SAKA_COMPOST_ENABLED=True
   SAKA_SILO_REDIS_ENABLED=True
   ```
4. **Redeployer** l'application

### Docker / Local

Créer un fichier `.env` dans `backend/` :

```bash
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True
```

Puis redémarrer les services :
```bash
docker-compose restart backend
# ou
python manage.py runserver
```

---

## ✅ Vérification de l'Activation

### 1. Vérifier les Variables dans le Code

```python
# backend/config/settings.py
ENABLE_SAKA = os.getenv('ENABLE_SAKA', 'False').lower() == 'true'
SAKA_COMPOST_ENABLED = os.getenv('SAKA_COMPOST_ENABLED', 'False').lower() == 'true'
SAKA_SILO_REDIS_ENABLED = os.getenv('SAKA_SILO_REDIS_ENABLED', 'False').lower() == 'true'
```

### 2. Vérifier via l'API

```bash
# Vérifier que l'API SAKA est accessible
curl https://votre-domaine.com/api/saka/silo/

# Devrait retourner :
# {
#   "enabled": true,
#   "total_balance": 0,
#   ...
# }
```

### 3. Vérifier les Tâches Celery

```bash
# Vérifier que Celery Beat est configuré
celery -A config beat --loglevel=info

# Devrait afficher :
# saka-compost-cycle: core.tasks.saka_run_compost_cycle (lundi 3h UTC)
# saka-silo-redistribution: core.tasks.run_saka_silo_redistribution (1er du mois 4h UTC)
```

---

## ⚠️ Points d'Attention

### 1. Redis Doit Être Configuré

Le protocole SAKA nécessite Redis pour :
- Cache
- Celery broker
- WebSockets (Channels)

Vérifier que `REDIS_URL` est défini.

### 2. Celery Worker Doit Être Actif

Les tâches de compostage et redistribution nécessitent un worker Celery actif :

```bash
celery -A config worker --loglevel=info
```

### 3. Celery Beat Doit Être Actif

Pour les tâches périodiques :

```bash
celery -A config beat --loglevel=info
```

---

## 📊 Checklist d'Activation

- [ ] Variables d'environnement définies (`ENABLE_SAKA=True`, etc.)
- [ ] Redis configuré et accessible
- [ ] Celery worker actif
- [ ] Celery Beat actif (pour tâches périodiques)
- [ ] API `/api/saka/silo/` retourne `enabled: true`
- [ ] API `/api/saka/cycles/` accessible
- [ ] Frontend affiche la page `/saka/saisons`
- [ ] Dashboard affiche la prévisualisation du compostage

---

## 🔍 Dépannage

### Problème : API SAKA retourne `enabled: false`

**Solution** : Vérifier que `ENABLE_SAKA=True` est bien défini et que le service a été redémarré.

### Problème : Compostage ne se déclenche pas

**Solution** : Vérifier que :
- `SAKA_COMPOST_ENABLED=True`
- Celery Beat est actif
- La tâche est programmée (lundi 3h UTC)

### Problème : Redistribution ne se déclenche pas

**Solution** : Vérifier que :
- `SAKA_SILO_REDIS_ENABLED=True`
- Celery Beat est actif
- La tâche est programmée (1er du mois 4h UTC)

---

## 📝 Notes

- Les feature flags sont **désactivés par défaut** pour éviter l'activation accidentelle
- L'activation nécessite une **action explicite** via variables d'environnement
- Les tâches Celery sont **automatiques** une fois activées (pas besoin d'intervention manuelle)

---

**Date de création** : 17 Décembre 2025  
**Référence** : `docs/deployment/GUIDE_ACTIVATION_FEATURE_FLAGS.md`

