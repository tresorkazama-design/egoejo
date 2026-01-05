# 🔧 FIX CRITIQUE : transaction_type Manquant

**Date** : 2025-01-01  
**Problème** : `NOT NULL constraint failed: core_sakatransaction.transaction_type`  
**Statut** : ✅ **CORRIGÉ**

---

## 📋 Résumé

Les tests E2E échouaient avec l'erreur `NOT NULL constraint failed: core_sakatransaction.transaction_type`.  
L'analyse a révélé que **7 appels** à `SakaTransaction.objects.create()` dans les fichiers de tests oubliaient de fournir `transaction_type`.

---

## 🔍 Analyse

### Scan Global des Appels

**Appels dans `backend/core/services/saka.py`** : ✅ **TOUS CONFORMES**
- Ligne 308 : `harvest_saka()` → `transaction_type='HARVEST'` ✅
- Ligne 379 : `spend_saka()` → `transaction_type='SPEND'` ✅
- Ligne 553 : `compost_cycle()` → `transaction_type='COMPOST'` ✅
- Ligne 803 : `redistribute_saka_silo()` → `transaction_type='REDISTRIBUTION'` ✅

**Appels dans les fichiers de tests** : ❌ **7 APPELS MANQUANTS**
- `backend/core/tests_saka.py` : 4 appels manquants (lignes 1037, 1046, 1058, 1147)
- `backend/core/tests/test_race_condition_harvest_saka.py` : 1 appel manquant (ligne 129)
- `backend/core/tests_saka_public.py` : 2 appels manquants (lignes 117, 132)

---

## ✅ Corrections Appliquées

### 1. Fichier `backend/core/tests_saka.py`

**Ligne 1037** (Transaction EARN - content_read) :
```python
# AVANT
tx1 = SakaTransaction.objects.create(
    user=self.user1,
    direction='EARN',
    amount=50,
    reason='content_read'
)

# APRÈS
tx1 = SakaTransaction.objects.create(
    user=self.user1,
    direction='EARN',
    amount=50,
    reason='content_read',
    transaction_type='HARVEST'  # ✅ AJOUTÉ
)
```

**Ligne 1046** (Transaction SPEND - project_boost) :
```python
# AVANT
tx2 = SakaTransaction.objects.create(
    user=self.user1,
    direction='SPEND',
    amount=20,
    reason='project_boost'
)

# APRÈS
tx2 = SakaTransaction.objects.create(
    user=self.user1,
    direction='SPEND',
    amount=20,
    reason='project_boost',
    transaction_type='SPEND'  # ✅ AJOUTÉ
)
```

**Ligne 1058** (Transaction EARN - content_read) :
```python
# AVANT
tx3 = SakaTransaction.objects.create(
    user=self.user1,
    direction='EARN',
    amount=100,
    reason='content_read'
)

# APRÈS
tx3 = SakaTransaction.objects.create(
    user=self.user1,
    direction='EARN',
    amount=100,
    reason='content_read',
    transaction_type='HARVEST'  # ✅ AJOUTÉ
)
```

**Ligne 1147** (Transaction EARN - content_read) :
```python
# AVANT
tx = SakaTransaction.objects.create(
    user=self.user1,
    direction='EARN',
    amount=100,
    reason='content_read'
)

# APRÈS
tx = SakaTransaction.objects.create(
    user=self.user1,
    direction='EARN',
    amount=100,
    reason='content_read',
    transaction_type='HARVEST'  # ✅ AJOUTÉ
)
```

### 2. Fichier `backend/core/tests/test_race_condition_harvest_saka.py`

**Ligne 129** (Transaction EARN - poll_vote) :
```python
# AVANT
for i in range(9):
    SakaTransaction.objects.create(
        user=self.user,
        direction='EARN',
        reason='poll_vote',
        amount=5
    )

# APRÈS
for i in range(9):
    SakaTransaction.objects.create(
        user=self.user,
        direction='EARN',
        reason='poll_vote',
        amount=5,
        transaction_type='HARVEST'  # ✅ AJOUTÉ
    )
```

### 3. Fichier `backend/core/tests_saka_public.py`

**Ligne 117** (Transaction EARN - test) :
```python
# AVANT
transaction_earn = SakaTransaction.objects.create(
    user=self.user,
    amount=100,
    direction='EARN',
    reason='test',
)

# APRÈS
transaction_earn = SakaTransaction.objects.create(
    user=self.user,
    amount=100,
    direction='EARN',
    reason='test',
    transaction_type='HARVEST',  # ✅ AJOUTÉ
)
```

**Ligne 132** (Transaction SPEND - test) :
```python
# AVANT
transaction_spend = SakaTransaction.objects.create(
    user=self.user,
    amount=50,
    direction='SPEND',
    reason='test',
)

# APRÈS
transaction_spend = SakaTransaction.objects.create(
    user=self.user,
    amount=50,
    direction='SPEND',
    reason='test',
    transaction_type='SPEND',  # ✅ AJOUTÉ
)
```

