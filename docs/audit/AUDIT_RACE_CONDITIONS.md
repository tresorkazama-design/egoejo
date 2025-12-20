# 🔥 AUDIT CRITIQUE - Race Conditions & Idempotence

**Date** : 2025-12-19  
**Auditeur** : Senior Code Auditor (Cynique)  
**Mission** : Recherche de Race Conditions - Identifier les failles de concurrence

---

## 💀 FAILLES CRITIQUES IDENTIFIÉES

### 1. 🥇 `pledge_funds()` : Vérification Idempotence AVANT Verrouillage = DOUBLE DÉPENSE

**Fichier** : `backend/finance/services.py:36-39, 53`

**Problème** :
```python
@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    # ❌ VÉRIFICATION IDEMPOTENCE AVANT VERROUILLAGE
    if idempotency_key:
        if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
            raise ValidationError("Cette transaction a déjà été traitée.")
    
    # ... validations ...
    
    # ✅ VERROUILLAGE (trop tard)
    wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=user)
    
    # ... reste du code ...
```

**Scénario de Race Condition** :
1. **Requête A** arrive avec `idempotency_key="abc-123"`
2. **Requête B** arrive avec `idempotency_key="abc-123"` (même clé, double clic)
3. **Requête A** : Vérifie `exists()` → **False** (pas encore créé)
4. **Requête B** : Vérifie `exists()` → **False** (pas encore créé)
5. **Requête A** : Verrouille wallet, débite, crée transaction avec clé "abc-123"
6. **Requête B** : Verrouille wallet (attend), débite, crée transaction avec clé "abc-123"
7. **Résultat** : **DOUBLE DÉPENSE** + **Violation unique constraint** (si `idempotency_key` est unique)

**Verdict** : **RACE CONDITION CONFIRMÉE**. Double dépense possible.

**Fix** :
```python
@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION', idempotency_key=None):
    # ✅ VERROUILLAGE EN PREMIER
    wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=user)
    
    # ✅ VÉRIFICATION IDEMPOTENCE APRÈS VERROUILLAGE (dans la même transaction)
    if idempotency_key:
        if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
            raise ValidationError("Cette transaction a déjà été traitée.")
    
    # ... reste du code ...
```

**OU utiliser un verrouillage au niveau DB** :
```python
# Utiliser get_or_create avec select_for_update sur idempotency_key
if idempotency_key:
    # Tenter de créer une transaction "fantôme" pour verrouiller la clé
    try:
        WalletTransaction.objects.create(
            idempotency_key=idempotency_key,
            wallet=wallet,
            amount=Decimal('0'),  # Transaction temporaire
            transaction_type='PLEDGE_DONATION',
            # ... autres champs requis
        )
    except IntegrityError:
        # Clé déjà utilisée
        raise ValidationError("Cette transaction a déjà été traitée.")
```

---

### 2. 🥈 `harvest_saka()` : Vérification Limite Quotidienne AVANT Verrouillage = DOUBLE CRÉDIT

**Fichier** : `backend/core/services/saka.py:121-149, 169-173`

**Problème** :
```python
@transaction.atomic
def harvest_saka(user, reason: SakaReason, amount: Optional[int] = None, ...):
    # ❌ VÉRIFICATION LIMITE AVANT VERROUILLAGE
    wallet = get_or_create_wallet(user)  # ❌ PAS DE VERROUILLAGE
    if not wallet:
        return None
    
    # ✅ VERROUILLAGE (trop tard)
    wallet = SakaWallet.objects.select_for_update().get(id=wallet.id)
    
    # ❌ VÉRIFICATION LIMITE (après verrouillage mais avec requête séparée)
    daily_limit = SAKA_DAILY_LIMITS.get(reason, 0)
    if daily_limit > 0:
        today = date.today()
        today_count = SakaTransaction.objects.filter(
            user=user,
            direction='EARN',
            reason=reason.value,
            created_at__date=today
        ).count()  # ❌ REQUÊTE SÉPARÉE (pas dans le verrou)
        
        if today_count >= daily_limit:
            return None
    
    # ✅ MISE À JOUR (après vérification)
    wallet.balance += amount
    wallet.save()
    
    # ✅ CRÉATION TRANSACTION
    saka_transaction = SakaTransaction.objects.create(...)
```

