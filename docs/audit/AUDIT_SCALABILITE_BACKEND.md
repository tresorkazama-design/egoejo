# 🔥 AUDIT CRITIQUE - Scalabilité Backend (100K Utilisateurs)

**Date** : 2025-12-19  
**Auditeur** : Senior Code Auditor (Cynique)  
**Mission** : Crash Test de Scalabilité - Identifier les points de rupture à 100K utilisateurs

---

## 💀 CRITIQUES MAJEURES

### 1. Compostage : Boucle N+1 avec Saves Individuels = SUICIDE

**Fichier** : `backend/core/services/saka.py:372-409`

**Problème** :
```python
for wallet in qs:  # ❌ BOUCLE sur tous les wallets inactifs
    # ...
    wallet.balance -= amount
    wallet.total_composted += amount
    wallet.last_activity_date = timezone.now()
    wallet.save(update_fields=[...])  # ❌ SAVE INDIVIDUEL
    
    SakaTransaction.objects.create(  # ❌ CREATE INDIVIDUEL
        user=wallet.user,
        # ...
    )
```

**Impact avec 100K utilisateurs** :
- **10% inactifs = 10K wallets**
- **10K `wallet.save()` = 10K requêtes UPDATE**
- **10K `SakaTransaction.objects.create()` = 10K requêtes INSERT**
- **Total = 20K requêtes DB dans une transaction**
- **Temps estimé : 5-10 minutes** (si DB tient)
- **Verrou DB : Table `SakaWallet` verrouillée pendant TOUT le cycle**
- **Timeout garanti**

**Verdict** : **CATASTROPHIQUE**. Code d'amateur qui ne scale pas.

**Fix** :
```python
# Préparer les mises à jour en batch
wallets_to_update = []
transactions_to_create = []

for wallet in qs:
    # Calculs seulement
    amount = int(floor(wallet.balance * rate))
    if amount < min_amount:
        continue
    
    wallets_to_update.append({
        'id': wallet.id,
        'balance': wallet.balance - amount,
        'total_composted': wallet.total_composted + amount,
        'last_activity_date': timezone.now()
    })
    
    transactions_to_create.append(
        SakaTransaction(
            user_id=wallet.user_id,  # ❌ ÉVITER wallet.user (N+1)
            direction='SPEND',
            amount=amount,
            reason='compost',
            # ...
        )
    )

# Batch update (1 requête)
SakaWallet.objects.bulk_update(
    [SakaWallet(**w) for w in wallets_to_update],
    ['balance', 'total_composted', 'last_activity_date']
)

# Bulk create (1 requête)
SakaTransaction.objects.bulk_create(transactions_to_create)
```

---

### 2. Redistribution : Chargement de 100K Wallets en Mémoire = OOM

**Fichier** : `backend/core/services/saka.py:584-608`

**Problème** :
```python
eligible_qs = SakaWallet.objects.select_for_update().filter(...)
eligible_wallets = list(eligible_qs)  # ❌ CHARGE TOUS EN MÉMOIRE
wallet_ids = [w.id for w in eligible_wallets]

# ...
for wallet in eligible_wallets:  # ❌ BOUCLE sur 100K objets
    transactions_to_create.append(
        SakaTransaction(user=wallet.user, ...)  # ❌ N+1 si pas select_related
    )
```

**Impact avec 100K utilisateurs** :
- **100K wallets éligibles = 100K objets en mémoire**
- **Mémoire : ~500MB-1GB** (selon taille objets)
- **Out of Memory (OOM) garanti** sur serveur < 4GB RAM
- **Même avec RAM suffisante, GC pressure énorme**

**Verdict** : **MEMORY LEAK MASSIF**. Pas de pagination, pas de chunking.

**Fix** :
```python
# Chunking : Traiter par batches de 1000
BATCH_SIZE = 1000

eligible_ids = list(
    SakaWallet.objects
    .filter(total_harvested__gte=min_activity)
    .values_list('id', flat=True)
)

# Traiter par chunks
for i in range(0, len(eligible_ids), BATCH_SIZE):
    chunk_ids = eligible_ids[i:i + BATCH_SIZE]
    
    # Batch update
    SakaWallet.objects.filter(id__in=chunk_ids).update(
        balance=F('balance') + per_wallet,
        total_harvested=F('total_harvested') + per_wallet,
        last_activity_date=timezone.now()
    )
    
    # Bulk create transactions (avec user_id directement)
    transactions = [
        SakaTransaction(
            user_id=wallet_id,  # ❌ BESOIN user_id, pas user
            direction='EARN',
            amount=per_wallet,
            reason='silo_redistribution',
        )
        for wallet_id in chunk_ids
    ]
    SakaTransaction.objects.bulk_create(transactions)
```

