# ❓ FAQ - EGOEJO Code-Enforced

**Date** : 17 Décembre 2025  
**Objectif** : Expliquer publiquement que EGOEJO est "Code-Enforced"

---

## 🤔 Qu'est-ce que "Code-Enforced" ?

**Code-Enforced** signifie que les règles et principes d'EGOEJO ne sont pas seulement des promesses marketing, mais des **contraintes logicielles vérifiables dans le code source**.

Cela signifie que :
- ✅ Les règles sont **implémentées dans le code**
- ✅ Les règles sont **testées automatiquement**
- ✅ Les règles sont **vérifiables** par n'importe qui (code open source)
- ✅ Les règles **ne peuvent pas être contournées** sans modifier le code

---

## 🔒 Quelles Règles sont Code-Enforced ?

### 1. Anti-Accumulation

**Règle** : Le SAKA ne peut pas être accumulé indéfiniment sans conséquence.

**Code-Enforced** :
- Le compostage progressif (10% après 90 jours d'inactivité) est **automatique**
- La tâche Celery s'exécute **tous les lundis à 3h UTC**
- Les tests vérifient que **aucun solde ne reste bloqué éternellement**

**Fichiers** :
- `backend/core/services/saka.py` : Service de compostage
- `backend/core/tasks.py` : Tâche Celery automatique
- `backend/core/tests_saka_philosophy.py` : Tests philosophiques

### 2. Circulation de la Valeur

**Règle** : Toute valeur inactive doit retourner au commun (Silo).

**Code-Enforced** :
- Le compostage **retourne automatiquement** le SAKA au Silo Commun
- La redistribution **redistribue automatiquement** le Silo aux wallets actifs
- Les tests vérifient que **le Silo reçoit effectivement** la valeur compostée

**Fichiers** :
- `backend/core/services/saka.py` : Services de compostage et redistribution
- `backend/core/tests_saka_philosophy.py` : Tests de circulation

### 3. Transparence

**Règle** : Les cycles SAKA doivent être visibles et compréhensibles.

**Code-Enforced** :
- Les cycles SAKA sont **exposés via l'API** (`/api/saka/cycles/`)
- Le Silo Commun est **exposé via l'API** (`/api/saka/silo/`)
- Les données sont **affichées dans l'interface utilisateur**

**Fichiers** :
- `backend/core/api/saka_views.py` : Endpoints API
- `frontend/frontend/src/pages/SakaSeasons.tsx` : Interface utilisateur

### 4. Non-Spéculation

**Règle** : Le SAKA ne peut pas être échangé contre de l'argent.

**Code-Enforced** :
- Aucun endpoint API ne permet d'**échanger SAKA contre EUR**
- Les tests vérifient que **le SAKA reste séparé** de l'argent
- La structure économique est **double** (Instrumental: EUR, Relational: SAKA)

**Fichiers** :
- `backend/core/services/saka.py` : Services SAKA (pas d'échange)
- `backend/core/tests_saka_philosophy.py` : Tests de séparation

---

## 🧪 Comment Vérifier que c'est Code-Enforced ?

### 1. Vérifier les Tests

Tous les principes philosophiques sont testés dans `backend/core/tests_saka_philosophy.py` :

```bash
# Exécuter les tests philosophiques
python -m pytest backend/core/tests_saka_philosophy.py -v
```

**Résultat attendu** : Tous les tests passent (14 tests)

### 2. Vérifier le Code

Les règles sont implémentées dans le code source :

```python
# Exemple : Compostage automatique
# backend/core/services/saka.py
def run_saka_compost_cycle(dry_run=False, source="celery"):
    # Sélectionner les wallets inactifs
    qs = SakaWallet.objects.select_for_update().filter(
        last_activity_date__lt=cutoff,
        balance__gte=min_balance,
    )
    # Composter 10% du solde
    amount = int(floor(wallet.balance * rate))
    # Retourner au Silo
    silo.total_balance += amount
```

### 3. Vérifier les Tâches Automatiques

Les tâches Celery s'exécutent automatiquement :

```python
# backend/config/celery.py
app.conf.beat_schedule = {
    'saka-compost-cycle': {
        'task': 'core.tasks.saka_run_compost_cycle',
        'schedule': crontab(hour=3, minute=0, day_of_week=1),  # Tous les lundis
    },
}
```

---

## 🔍 Où Trouver le Code ?

### Repository GitHub

Le code source est disponible sur GitHub :
- **Backend** : `backend/core/services/saka.py`
- **Tests** : `backend/core/tests_saka_philosophy.py`
- **API** : `backend/core/api/saka_views.py`
- **Frontend** : `frontend/frontend/src/pages/SakaSeasons.tsx`

### Documentation

- **Philosophie** : `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md`
- **Tests** : `docs/reports/RESOLUTION_FINALE_TESTS_COMPOSTAGE_2025-12-17.md`
- **Activation** : `docs/deployment/GUIDE_ACTIVATION_FEATURE_FLAGS.md`

---

## ❓ Questions Fréquentes

### Q: Est-ce que les règles peuvent être modifiées ?

**R** : Oui, mais toute modification doit :
1. Passer les tests philosophiques
2. Être documentée publiquement
3. Être validée par la communauté

### Q: Comment savoir si les règles sont respectées en production ?

**R** : 
1. Vérifier les logs de compostage (tous les lundis)
2. Vérifier les logs de redistribution (1er du mois)
3. Vérifier l'API `/api/saka/silo/` pour voir le solde du Silo
4. Vérifier les tests E2E qui vérifient l'affichage des cycles

### Q: Que se passe-t-il si une règle est violée ?

**R** : 
- Les tests échouent (détection automatique)
- Les logs montrent l'erreur
- L'équipe technique est alertée
- Une correction est déployée

### Q: Les règles sont-elles vraiment automatiques ?

**R** : Oui, les règles sont exécutées automatiquement par :
- **Celery Beat** : Tâches périodiques (compostage, redistribution)
- **Services Django** : Logique métier (récolte, plantation)
- **Tests** : Vérification continue

---

## 📚 Ressources

- **Code Source** : [GitHub Repository](https://github.com/tresorkazama-design/egoejo)
- **Documentation** : `docs/architecture/PROTOCOLE_SAKA_PHILOSOPHIE.md`
- **Tests** : `backend/core/tests_saka_philosophy.py`
- **API** : `/api/saka/cycles/`, `/api/saka/silo/`

---

**Date de création** : 17 Décembre 2025  
**Statut** : ✅ FAQ publique