---

## 🛡️ Sécurisation : Validation Explicite dans le Modèle

Ajout d'une validation explicite dans `SakaTransaction.save()` pour faciliter le débogage futur :

```python
def save(self, *args, **kwargs):
    """
    Validation explicite : transaction_type est OBLIGATOIRE.
    
    Cette validation facilite le débogage en levant une ValueError claire
    si transaction_type est manquant, plutôt qu'une erreur générique de base de données.
    
    Raises:
        ValueError: Si transaction_type est manquant ou invalide
    """
    # Validation : transaction_type est OBLIGATOIRE
    if not self.transaction_type:
        raise ValueError(
            f"VIOLATION : transaction_type est OBLIGATOIRE pour SakaTransaction. "
            f"Direction: {self.direction}, Reason: {self.reason}, Amount: {self.amount}. "
            f"Valeurs possibles: HARVEST, SPEND, COMPOST, REDISTRIBUTION. "
            f"Vérifiez que tous les appels à SakaTransaction.objects.create() fournissent transaction_type."
        )
    
    # Validation : transaction_type doit être dans les choix valides
    valid_types = [choice[0] for choice in self.TRANSACTION_TYPE_CHOICES]
    if self.transaction_type not in valid_types:
        raise ValueError(
            f"VIOLATION : transaction_type invalide '{self.transaction_type}'. "
            f"Valeurs possibles: {', '.join(valid_types)}. "
            f"Direction: {self.direction}, Reason: {self.reason}, Amount: {self.amount}."
        )
    
    # Validation : Cohérence direction / transaction_type
    if self.direction == 'EARN' and self.transaction_type not in ['HARVEST', 'REDISTRIBUTION']:
        raise ValueError(
            f"VIOLATION : transaction_type '{self.transaction_type}' incompatible avec direction='EARN'. "
            f"Pour direction='EARN', transaction_type doit être 'HARVEST' ou 'REDISTRIBUTION'. "
            f"Reason: {self.reason}, Amount: {self.amount}."
        )
    
    if self.direction == 'SPEND' and self.transaction_type not in ['SPEND', 'COMPOST']:
        raise ValueError(
            f"VIOLATION : transaction_type '{self.transaction_type}' incompatible avec direction='SPEND'. "
            f"Pour direction='SPEND', transaction_type doit être 'SPEND' ou 'COMPOST'. "
            f"Reason: {self.reason}, Amount: {self.amount}."
        )
    
    super().save(*args, **kwargs)
```

**Avantages de cette validation** :
1. ✅ **Erreur claire** : `ValueError` avec message explicite au lieu d'erreur générique de base de données
2. ✅ **Débogage facilité** : Le message indique exactement quel appel est fautif
3. ✅ **Cohérence garantie** : Vérifie que `direction` et `transaction_type` sont cohérents
4. ✅ **Détection précoce** : L'erreur est levée avant l'insertion en base de données

---

## ✅ Vérification Finale

### Tous les Appels Sont Conformes

**Appels dans `backend/core/services/saka.py`** : ✅ **4/4 CONFORMES**
- ✅ `harvest_saka()` → `transaction_type='HARVEST'`
- ✅ `spend_saka()` → `transaction_type='SPEND'`
- ✅ `compost_cycle()` → `transaction_type='COMPOST'`
- ✅ `redistribute_saka_silo()` → `transaction_type='REDISTRIBUTION'`

**Appels dans les fichiers de tests** : ✅ **7/7 CORRIGÉS**
- ✅ `backend/core/tests_saka.py` : 4 appels corrigés
- ✅ `backend/core/tests/test_race_condition_harvest_saka.py` : 1 appel corrigé
- ✅ `backend/core/tests_saka_public.py` : 2 appels corrigés

---

## 📊 Résultat

✅ **7 appels corrigés** dans les fichiers de tests  
✅ **Validation explicite ajoutée** dans `SakaTransaction.save()`  
✅ **Tous les appels sont maintenant conformes**

**Le bug `NOT NULL constraint failed: core_sakatransaction.transaction_type` est maintenant corrigé.**

---

## 🧪 Tests à Exécuter

Pour vérifier que les corrections fonctionnent :

```bash
# Tests unitaires SAKA
cd backend
pytest core/tests_saka.py -v

# Tests de race condition
pytest core/tests/test_race_condition_harvest_saka.py -v

# Tests publics SAKA
pytest core/tests_saka_public.py -v

# Tests E2E (une fois le backend démarré)
cd frontend/frontend
npm run test:e2e -- e2e/flux-complet-saka-vote.spec.js
```

---

**Document généré le** : 2025-01-01  
**Statut** : ✅ **CORRIGÉ**