**PROBLÈME** : `SakaTransaction` a `user` (ForeignKey), pas `user_id`. **BESOIN DE MIGRATION**.

---

### 3. Redistribution : select_for_update() sur 100K Wallets = DEADLOCK

**Fichier** : `backend/core/services/saka.py:558-562`

**Problème** :
```python
eligible_qs = (
    SakaWallet.objects
    .select_for_update()  # ❌ VERROUILLE 100K LIGNES
    .filter(total_harvested__gte=min_activity)
)
```

**Impact avec 100K utilisateurs** :
- **`select_for_update()` verrouille TOUTES les lignes**
- **100K verrous = Deadlock garanti** si autre transaction accède aux wallets
- **Timeout DB : Transaction trop longue**
- **Blocage de TOUTES les opérations SAKA** pendant la redistribution

**Verdict** : **DEADLOCK GARANTI**. Verrouillage massif inacceptable.

**Fix** :
```python
# ❌ NE PAS utiliser select_for_update() sur toute la table
# Utiliser F() expressions (atomiques) sans verrouillage explicite
# OU verrouiller seulement le Silo (singleton)
```

---

### 4. Compostage : select_for_update() sur QuerySet = VERROU MASSIF

**Fichier** : `backend/core/services/saka.py:353-356`

**Problème** :
```python
qs = SakaWallet.objects.select_for_update().filter(
    last_activity_date__lt=cutoff,
    balance__gte=min_balance,
)
```

**Impact avec 100K utilisateurs** :
- **10K wallets inactifs = 10K verrous**
- **Verrou pendant TOUTE la boucle** (5-10 minutes)
- **Toutes les opérations SAKA bloquées**

**Verdict** : **BLOCAGE TOTAL**. Architecture défaillante.

**Fix** :
```python
# Ne pas verrouiller les wallets individuellement
# Utiliser F() expressions pour updates atomiques
# Verrouiller seulement le Silo (singleton)
```

---

### 5. harvest_saka : 2 Requêtes pour Limite Quotidienne = INEFFICACE

**Fichier** : `backend/core/services/saka.py:135-149`

**Problème** :
```python
today_total = SakaTransaction.objects.filter(...).aggregate(total=Sum('amount'))['total']
# ❌ REQUÊTE 1 : SUM

today_count = SakaTransaction.objects.filter(...).count()
# ❌ REQUÊTE 2 : COUNT (même filtre)
```

**Impact avec 100K utilisateurs** :
- **2 requêtes au lieu d'1** pour chaque `harvest_saka()`
- **Si 1000 récoltes/min = 2000 requêtes/min inutiles**
- **Charge DB inutile**

**Verdict** : **INEFFICACE**. Requêtes dupliquées.

**Fix** :
```python
# Une seule requête avec annotate
from django.db.models import Sum, Count

stats = SakaTransaction.objects.filter(
    user=user,
    direction='EARN',
    reason=reason.value,
    created_at__date=today
).aggregate(
    total=Sum('amount'),
    count=Count('id')
)

today_total = stats['total'] or 0
today_count = stats['count']
```

---

### 6. tasks.py : Boucle avec Tâches Celery Individuelles = QUEUE EXPLOSION

**Fichier** : `backend/core/tasks.py:38-51`

**Problème** :
```python
for escrow in escrows:
    if escrow.user and escrow.user.email:
        send_email_task.delay(...)  # ❌ TÂCHE CELERY PAR EMAIL
```

**Impact avec 100K utilisateurs** :
- **Si 1000 escrows = 1000 tâches Celery créées**
- **Queue Celery saturée**
- **Latence énorme**
- **Memory leak si queue non vidée**

**Verdict** : **QUEUE EXPLOSION**. Pas de batching.

**Fix** :
```python
# Grouper les emails par batch
emails_batch = [
    (escrow.user.email, subject, html_content)
    for escrow in escrows
    if escrow.user and escrow.user.email
]

# Une seule tâche pour envoyer tous les emails
send_bulk_email_task.delay(emails_batch)
```

---

### 7. Compostage : Pas de Pagination/Chunking = TIMEOUT

**Fichier** : `backend/core/services/saka.py:372`

**Problème** :
```python
for wallet in qs:  # ❌ TOUS les wallets en une fois
```

**Impact avec 100K utilisateurs** :
- **10K wallets traités en une transaction**
- **Transaction trop longue = Timeout**
- **Rollback complet si erreur**

**Verdict** : **TIMEOUT GARANTI**. Pas de chunking.

