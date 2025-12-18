# ⚡ Instructions d'Activation Rapide - SAKA

**Date** : 17 Décembre 2025  
**Objectif** : Activer le protocole SAKA en production en 5 minutes

---

## 🚀 Activation en 3 Étapes

### Étape 1 : Ajouter les Variables (2 minutes)

#### Sur Railway

1. Allez sur [railway.app](https://railway.app) → Votre projet → Service backend
2. Cliquez sur **"Variables"**
3. Ajoutez ces 3 variables (cliquez sur **"New Variable"** pour chacune) :

```
ENABLE_SAKA = True
SAKA_COMPOST_ENABLED = True
SAKA_SILO_REDIS_ENABLED = True
```

4. Cliquez sur **"Redeploy"** pour redémarrer le service

#### Sur Vercel

1. Allez sur [vercel.com](https://vercel.com) → Votre projet
2. **Settings** → **Environment Variables**
3. Ajoutez les mêmes 3 variables pour **Production**
4. Redéployez

---

### Étape 2 : Vérifier (1 minute)

Une fois le service redémarré, vérifiez que ça fonctionne :

```bash
# Vérifier via l'API
curl https://votre-domaine.com/api/config/features/
```

**Résultat attendu** :
```json
{
  "saka_enabled": true,
  "saka_compost_enabled": true,
  "saka_silo_redis_enabled": true
}
```

---

### Étape 3 : Vérifier Celery Beat (2 minutes)

1. Vérifiez que le service **Celery Beat** est actif sur Railway
2. Vérifiez les logs pour voir :
   ```
   beat: Starting...
   Scheduler: Sending due task saka-compost-cycle
   ```

---

## ✅ C'est Tout !

Une fois ces 3 étapes faites :
- ✅ Le protocole SAKA est activé
- ✅ Le compostage s'exécutera automatiquement (tous les lundis à 3h UTC)
- ✅ La redistribution s'exécutera automatiquement (1er du mois à 4h UTC)

---

## 🔍 Vérification Complète (Optionnel)

Pour une vérification plus approfondie, consultez :
- `docs/deployment/CHECKLIST_ACTIVATION_PRODUCTION.md`

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide rapide