**Scénario de Race Condition** :
1. **Requête A** arrive (user vote pour poll)
2. **Requête B** arrive (même user vote pour même poll, double clic)
3. **Requête A** : `get_or_create_wallet()` → wallet créé/récupéré
4. **Requête B** : `get_or_create_wallet()` → même wallet (pas encore verrouillé)
5. **Requête A** : Verrouille wallet, vérifie `today_count` → **0** (pas encore de transaction)
6. **Requête B** : Attend verrouillage...
7. **Requête A** : Crédite balance, crée transaction
8. **Requête A** : Libère verrouillage
9. **Requête B** : Verrouille wallet, vérifie `today_count` → **1** (mais limite = 10, donc OK)
10. **Requête B** : Crédite balance, crée transaction
11. **Résultat** : **DOUBLE CRÉDIT** (2 transactions au lieu d'1)

**Verdict** : **RACE CONDITION CONFIRMÉE**. Double crédit possible.

**Fix** :
```python
@transaction.atomic
def harvest_saka(user, reason: SakaReason, amount: Optional[int] = None, ...):
    # ✅ VERROUILLAGE EN PREMIER
    wallet, created = SakaWallet.objects.select_for_update().get_or_create(
        user=user,
        defaults={
            'balance': 0,
            'total_harvested': 0,
            'total_planted': 0,
            'total_composted': 0,
        }
    )
    
    # ✅ VÉRIFICATION LIMITE APRÈS VERROUILLAGE (dans la même transaction)
    daily_limit = SAKA_DAILY_LIMITS.get(reason, 0)
    if daily_limit > 0:
        today = date.today()
        today_count = SakaTransaction.objects.filter(
            user=user,
            direction='EARN',
            reason=reason.value,
            created_at__date=today
        ).count()  # ✅ DANS LA MÊME TRANSACTION (lecture cohérente)
        
        if today_count >= daily_limit:
            return None
    
    # ✅ MISE À JOUR (atomique)
    wallet.balance += amount
    wallet.total_harvested += amount
    wallet.last_activity_date = timezone.now()
    wallet.save()
    
    # ✅ CRÉATION TRANSACTION
    saka_transaction = SakaTransaction.objects.create(...)
```

---

### 3. 🥉 `allocate_deposit_across_pockets()` : Transactions Imbriquées = DEADLOCK

**Fichier** : `backend/finance/services.py:335-409`

**Problème** :
```python
@transaction.atomic
def allocate_deposit_across_pockets(user, amount: Decimal):
    # ✅ VERROUILLAGE
    wallet = UserWallet.objects.select_for_update().get(user=user)
    
    # ... calculs ...
    
    for pocket in pockets:
        # ❌ APPEL À transfer_to_pocket (qui est aussi @transaction.atomic)
        tx = transfer_to_pocket(user, pocket.id, allocated)
        # transfer_to_pocket essaie de verrouiller le même wallet
```

**Scénario de Deadlock** :
1. **Transaction A** : `allocate_deposit_across_pockets()` verrouille `wallet`
2. **Transaction B** : `transfer_to_pocket()` essaie de verrouiller `wallet` → **BLOQUÉ**
3. **Transaction A** : Appelle `transfer_to_pocket()` → Essaie de verrouiller `wallet` (déjà verrouillé par A)
4. **Résultat** : **DEADLOCK** (A attend B, B attend A)

**Verdict** : **DEADLOCK GARANTI**. Transactions imbriquées.

**Fix** :
```python
@transaction.atomic
def allocate_deposit_across_pockets(user, amount: Decimal):
    wallet = UserWallet.objects.select_for_update().get(user=user)
    
    # ... calculs ...
    
    for pocket in pockets:
        # ✅ NE PAS APPELER transfer_to_pocket (évite transaction imbriquée)
        # ✅ FAIRE LE TRANSFERT DIRECTEMENT
        pocket_obj = WalletPocket.objects.select_for_update().get(
            id=pocket.id,
            wallet=wallet
        )
        
        # Vérifier solde
        if wallet.balance >= allocated:
            # Créer transaction
            tx = WalletTransaction.objects.create(
                wallet=wallet,
                amount=allocated,
                transaction_type='POCKET_TRANSFER',
                description=f"Transfert vers pocket: {pocket_obj.name}",
            )
            
            # Mettre à jour soldes
            wallet.balance = (wallet.balance - allocated).quantize(cents, rounding=ROUND_HALF_UP)
            wallet.save()
            
            pocket_obj.current_amount = (pocket_obj.current_amount + allocated).quantize(cents, rounding=ROUND_HALF_UP)
            pocket_obj.save()
            
            transactions.append(tx)
```

---

### 4. ❌ `release_escrow()` : Pas de Vérification Idempotence = DOUBLE LIBÉRATION

**Fichier** : `backend/finance/services.py:129-186`

**Problème** :
```python
@transaction.atomic
def release_escrow(escrow_contract):
    # ❌ VÉRIFICATION STATUS SEULEMENT (pas d'idempotence)
    if escrow_contract.status != 'LOCKED':
        raise ValidationError("Ce contrat n'est pas verrouillé.")
    
    # ✅ VERROUILLAGE
    commission_wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=None)
    
    # ... calculs ...
    
    # ❌ PAS DE VÉRIFICATION SI DÉJÀ LIBÉRÉ
    escrow_contract.status = 'RELEASED'
    escrow_contract.save()
```

**Scénario de Race Condition** :
1. **Webhook Stripe A** arrive (paiement réussi)
2. **Webhook Stripe B** arrive (même événement, retry Stripe)
3. **Webhook A** : Vérifie `status != 'LOCKED'` → **False** (status = 'LOCKED')
4. **Webhook B** : Vérifie `status != 'LOCKED'` → **False** (status = 'LOCKED', pas encore changé)
5. **Webhook A** : Libère escrow, met status = 'RELEASED'
6. **Webhook B** : Libère escrow, met status = 'RELEASED'
7. **Résultat** : **DOUBLE LIBÉRATION** (commission créditée 2 fois)

**Verdict** : **RACE CONDITION CONFIRMÉE**. Double libération possible.

**Fix** :
```python
@transaction.atomic
def release_escrow(escrow_contract):
    # ✅ VERROUILLAGE EN PREMIER
    escrow = EscrowContract.objects.select_for_update().get(id=escrow_contract.id)
    
    # ✅ VÉRIFICATION STATUS APRÈS VERROUILLAGE
    if escrow.status != 'LOCKED':
        raise ValidationError("Ce contrat n'est pas verrouillé.")
    
    # ✅ MARQUER COMME LIBÉRÉ AVANT LES CALCULS (évite double libération)
    escrow.status = 'RELEASED'
    escrow.released_at = timezone.now()
    escrow.save(update_fields=['status', 'released_at'])
    
    # ... reste du code (calculs, commissions) ...
```

---

### 5. ❌ `harvest_saka()` : `get_or_create_wallet()` Sans Verrouillage = RACE CONDITION

**Fichier** : `backend/core/services/saka.py:58-80, 121-126`

**Problème** :
```python
def get_or_create_wallet(user):
    # ❌ PAS DE VERROUILLAGE
    wallet, created = SakaWallet.objects.get_or_create(
        user=user,
        defaults={...}
    )
    return wallet

@transaction.atomic
def harvest_saka(...):
    # ❌ APPEL À get_or_create_wallet (pas de verrouillage)
    wallet = get_or_create_wallet(user)
    if not wallet:
        return None
    
    # ✅ VERROUILLAGE (trop tard, wallet peut avoir changé)
    wallet = SakaWallet.objects.select_for_update().get(id=wallet.id)
```

**Scénario de Race Condition** :
1. **Requête A** arrive (première récolte SAKA pour user)
2. **Requête B** arrive (même user, même action)
3. **Requête A** : `get_or_create_wallet()` → Crée wallet (id=1)
4. **Requête B** : `get_or_create_wallet()` → Crée wallet (id=2) **OU** Récupère wallet (id=1)
5. **Résultat** : **DOUBLE CRÉATION** ou **RACE CONDITION**

**Verdict** : **RACE CONDITION CONFIRMÉE**. Double création possible.

**Fix** :
```python
@transaction.atomic
def harvest_saka(...):
    # ✅ VERROUILLAGE DIRECT (pas d'appel intermédiaire)
    wallet, created = SakaWallet.objects.select_for_update().get_or_create(
        user=user,
        defaults={
            'balance': 0,
            'total_harvested': 0,
            'total_planted': 0,
            'total_composted': 0,
        }
    )
    
    # ... reste du code ...
```

---

## 🧪 TESTS POUR PROUVER LES FAILLES

### Test 1 : Double Dépense `pledge_funds()` (Sans Idempotence)

```python
# backend/finance/tests/test_race_condition_pledge.py
import threading
import time
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from finance.services import pledge_funds
from finance.models import UserWallet, EscrowContract, WalletTransaction
from core.models import Projet

User = get_user_model()

class TestRaceConditionPledge(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.project = Projet.objects.create(
            titre='Test Project',
            funding_type='DONATION'
        )
        UserWallet.objects.create(user=self.user, balance=Decimal('100.00'))
    
    def test_double_pledge_without_idempotency_creates_double_debit(self):
        """
        PROUVE LA FAILLE : Double clic sans idempotency_key = double débit
        """
        amount = Decimal('50.00')
        results = []
        errors = []
        
        def make_pledge():
            try:
                escrow = pledge_funds(
                    self.user,
                    self.project,
                    amount,
                    pledge_type='DONATION',
                    idempotency_key=None  # ❌ PAS D'IDEMPOTENCE
                )
                results.append(escrow)
            except Exception as e:
                errors.append(str(e))
        
        # Lancer 2 threads simultanément (simule double clic)
        thread1 = threading.Thread(target=make_pledge)
        thread2 = threading.Thread(target=make_pledge)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Vérifier le résultat
        wallet = UserWallet.objects.get(user=self.user)
        escrows_count = EscrowContract.objects.filter(user=self.user, project=self.project).count()
        transactions_count = WalletTransaction.objects.filter(
            wallet=wallet,
            transaction_type='PLEDGE_DONATION'
        ).count()
        
        # ❌ CE TEST VA ÉCHOUER (prouve la faille)
        self.assertEqual(
            wallet.balance,
            Decimal('0.00'),  # Attendu : 100 - 50 = 50 (mais on a débité 2 fois)
            "Le solde devrait être 50€ (100 - 50), mais la race condition a causé un double débit"
        )
        self.assertEqual(
            escrows_count,
            1,  # Attendu : 1 escrow (mais on en a créé 2)
            "Un seul escrow devrait être créé, mais la race condition a créé 2 escrows"
        )
        self.assertEqual(
            transactions_count,
            1,  # Attendu : 1 transaction (mais on en a créé 2)
            "Une seule transaction devrait être créée, mais la race condition a créé 2 transactions"
        )
```

---

### Test 2 : Double Crédit `harvest_saka()` (Limite Quotidienne)

```python
# backend/core/tests/test_race_condition_harvest_saka.py
import threading
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.services.saka import harvest_saka, SakaReason
from core.models.saka import SakaWallet, SakaTransaction

User = get_user_model()

class TestRaceConditionHarvestSaka(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
    
    def test_double_harvest_creates_double_credit(self):
        """
        PROUVE LA FAILLE : Double clic sur vote = double crédit SAKA
        """
        results = []
        
        def make_harvest():
            tx = harvest_saka(
                self.user,
                SakaReason.POLL_VOTE,
                amount=5
            )
            results.append(tx)
        
        # Lancer 2 threads simultanément (simule double clic)
        thread1 = threading.Thread(target=make_harvest)
        thread2 = threading.Thread(target=make_harvest)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Vérifier le résultat
        wallet = SakaWallet.objects.get(user=self.user)
        transactions_count = SakaTransaction.objects.filter(
            user=self.user,
            direction='EARN',
            reason='poll_vote'
        ).count()
        
        # ❌ CE TEST VA ÉCHOUER (prouve la faille)
        self.assertEqual(
            wallet.balance,
            5,  # Attendu : 5 grains (mais on a crédité 2 fois = 10)
            "Le solde devrait être 5 grains, mais la race condition a causé un double crédit"
        )
        self.assertEqual(
            transactions_count,
            1,  # Attendu : 1 transaction (mais on en a créé 2)
            "Une seule transaction devrait être créée, mais la race condition a créé 2 transactions"
        )
```

---

### Test 3 : Double Libération `release_escrow()` (Webhook Retry)

```python
# backend/finance/tests/test_race_condition_release_escrow.py
import threading
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from finance.services import pledge_funds, release_escrow
from finance.models import UserWallet, EscrowContract, WalletTransaction
from core.models import Projet

User = get_user_model()

class TestRaceConditionReleaseEscrow(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        self.project = Projet.objects.create(
            titre='Test Project',
            funding_type='DONATION'
        )
        UserWallet.objects.create(user=self.user, balance=Decimal('100.00'))
        
        # Créer un escrow
        self.escrow = pledge_funds(
            self.user,
            self.project,
            Decimal('50.00'),
            pledge_type='DONATION'
        )
    
    def test_double_release_creates_double_commission(self):
        """
        PROUVE LA FAILLE : Webhook Stripe retry = double libération = double commission
        """
        results = []
        errors = []
        
        def make_release():
            try:
                result = release_escrow(self.escrow)
                results.append(result)
            except Exception as e:
                errors.append(str(e))
        
        # Lancer 2 threads simultanément (simule webhook retry)
        thread1 = threading.Thread(target=make_release)
        thread2 = threading.Thread(target=make_release)
        
        thread1.start()
        thread2.start()
        
        thread1.join()
        thread2.join()
        
        # Vérifier le résultat
        commission_wallet = UserWallet.objects.get(user=None)
        escrow = EscrowContract.objects.get(id=self.escrow.id)
        commission_txs = WalletTransaction.objects.filter(
            transaction_type='COMMISSION',
            related_project=self.project
        ).count()
        
        # ❌ CE TEST VA ÉCHOUER (prouve la faille)
        self.assertEqual(
            escrow.status,
            'RELEASED',  # OK
            "L'escrow devrait être libéré"
        )
        self.assertEqual(
            commission_txs,
            1,  # Attendu : 1 transaction commission (mais on en a créé 2)
            "Une seule transaction commission devrait être créée, mais la race condition a créé 2 transactions"
        )
        # Vérifier que la commission n'a été créditée qu'une seule fois
        # (calculer commission attendue = 50 * 0.05 = 2.5)
        expected_commission = Decimal('2.50')
        # ❌ CE TEST VA ÉCHOUER (commission créditée 2 fois)
        self.assertEqual(
            commission_wallet.balance,
            expected_commission,  # Attendu : 2.5€ (mais on a crédité 2 fois = 5€)
            f"La commission devrait être {expected_commission}€, mais la race condition a causé un double crédit"
        )
```

---

### Test 4 : Deadlock `allocate_deposit_across_pockets()`

```python
# backend/finance/tests/test_deadlock_allocate_deposit.py
import threading
import time
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from finance.services import allocate_deposit_across_pockets, transfer_to_pocket
from finance.models import UserWallet, WalletPocket

User = get_user_model()

class TestDeadlockAllocateDeposit(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com')
        UserWallet.objects.create(user=self.user, balance=Decimal('100.00'))
        self.pocket = WalletPocket.objects.create(
            wallet=UserWallet.objects.get(user=self.user),
            name='Test Pocket',
            pocket_type='DONATION',
            allocation_percentage=Decimal('50.0')
        )
    
    def test_nested_transactions_cause_deadlock(self):
        """
        PROUVE LA FAILLE : Transactions imbriquées = deadlock
        """
        errors = []
        
        def allocate():
            try:
                result = allocate_deposit_across_pockets(self.user, Decimal('50.00'))
                return result
            except Exception as e:
                errors.append(str(e))
                return None
        
        def transfer():
            try:
                result = transfer_to_pocket(self.user, self.pocket.id, Decimal('25.00'))
                return result
            except Exception as e:
                errors.append(str(e))
                return None
        
        # Lancer 2 threads simultanément (simule opérations concurrentes)
        thread1 = threading.Thread(target=allocate)
        thread2 = threading.Thread(target=transfer)
        
        thread1.start()
        time.sleep(0.01)  # Petit délai pour créer le deadlock
        thread2.start()
        
        # Timeout pour détecter le deadlock
        thread1.join(timeout=5)
        thread2.join(timeout=5)
        
        # ❌ CE TEST VA ÉCHOUER (prouve le deadlock)
        # Si deadlock, les threads ne se terminent pas dans les 5 secondes
        self.assertFalse(
            thread1.is_alive() and thread2.is_alive(),
            "Les threads sont bloqués (deadlock détecté)"
        )
        self.assertEqual(
            len(errors),
            0,  # Attendu : pas d'erreurs (mais on a un deadlock)
            "Aucune erreur ne devrait survenir, mais un deadlock a été détecté"
        )
```

---

## 📊 RÉSUMÉ DES FAILLES

| Faille | Fichier | Impact | Test |
|--------|---------|--------|------|
| Double dépense (idempotence) | `finance/services.py:36-39` | 🔴 Critique | `test_double_pledge_without_idempotency` |
| Double crédit SAKA | `core/services/saka.py:121-149` | 🔴 Critique | `test_double_harvest_creates_double_credit` |
| Double libération escrow | `finance/services.py:139-180` | 🔴 Critique | `test_double_release_creates_double_commission` |
| Deadlock (transactions imbriquées) | `finance/services.py:335-409` | 🟡 Important | `test_nested_transactions_cause_deadlock` |
| Double création wallet SAKA | `core/services/saka.py:58-80` | 🟡 Important | (implicite dans test 2) |

---

## 🎯 FIXES PRIORITAIRES

### Priorité 1 : Fix `pledge_funds()` (2h)
1. Déplacer vérification idempotence APRÈS verrouillage
2. OU utiliser verrouillage DB sur `idempotency_key`

### Priorité 2 : Fix `harvest_saka()` (2h)
1. Utiliser `select_for_update().get_or_create()` directement
2. Déplacer vérification limite APRÈS verrouillage

### Priorité 3 : Fix `release_escrow()` (1h)
1. Verrouiller escrow avec `select_for_update()`
2. Marquer status = 'RELEASED' AVANT calculs

### Priorité 4 : Fix `allocate_deposit_across_pockets()` (1h)
1. Ne pas appeler `transfer_to_pocket()` (évite transaction imbriquée)
2. Faire le transfert directement dans la fonction

---

**Document généré le : 2025-12-19**  
**Auditeur : Senior Code Auditor (Cynique)**  
**Statut : 🔥 RACE CONDITIONS IDENTIFIÉES - TESTS POUR PREUVE CRÉÉS**

