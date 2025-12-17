# ✅ Checklist d'Activation Production - Protocole SAKA

**Date** : 17 Décembre 2025  
**Objectif** : Activer le protocole SAKA en production de manière sécurisée

---

## 🔴 ÉTAPE 1 : Variables d'Environnement (OBLIGATOIRE)

### Dans Railway

1. Aller dans l'onglet **"Variables"** de votre service backend
2. Ajouter les variables suivantes :

```
ENABLE_SAKA=True
SAKA_COMPOST_ENABLED=True
SAKA_SILO_REDIS_ENABLED=True
```

3. **Redémarrer le service** après avoir ajouté les variables

### Dans Vercel (si backend déployé sur Vercel)

1. Aller dans **Settings** → **Environment Variables**
2. Ajouter les mêmes variables pour l'environnement **Production**
3. Redéployer l'application

### Vérification

```bash
# Vérifier que les variables sont bien définies
# Dans les logs du service, vous devriez voir :
# "ENABLE_SAKA=True" dans la configuration
```

---

## 🔴 ÉTAPE 2 : Vérifier Celery Beat

### Prérequis

- Redis doit être actif et accessible
- Variable `REDIS_URL` doit être définie

### Configuration Vérifiée

✅ **Tâche de compostage** : Tous les lundis à 3h UTC
- Fichier : `backend/config/celery.py`
- Tâche : `core.tasks.saka_run_compost_cycle`
- Condition : `SAKA_COMPOST_ENABLED=True`

✅ **Tâche de redistribution** : Le 1er de chaque mois à 4h UTC
- Fichier : `backend/config/celery.py`
- Tâche : `core.tasks.run_saka_silo_redistribution`
- Condition : `SAKA_SILO_REDIS_ENABLED=True`

### Vérifier que Celery Beat est actif

**Dans Railway** :
1. Vérifier qu'un service **Celery Beat** est déployé
2. Vérifier les logs pour confirmer que Beat démarre
3. Chercher dans les logs : `beat: Starting...`

**Commande de vérification locale** :
```bash
# Vérifier que Celery Beat peut démarrer
celery -A config beat --loglevel=info
```

---

## 🔴 ÉTAPE 3 : Test Dry-Run (RECOMMANDÉ)

### Avant d'activer en production, tester en dry-run

```bash
# Se connecter au service backend
# Exécuter manuellement la tâche de compostage en dry-run
python manage.py shell
```

```python
from core.tasks import saka_run_compost_cycle

# Exécuter en dry-run (ne modifie pas les données)
result = saka_run_compost_cycle.delay(True)  # True = dry_run
print(result.get())
```

**Résultat attendu** :
```python
{
    'total_wallets_checked': X,
    'total_composted': 0,  # 0 en dry-run
    'dry_run': True
}
```

---

## 🔴 ÉTAPE 4 : Activation Progressive

### Phase 1 : Activer ENABLE_SAKA uniquement

1. Activer `ENABLE_SAKA=True`
2. Vérifier que les utilisateurs peuvent récolter/planter SAKA
3. Vérifier que `/api/impact/global-assets/` expose le solde SAKA
4. Attendre 24h et vérifier les logs

### Phase 2 : Activer le compostage

1. Activer `SAKA_COMPOST_ENABLED=True`
2. Vérifier que la tâche Celery est planifiée
3. Attendre le prochain lundi à 3h UTC (ou déclencher manuellement)
4. Vérifier les logs de compostage

### Phase 3 : Activer la redistribution

1. Activer `SAKA_SILO_REDIS_ENABLED=True`
2. Vérifier que la tâche est planifiée
3. Attendre le 1er du mois à 4h UTC (ou déclencher manuellement)
4. Vérifier les logs de redistribution

---

## 🔴 ÉTAPE 5 : Monitoring Initial

### Logs à surveiller

1. **Compostage** :
   ```
   [SAKA COMPOST] Total wallets checked: X
   [SAKA COMPOST] Total composted: Y SAKA
   [SAKA COMPOST] Silo balance increased: Y SAKA
   ```

2. **Redistribution** :
   ```
   [SAKA REDIST] Total redistributed: X SAKA
   [SAKA REDIST] Wallets credited: Y
   [SAKA REDIST] Silo balance decreased: X SAKA
   ```

### Métriques à suivre

- Nombre de wallets compostés par cycle
- Montant total composté
- Montant redistribué
- Nombre de wallets crédités

---

## ⚠️ Points d'Attention

### Erreurs Communes

1. **Celery Beat non actif** : Les tâches ne s'exécuteront jamais
2. **Redis non accessible** : Les tâches échoueront
3. **Variables mal définies** : Vérifier que `True` est bien une chaîne, pas un booléen
4. **Redémarrage oublié** : Les variables ne sont pas prises en compte sans redémarrage

### Rollback

Si quelque chose ne va pas :

1. Désactiver les feature flags :
   ```
   ENABLE_SAKA=False
   SAKA_COMPOST_ENABLED=False
   SAKA_SILO_REDIS_ENABLED=False
   ```

2. Redémarrer le service

3. Les données déjà compostées/redistribuées restent (c'est normal, c'est irréversible par design)

---

## ✅ Validation Finale

- [ ] Variables d'environnement définies
- [ ] Service redémarré
- [ ] Celery Beat actif
- [ ] Test dry-run réussi
- [ ] Monitoring configuré
- [ ] Logs vérifiés après premier cycle

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Prêt pour activation

