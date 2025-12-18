# 🚂 Guide d'Activation - Railway

**Date** : 17 Décembre 2025  
**Objectif** : Activer les feature flags SAKA sur Railway

---

## 📋 Étapes d'Activation

### 1. Accéder aux Variables d'Environnement

1. Connectez-vous à [Railway](https://railway.app)
2. Sélectionnez votre projet **EGOEJO**
3. Sélectionnez le service **backend** (ou le service Django)
4. Allez dans l'onglet **"Variables"** (ou **"Settings"** → **"Variables"**)

### 2. Ajouter les Variables

Cliquez sur **"New Variable"** et ajoutez les variables suivantes :

#### Variable 1 : ENABLE_SAKA
- **Nom** : `ENABLE_SAKA`
- **Valeur** : `True`
- **Description** : Active le protocole SAKA

#### Variable 2 : SAKA_COMPOST_ENABLED
- **Nom** : `SAKA_COMPOST_ENABLED`
- **Valeur** : `True`
- **Description** : Active le compostage progressif

#### Variable 3 : SAKA_SILO_REDIS_ENABLED
- **Nom** : `SAKA_SILO_REDIS_ENABLED`
- **Valeur** : `True`
- **Description** : Active la redistribution automatique du Silo

#### Variable 4 : NOTIFY_EMAIL (Optionnel mais recommandé)
- **Nom** : `NOTIFY_EMAIL`
- **Valeur** : `votre-email@example.com`
- **Description** : Email pour recevoir les alertes de monitoring

### 3. Redémarrer le Service

**IMPORTANT** : Après avoir ajouté les variables, vous DEVEZ redémarrer le service :

1. Allez dans l'onglet **"Deployments"**
2. Cliquez sur **"Redeploy"** (ou **"Deploy"**)
3. Attendez que le déploiement soit terminé

### 4. Vérifier l'Activation

Une fois le service redémarré, vérifiez que les variables sont bien prises en compte :

1. Allez dans l'onglet **"Logs"**
2. Cherchez dans les logs : `ENABLE_SAKA=True` ou `SAKA enabled`
3. Vérifiez qu'il n'y a pas d'erreurs de configuration

---

## 🔍 Vérification via API

Une fois activé, vous pouvez vérifier via l'API :

```bash
# Vérifier que SAKA est activé
curl https://votre-domaine.railway.app/api/config/features/

# Réponse attendue :
{
  "saka_enabled": true,
  "saka_compost_enabled": true,
  "saka_silo_redis_enabled": true
}
```

---

## ⚠️ Points d'Attention

### Redis Doit Être Actif

Les feature flags SAKA nécessitent Redis pour Celery. Vérifiez que :
- Un service Redis est déployé sur Railway
- La variable `REDIS_URL` est définie
- Redis est accessible depuis le service backend

### Celery Beat Doit Être Actif

Pour que le compostage et la redistribution s'exécutent automatiquement :
- Un service **Celery Beat** doit être déployé
- Il doit utiliser la même configuration Redis que le backend
- Vérifiez les logs pour confirmer qu'il démarre

---

## 🐛 Dépannage

### Problème : Les variables ne sont pas prises en compte

**Solution** :
1. Vérifiez que les variables sont bien définies (pas de fautes de frappe)
2. Vérifiez que le service a été redémarré
3. Vérifiez les logs pour voir si les variables sont lues

### Problème : Celery Beat ne démarre pas

**Solution** :
1. Vérifiez que Redis est accessible
2. Vérifiez que `REDIS_URL` est définie
3. Vérifiez les logs de Celery Beat

### Problème : Les tâches ne s'exécutent pas

**Solution** :
1. Vérifiez que Celery Beat est actif
2. Vérifiez que les feature flags sont activés
3. Vérifiez les logs pour voir les erreurs éventuelles

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide de référence

