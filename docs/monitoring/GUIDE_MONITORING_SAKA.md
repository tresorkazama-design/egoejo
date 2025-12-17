# 📊 Guide de Monitoring - Protocole SAKA

**Date** : 17 Décembre 2025  
**Objectif** : Monitorer l'exécution du protocole SAKA en production

---

## 🔍 Logs à Surveiller

### 1. Compostage (Tous les lundis à 3h UTC)

**Logs de succès** :
```
[SAKA COMPOST] Cycle démarré
[SAKA COMPOST] Wallets inactifs trouvés: X
[SAKA COMPOST] Total composté: Y SAKA
[SAKA COMPOST] Silo balance: Z SAKA (avant) → Z+Y SAKA (après)
[SAKA COMPOST] Cycle terminé avec succès
```

**Logs d'erreur** :
```
[SAKA COMPOST] ERREUR: Exception lors du compostage
[SAKA COMPOST] ERREUR: Redis non accessible
[SAKA COMPOST] ERREUR: Transaction échouée
```

### 2. Redistribution (1er du mois à 4h UTC)

**Logs de succès** :
```
[SAKA REDIST] Redistribution démarrée
[SAKA REDIST] Silo balance: X SAKA
[SAKA REDIST] Montant à redistribuer: Y SAKA (5%)
[SAKA REDIST] Wallets éligibles: Z
[SAKA REDIST] Montant par wallet: W SAKA
[SAKA REDIST] Redistribution terminée avec succès
```

**Logs d'erreur** :
```
[SAKA REDIST] ERREUR: Silo vide
[SAKA REDIST] ERREUR: Aucun wallet éligible
[SAKA REDIST] ERREUR: Transaction échouée
```

### 3. Tâches Celery

**Logs de démarrage** :
```
[celery.beat] beat: Starting...
[celery.beat] Scheduler: Sending due task saka-compost-cycle
[celery.beat] Scheduler: Sending due task saka-silo-redistribution
```

**Logs d'exécution** :
```
[celery.worker] Task core.tasks.saka_run_compost_cycle[xxx] received
[celery.worker] Task core.tasks.saka_run_compost_cycle[xxx] succeeded
```

---

## 📈 Métriques à Suivre

### Métriques de Compostage

1. **Nombre de wallets compostés** : `SakaCompostLog.objects.count()`
2. **Montant total composté** : `SakaSilo.objects.first().total_composted`
3. **Solde actuel du Silo** : `SakaSilo.objects.first().total_balance`
4. **Dernier cycle** : `SakaSilo.objects.first().last_compost_at`

### Métriques de Redistribution

1. **Montant redistribué** : Somme des transactions `REDISTRIBUTION`
2. **Nombre de wallets crédités** : Nombre de transactions `REDISTRIBUTION`
3. **Solde du Silo après redistribution** : `SakaSilo.objects.first().total_balance`

### Métriques Globales SAKA

1. **Total récolté** : `SakaWallet.objects.aggregate(Sum('total_harvested'))`
2. **Total planté** : `SakaWallet.objects.aggregate(Sum('total_planted'))`
3. **Total composté** : `SakaWallet.objects.aggregate(Sum('total_composted'))`
4. **Nombre de wallets actifs** : `SakaWallet.objects.filter(balance__gt=0).count()`

---

## 🚨 Alertes à Configurer

### Alertes Critiques

1. **Celery Beat inactif** :
   - Condition : Pas de log "beat: Starting..." depuis 1h
   - Action : Alerter l'équipe technique

2. **Échec de compostage** :
   - Condition : Exception dans les logs de compostage
   - Action : Alerter immédiatement, vérifier les logs

3. **Échec de redistribution** :
   - Condition : Exception dans les logs de redistribution
   - Action : Alerter immédiatement, vérifier les logs

4. **Redis inaccessible** :
   - Condition : Erreur de connexion Redis
   - Action : Alerter immédiatement, vérifier la configuration

### Alertes de Performance

1. **Compostage trop long** :
   - Condition : Durée d'exécution > 60 secondes
   - Action : Vérifier le nombre de wallets, optimiser si nécessaire

2. **Silo trop plein** :
   - Condition : `total_balance > 100000` SAKA
   - Action : Vérifier que la redistribution fonctionne

3. **Aucun compostage** :
   - Condition : Aucun wallet composté depuis 2 cycles
   - Action : Vérifier la logique de compostage

---

## 📊 Dashboard de Monitoring (À Créer)

### Vue d'Ensemble

- **Solde actuel du Silo** : Graphique en temps réel
- **Compostage** : Graphique des cycles (montant composté par cycle)
- **Redistribution** : Graphique des redistributions (montant redistribué)
- **Wallets actifs** : Nombre de wallets avec balance > 0

### Vue Détail Compostage

- Liste des derniers cycles
- Montant composté par cycle
- Nombre de wallets compostés
- Wallets les plus compostés

### Vue Détail Redistribution

- Liste des dernières redistributions
- Montant redistribué
- Nombre de wallets crédités
- Distribution par wallet

---

## 🔧 Commandes de Diagnostic

### Vérifier l'état du Silo

```python
from core.models.saka import SakaSilo

silo = SakaSilo.objects.first()
print(f"Solde: {silo.total_balance} SAKA")
print(f"Total composté: {silo.total_composted} SAKA")
print(f"Dernier compost: {silo.last_compost_at}")
```

### Vérifier les derniers compostages

```python
from core.models.saka import SakaCompostLog

logs = SakaCompostLog.objects.order_by('-created_at')[:10]
for log in logs:
    print(f"{log.created_at}: {log.amount} SAKA compostés de {log.wallet.user.username}")
```

### Vérifier les tâches Celery

```bash
# Vérifier les tâches en attente
celery -A config inspect active

# Vérifier les tâches planifiées
celery -A config inspect scheduled

# Vérifier les workers
celery -A config inspect stats
```

---

## 📝 Rapport Hebdomadaire (Recommandé)

### Contenu du Rapport

1. **Résumé** :
   - Nombre de cycles de compostage exécutés
   - Montant total composté
   - Montant total redistribué

2. **Métriques** :
   - Solde actuel du Silo
   - Nombre de wallets actifs
   - Taux de compostage moyen

3. **Incidents** :
   - Erreurs rencontrées
   - Actions correctives prises

4. **Tendances** :
   - Évolution du solde du Silo
   - Évolution du nombre de wallets actifs

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ Guide de référence

