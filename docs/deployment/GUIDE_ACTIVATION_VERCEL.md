# ▲ Guide d'Activation - Vercel

**Date** : 17 Décembre 2025  
**Objectif** : Activer les feature flags SAKA sur Vercel

---

## ⚠️ Note Importante

**Vercel est principalement utilisé pour le frontend**. Si votre backend Django est déployé sur Vercel, suivez ce guide. Sinon, utilisez le guide Railway.

---

## 📋 Étapes d'Activation

### 1. Accéder aux Variables d'Environnement

1. Connectez-vous à [Vercel](https://vercel.com)
2. Sélectionnez votre projet **EGOEJO**
3. Allez dans **Settings** → **Environment Variables**

### 2. Ajouter les Variables

Pour chaque variable, sélectionnez l'environnement (**Production**, **Preview**, **Development**) et ajoutez :

#### Variable 1 : ENABLE_SAKA
- **Key** : `ENABLE_SAKA`
- **Value** : `True`
- **Environment** : Production (et Preview si nécessaire)

#### Variable 2 : SAKA_COMPOST_ENABLED
- **Key** : `SAKA_COMPOST_ENABLED`
- **Value** : `True`
- **Environment** : Production (et Preview si nécessaire)

#### Variable 3 : SAKA_SILO_REDIS_ENABLED
- **Key** : `SAKA_SILO_REDIS_ENABLED`
- **Value** : `True`
- **Environment** : Production (et Preview si nécessaire)

#### Variable 4 : NOTIFY_EMAIL
- **Key** : `NOTIFY_EMAIL`
- **Value** : `votre-email@example.com`
- **Environment** : Production

### 3. Redéployer

**IMPORTANT** : Après avoir ajouté les variables, vous DEVEZ redéployer :

1. Allez dans l'onglet **"Deployments"**
2. Cliquez sur **"Redeploy"** sur le dernier déploiement
3. Ou créez un nouveau déploiement en poussant un commit

### 4. Vérifier l'Activation

Une fois redéployé, vérifiez via l'API :

```bash
curl https://votre-domaine.vercel.app/api/config/features/
```

---

## ⚠️ Limitations Vercel

### Celery Beat sur Vercel

**Vercel ne supporte pas les tâches périodiques de manière native**. Si votre backend est sur Vercel, vous devez :

1. **Option 1** : Utiliser un service externe pour Celery Beat (Railway, Heroku, etc.)
2. **Option 2** : Utiliser Vercel Cron Jobs (si disponible)
3. **Option 3** : Déclencher manuellement les tâches via l'API admin

### Configuration Recommandée

Pour EGOEJO, il est recommandé de :
- **Backend Django** : Railway (pour Celery Beat)
- **Frontend React** : Vercel (pour le déploiement rapide)

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide de référence