**Fix** :
```python
# Traiter par chunks de 500
BATCH_SIZE = 500
offset = 0

while True:
    chunk = qs[offset:offset + BATCH_SIZE]
    if not chunk.exists():
        break
    
    # Traiter le chunk
    # ...
    
    offset += BATCH_SIZE
```

---

### 8. Redistribution : Pas de select_related() = N+1 Queries

**Fichier** : `backend/core/services/saka.py:584-605`

**Problème** :
```python
eligible_wallets = list(eligible_qs)  # ❌ Pas de select_related('user')

for wallet in eligible_wallets:
    transactions_to_create.append(
        SakaTransaction(user=wallet.user, ...)  # ❌ N+1 si pas select_related
    )
```

**Impact avec 100K utilisateurs** :
- **100K wallets = 100K requêtes `SELECT user FROM User WHERE id=...`**
- **Total = 100K requêtes inutiles**
- **DB saturée**

**Verdict** : **N+1 QUERIES MASSIF**. Amateur.

**Fix** :
```python
# Utiliser user_id directement (si migration faite)
# OU select_related('user')
eligible_qs = SakaWallet.objects.select_related('user').filter(...)
```

---

## 🔥 POINTS DE RUPTURE PAR CATÉGORIE

### Performance Critique
1. ❌ Compostage : 20K requêtes DB (saves individuels)
2. ❌ Redistribution : 100K objets en mémoire (OOM)
3. ❌ Compostage : Pas de chunking (timeout)
4. ❌ Redistribution : Pas de chunking (timeout)

### Verrous DB
5. ❌ `select_for_update()` sur 100K wallets (deadlock)
6. ❌ Transaction trop longue (timeout)
7. ❌ Verrouillage de toute la table `SakaWallet`

### Memory Leaks
8. ❌ Chargement de 100K wallets en mémoire
9. ❌ Pas de pagination/chunking
10. ❌ GC pressure énorme

### N+1 Queries
11. ❌ 2 requêtes pour limite quotidienne (harvest_saka)
12. ❌ Pas de select_related('user') (redistribution)
13. ❌ Boucle avec wallet.user (N+1)

### Architecture
14. ❌ Pas de batching pour emails (tasks.py)
15. ❌ Pas de migration pour user_id (SakaTransaction)

---

## 💣 SCORE DE RUPTURE

| Service | Score Rupture | Verdict |
|---------|---------------|---------|
| `run_saka_compost_cycle` | **10/10** | 💀 Critique - Ne scale pas |
| `redistribute_saka_silo` | **9/10** | 💀 Critique - OOM + Deadlock |
| `harvest_saka` | **5/10** | ⚠️ Inefficace |
| `tasks.py` | **6/10** | ⚠️ Queue explosion |

**Score Global** : **8/10 - PROJET NE SCALE PAS**

---

## 🎯 REFACTORISATION MASSIVE (Par Priorité)

### 🔴 PRIORITÉ 1 : Fix Compostage (4h)
1. **Batch Update** : Remplacer `wallet.save()` par `bulk_update()`
2. **Bulk Create** : Remplacer `create()` par `bulk_create()`
3. **Chunking** : Traiter par batches de 500
4. **Retirer select_for_update()** : Utiliser F() expressions

**Code Refactorisé** :
```python
def run_saka_compost_cycle(dry_run: bool = False, source: str = "celery") -> Dict:
    # ... config ...
    
    BATCH_SIZE = 500
    offset = 0
    total_composted = 0
    affected = 0
    
    while True:
        # Chunk de wallets
        chunk = SakaWallet.objects.filter(
            last_activity_date__lt=cutoff,
            balance__gte=min_balance,
        )[offset:offset + BATCH_SIZE]
        
        if not chunk.exists():
            break
        
        wallets_to_update = []
        transactions_to_create = []
        
        for wallet in chunk:
            amount = int(floor(wallet.balance * rate))
            if amount < min_amount:
                continue
            
            wallets_to_update.append(SakaWallet(
                id=wallet.id,
                balance=wallet.balance - amount,
                total_composted=wallet.total_composted + amount,
                last_activity_date=timezone.now()
            ))
            
            transactions_to_create.append(SakaTransaction(
                user_id=wallet.user_id,  # ❌ BESOIN user_id
                direction='SPEND',
                amount=amount,
                reason='compost',
                metadata={...}
            ))
        
        if not dry_run and wallets_to_update:
            # Batch update
            SakaWallet.objects.bulk_update(
                wallets_to_update,
                ['balance', 'total_composted', 'last_activity_date']
            )
            
            # Bulk create
            SakaTransaction.objects.bulk_create(transactions_to_create)
            
            # Mise à jour Silo (une seule fois par chunk)
            SakaSilo.objects.filter(id=1).update(
                total_balance=F('total_balance') + sum(t.amount for t in transactions_to_create),
                total_composted=F('total_composted') + sum(t.amount for t in transactions_to_create),
            )
        
        total_composted += sum(t.amount for t in transactions_to_create)
        affected += len(wallets_to_update)
        offset += BATCH_SIZE
    
    # ...
```

