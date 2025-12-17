# 🚀 Guide d'Activation des Feature Flags EGOEJO

**Date** : 17 Décembre 2025  
**Objectif** : Activer le protocole SAKA et ses mécanismes (compostage, redistribution) en production

---

## ⚠️ IMPORTANT : Sans Activation, le Moteur SAKA Reste Éteint

Par défaut, **tous les feature flags sont désactivés** (`False`). Cela signifie que :
- ❌ Le protocole SAKA ne fonctionne pas
- ❌ Le compostage ne s'exécute pas
- ❌ La redistribution ne s'exécute pas
- ❌ Les utilisateurs ne peuvent pas récolter ou planter de SAKA

**Pour activer le protocole SAKA en production, vous DEVEZ définir explicitement les variables d'environnement.**

---

## 📋 Variables d'Environnement Requises

### 1. Activation du Protocole SAKA

**Variable** : `ENABLE_SAKA`  
**Valeur** : `True`  
**Description** : Active le protocole SAKA (récolte, plantation, exposition dans global-assets)

**Où l'activer** :
- **Railway** : Onglet "Variables" → Ajouter `ENABLE_SAKA=True`
- **Vercel** : Settings → Environment Variables → Ajouter `ENABLE_SAKA=True` (pour le backend si déployé sur Vercel)
- **Docker** : Dans votre `.env` ou `docker-compose.yml`

**Code concerné** :
```python
# backend/config/settings.py
ENABLE_SAKA = os.environ.get('ENABLE_SAKA', 'False').lower() == 'true'
```

---

### 2. Activation du Compostage