---

### 🟡 PRIORITÉ 2 : Fix Redistribution (3h)
1. **Chunking** : Traiter par batches de 1000
2. **Retirer select_for_update()** : Utiliser F() expressions
3. **Migration user_id** : Ajouter `user_id` à `SakaTransaction`
4. **Éviter list()** : Utiliser `values_list('id', flat=True)`

**Code Refactorisé** :
```python
def redistribute_saka_silo(rate: float | None = None) -> Dict:
    # ... config ...
    
    BATCH_SIZE = 1000
    
    # Récupérer seulement les IDs (pas les objets)
    eligible_ids = list(
        SakaWallet.objects
        .filter(total_harvested__gte=min_activity)
        .values_list('id', flat=True)
    )
    
    if not eligible_ids:
        return {"ok": False, "reason": "no_eligible_wallets"}
    
    per_wallet = total_to_redistribute // len(eligible_ids)
    
    # Traiter par chunks
    for i in range(0, len(eligible_ids), BATCH_SIZE):
        chunk_ids = eligible_ids[i:i + BATCH_SIZE]
        
        # Batch update (atomique avec F())
        SakaWallet.objects.filter(id__in=chunk_ids).update(
            balance=F('balance') + per_wallet,
            total_harvested=F('total_harvested') + per_wallet,
            last_activity_date=timezone.now()
        )
        
        # Bulk create transactions
        transactions = [
            SakaTransaction(
                user_id=wallet_id,  # ❌ BESOIN user_id
                direction='EARN',
                amount=per_wallet,
                reason='silo_redistribution',
            )
            for wallet_id in chunk_ids
        ]
        SakaTransaction.objects.bulk_create(transactions)
    
    # Mise à jour Silo (une seule fois)
    actual_redistributed = per_wallet * len(eligible_ids)
    SakaSilo.objects.filter(id=1).update(
        total_balance=F('total_balance') - actual_redistributed
    )
    
    # ...
```

---

### 🟢 PRIORITÉ 3 : Fix harvest_saka (1h)
1. **Une seule requête** : Utiliser `aggregate()` avec `Sum` et `Count`
2. **Optimiser** : Réduire de 2 requêtes à 1

---

### 🔵 PRIORITÉ 4 : Fix tasks.py (1h)
1. **Batching emails** : Grouper les emails en une seule tâche
2. **Éviter queue explosion** : Limiter le nombre de tâches

---

## 📋 MIGRATIONS REQUISES

### Migration 1 : Ajouter user_id à SakaTransaction
```python
# migrations/XXXX_add_user_id_to_saka_transaction.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('core', 'XXXX_previous'),
    ]

    operations = [
        migrations.AddField(
            model_name='sakatransaction',
            name='user_id',
            field=models.IntegerField(null=True),
        ),
        # Populate user_id from user
        migrations.RunPython(populate_user_id),
        # Make user_id not null
        migrations.AlterField(
            model_name='sakatransaction',
            name='user_id',
            field=models.IntegerField(),
        ),
    ]
```

---

## 🎯 ESTIMATION TEMPS

| Tâche | Temps | Priorité |
|-------|-------|----------|
| Fix Compostage | 4h | 🔴 Critique |
| Fix Redistribution | 3h | 🔴 Critique |
| Fix harvest_saka | 1h | 🟡 Important |
| Fix tasks.py | 1h | 🟡 Important |
| Migration user_id | 2h | 🔴 Critique |
| **TOTAL** | **11h** | |

---

## 💣 VERDICT FINAL

**Le code actuel NE SCALE PAS à 100K utilisateurs.**

**Points de rupture critiques** :
1. **Compostage** : 20K requêtes DB = Timeout garanti
2. **Redistribution** : 100K objets en mémoire = OOM garanti
3. **Verrous DB** : Deadlock garanti
4. **Pas de chunking** : Transactions trop longues

**Refactorisation massive requise avant production à grande échelle.**

---

**Document généré le : 2025-12-19**  
**Auditeur : Senior Code Auditor (Cynique)**  
**Statut : 🔥 POINTS DE RUPTURE IDENTIFIÉS - REFACTORISATION URGENTE**