**Variable** : `SAKA_COMPOST_ENABLED`  
**Valeur** : `True`  
**Description** : Active le compostage progressif (10% du solde après 90 jours d'inactivité)

**Où l'activer** :
- **Railway** : Onglet "Variables" → Ajouter `SAKA_COMPOST_ENABLED=True`
- **Vercel** : Settings → Environment Variables → Ajouter `SAKA_COMPOST_ENABLED=True`
- **Docker** : Dans votre `.env` ou `docker-compose.yml`

**Code concerné** :
```python
# backend/config/settings.py
SAKA_COMPOST_ENABLED = os.environ.get('SAKA_COMPOST_ENABLED', 'False').lower() == 'true'
```

**Tâche Celery** :
- Exécution : Tous les lundis à 3h UTC
- Service : `core.tasks.saka_run_compost_cycle`
- Configuration : `backend/config/celery.py`

---

### 3. Activation de la Redistribution

**Variable** : `SAKA_SILO_REDIS_ENABLED`  
**Valeur** : `True`  
**Description** : Active la redistribution automatique du Silo Commun (5% par cycle)

**Où l'activer** :
- **Railway** : Onglet "Variables" → Ajouter `SAKA_SILO_REDIS_ENABLED=True`
- **Vercel** : Settings → Environment Variables → Ajouter `SAKA_SILO_REDIS_ENABLED=True`
- **Docker** : Dans votre `.env` ou `docker-compose.yml`

**Code concerné** :
```python
# backend/config/settings.py
SAKA_SILO_REDIS_ENABLED = os.environ.get('SAKA_SILO_REDIS_ENABLED', 'False').lower() == 'true'
```

**Tâche Celery** :
- Exécution : Le 1er de chaque mois à 4h UTC
- Service : `core.tasks.run_saka_silo_redistribution`
- Configuration : `backend/config/celery.py`

---

### 4. Activation de l'Investissement (V2.0 - Optionnel)

**Variable** : `ENABLE_INVESTMENT_FEATURES`  
**Valeur** : `True` (uniquement si vous avez l'agrément AMF)  
**Description** : Active les fonctionnalités d'investissement (V2.0 dormant)

**⚠️ ATTENTION** : Ne pas activer sans agrément AMF. Le code est présent mais non testé en production.

**Où l'activer** :
- **Railway** : Onglet "Variables" → Ajouter `ENABLE_INVESTMENT_FEATURES=True`
- **Vercel** : Settings → Environment Variables → Ajouter `ENABLE_INVESTMENT_FEATURES=True`
- **Docker** : Dans votre `.env` ou `docker-compose.yml`

**Code concerné** :
```python
# backend/config/settings.py
ENABLE_INVESTMENT_FEATURES = os.environ.get('ENABLE_INVESTMENT_FEATURES', 'False').lower() == 'true'
```

---

## 🔧 Configuration Railway

### Étape 1 : Accéder aux Variables d'Environnement

1. Connectez-vous à [Railway](https://railway.app)
2. Sélectionnez votre projet **"egoejo"** (ou le nom de votre service backend)
3. Cliquez sur l'onglet **"Variables"**

### Étape 2 : Ajouter les Variables

Cliquez sur **"New Variable"** et ajoutez :

```bash
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True
```

### Étape 3 : Redéployer

Railway redéploie automatiquement votre service après avoir ajouté/modifié des variables.

**Vérification** :
1. Allez dans l'onglet **"Deployments"**
2. Vérifiez que le dernier déploiement est en cours ou terminé
3. Vérifiez les logs pour confirmer que les variables sont chargées

---

## 🔧 Configuration Vercel (Si Backend Déployé sur Vercel)

### Étape 1 : Accéder aux Variables d'Environnement

1. Connectez-vous à [Vercel](https://vercel.com)
2. Sélectionnez votre projet **"egoejo-backend"** (ou le nom de votre projet)
3. Allez dans **"Settings"** → **"Environment Variables"**

### Étape 2 : Ajouter les Variables

Cliquez sur **"Add New"** et ajoutez :

```bash
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True
```

**Environnements** : Sélectionnez **"Production"**, **"Preview"**, et **"Development"** selon vos besoins.

### Étape 3 : Redéployer

Vercel redéploie automatiquement votre service après avoir ajouté/modifié des variables.

**Vérification** :
1. Allez dans l'onglet **"Deployments"**
2. Vérifiez que le dernier déploiement est en cours ou terminé
3. Vérifiez les logs pour confirmer que les variables sont chargées

---

## 🔧 Configuration Docker

### Étape 1 : Créer un Fichier `.env`

Créez un fichier `.env` à la racine de votre projet :

```bash
# Feature Flags EGOEJO
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True

# Autres variables (exemple)
DJANGO_SECRET_KEY=votre-cle-secrete
DEBUG=0
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Étape 2 : Modifier `docker-compose.yml`

Assurez-vous que votre `docker-compose.yml` charge le fichier `.env` :

```yaml
services:
  web:
    build: ./backend
    env_file:
      - .env
    environment:
      - ENABLE_SAKA=${ENABLE_SAKA}
      - SAKA_COMPOST_ENABLED=${SAKA_COMPOST_ENABLED}
      - SAKA_SILO_REDIS_ENABLED=${SAKA_SILO_REDIS_ENABLED}
```

### Étape 3 : Redémarrer les Containers

```bash
docker-compose down
docker-compose up -d
```

---

## ✅ Vérification de l'Activation

### 1. Vérifier les Logs

Après le redéploiement, vérifiez les logs pour confirmer que les variables sont chargées :

```bash
# Railway
# Allez dans l'onglet "Deployments" → Cliquez sur le dernier déploiement → "Logs"

# Vercel
# Allez dans l'onglet "Deployments" → Cliquez sur le dernier déploiement → "Logs"

# Docker
docker-compose logs web | grep -i "ENABLE_SAKA\|SAKA_COMPOST"
```

### 2. Tester l'API

Testez que le protocole SAKA est activé :

```bash
# Test de l'endpoint SAKA (doit retourner des données si activé)
curl https://votre-backend.railway.app/api/saka/wallet/

# Test de l'endpoint Silo (doit retourner des données si activé)
curl https://votre-backend.railway.app/api/saka/silo/
```

### 3. Vérifier les Tâches Celery

Vérifiez que les tâches Celery sont configurées :

```bash
# Railway / Vercel
# Vérifiez les logs du worker Celery pour confirmer que les tâches sont planifiées

# Docker
docker-compose logs celery | grep -i "saka-compost\|saka-silo"
```

---

## 🎯 Configuration Recommandée pour Production

### Configuration Minimale (SAKA Actif)

```bash
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True
```

### Configuration Complète (SAKA + Investissement V2.0)

```bash
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True
ENABLE_INVESTMENT_FEATURES=True  # ⚠️ Uniquement si agrément AMF
```

---

## ⚠️ Points d'Attention

### 1. Celery Beat Doit Être Actif

Les tâches de compostage et redistribution nécessitent que **Celery Beat** soit actif.

**Vérification** :
- Railway : Vérifiez qu'un service Celery Beat est configuré
- Vercel : Vérifiez que les tâches cron sont configurées
- Docker : Vérifiez que le container `celery-beat` est actif

### 2. Redis Doit Être Configuré

Les tâches Celery nécessitent Redis comme broker.

**Vérification** :
- Railway : Vérifiez que le service Redis est actif
- Vercel : Vérifiez que la variable `REDIS_URL` est définie
- Docker : Vérifiez que le container `redis` est actif

### 3. Base de Données Doit Être Prête

Les modèles SAKA doivent être migrés.

**Vérification** :
```bash
# Railway / Vercel
# Vérifiez que les migrations sont appliquées dans les logs de déploiement

# Docker
docker-compose exec web python manage.py migrate
```

---

## 📊 Checklist d'Activation

- [ ] Variable `ENABLE_SAKA=True` ajoutée
- [ ] Variable `SAKA_COMPOST_ENABLED=True` ajoutée
- [ ] Variable `SAKA_SILO_REDIS_ENABLED=True` ajoutée
- [ ] Service redéployé
- [ ] Logs vérifiés (variables chargées)
- [ ] API testée (endpoints SAKA répondent)
- [ ] Celery Beat actif
- [ ] Redis configuré
- [ ] Migrations appliquées

---

## 🆘 Dépannage

### Le Protocole SAKA Ne Fonctionne Pas

1. **Vérifiez les variables** : Assurez-vous que `ENABLE_SAKA=True` est bien défini
2. **Vérifiez les logs** : Cherchez des erreurs dans les logs de déploiement
3. **Vérifiez l'API** : Testez les endpoints SAKA pour voir s'ils retournent des données

### Le Compostage Ne S'Exécute Pas

1. **Vérifiez la variable** : Assurez-vous que `SAKA_COMPOST_ENABLED=True` est bien défini
2. **Vérifiez Celery Beat** : Assurez-vous que Celery Beat est actif
3. **Vérifiez les logs** : Cherchez les logs de la tâche `saka_run_compost_cycle`

### La Redistribution Ne S'Exécute Pas

1. **Vérifiez la variable** : Assurez-vous que `SAKA_SILO_REDIS_ENABLED=True` est bien défini
2. **Vérifiez Celery Beat** : Assurez-vous que Celery Beat est actif
3. **Vérifiez les logs** : Cherchez les logs de la tâche `run_saka_silo_redistribution`

---

**Date de génération** : 17 Décembre 2025  
**Auteur** : Gardien de cohérence du Manifeste EGOEJO  
**Version du document** : 1.0

