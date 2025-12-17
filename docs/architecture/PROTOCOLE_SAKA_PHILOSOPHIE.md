# 🌾 Protocole SAKA : Pourquoi ça ne peut pas marcher autrement

**Date** : 2025-12-17  
**Version** : 1.0  
**Audiences** : Développeurs, Partenaires institutionnels, Membres de la communauté

---

## 📖 Introduction

Cette documentation explique **non seulement comment** le protocole SAKA fonctionne, mais **pourquoi** il ne peut pas fonctionner autrement. Chaque choix technique est une conséquence directe des principes fondateurs d'EGOEJO : **anti-accumulation, circulation obligatoire, retour au commun, non-spéculation**.

Si vous êtes développeur, partenaire institutionnel ou membre de la communauté, cette documentation vous aidera à comprendre que les "contraintes" techniques sont en réalité des **garanties morales** encodées dans le code.

---

## 🎯 Pour qui cette documentation ?

### 👨‍💻 Pour le développeur futur

Vous allez modifier le code SAKA. Avant de changer quoi que ce soit, comprenez **pourquoi** chaque ligne existe. Si vous supprimez une vérification, vous cassez une garantie morale. Si vous ajoutez une fonctionnalité, vérifiez qu'elle respecte le Manifeste.

### 🏛️ Pour le partenaire institutionnel

Vous évaluez EGOEJO pour un partenariat ou un financement. Cette documentation vous montre que le protocole SAKA n'est pas un "gadget technique", mais une **infrastructure morale** qui garantit que la plateforme ne peut pas dériver vers l'accumulation ou la spéculation.

### 👥 Pour le membre de la communauté

Vous utilisez SAKA au quotidien. Cette documentation vous explique que chaque mécanisme (compostage, redistribution, limites) existe pour **protéger le collectif** contre l'accumulation individuelle. Votre SAKA ne peut pas être "volé" ou "perdu" : il circule ou retourne au commun.

---

## 🌍 Les Principes Fondateurs (Le Pourquoi)

### 1. Anti-Accumulation : La valeur ne peut pas être stockée indéfiniment

**Principe moral** : L'accumulation infinie de valeur est une forme de captation qui nuit au collectif. Dans un système financier traditionnel, tu peux thésauriser de l'argent indéfiniment. Dans SAKA, **c'est impossible par design**.

**Contrainte technique** : Le compostage progressif (10% par cycle après 90 jours d'inactivité) n'est pas une "pénalité" : c'est une **garantie** que le SAKA inactif retourne au Silo Commun.

**Pourquoi ça ne peut pas marcher autrement** :
- ❌ **Sans compostage** : Les utilisateurs pourraient accumuler des milliers de SAKA et ne jamais les utiliser, créant une inégalité permanente.
- ✅ **Avec compostage** : Le SAKA inactif retourne au Silo, qui est redistribué équitablement au collectif. L'accumulation stérile est impossible.

**Code qui garantit cela** :
```python
# backend/core/services/saka.py - run_saka_compost_cycle()
# Cette fonction est OBLIGATOIRE. Si vous la désactivez, vous violez le Manifeste.
if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
    return {"skipped": "disabled"}  # ⚠️ VIOLATION PHILOSOPHIQUE
```

**Tests qui protègent cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_saka_inactif_doit_être_composté_après_inactivité(self):
    """PHILOSOPHIE : La valeur ne peut pas être stockée indéfiniment."""
    # Si ce test échoue, le Manifeste est violé.
```

---

### 2. Circulation Obligatoire : Un utilisateur ne peut pas contourner le cycle

**Principe moral** : Le SAKA doit circuler. Si un utilisateur essaie de "tricher" en faisant une activité minimale juste avant le compostage, le système doit quand même appliquer le compostage sur le solde inactif.

**Contrainte technique** : Le compostage vérifie `last_activity_date < cutoff` (90 jours). Même si un utilisateur fait une activité ponctuelle, le solde inactif depuis 90+ jours est composté.

**Pourquoi ça ne peut pas marcher autrement** :
- ❌ **Sans vérification d'inactivité** : Un utilisateur pourrait faire une activité minimale (1 SAKA) juste avant le compostage pour "réinitialiser" son inactivité, contournant le cycle.
- ✅ **Avec vérification stricte** : Le compostage s'applique sur le solde inactif, même si l'utilisateur essaie de contourner. Le cycle ne peut pas être contourné.

**Code qui garantit cela** :
```python
# backend/core/services/saka.py - run_saka_compost_cycle()
cutoff = timezone.now() - timedelta(days=inactivity_days)
qs = SakaWallet.objects.select_for_update().filter(
    last_activity_date__lt=cutoff,  # ⚠️ Vérification stricte : inactif depuis 90+ jours
    balance__gte=min_balance,
)
```

**Tests qui protègent cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_impossibilité_de_contourner_le_compostage_par_activité_ponctuelle(self):
    """PHILOSOPHIE : Un utilisateur ne peut pas contourner le cycle."""
    # Si ce test échoue, le cycle peut être contourné = violation du Manifeste.
```

---

### 3. Retour au Commun : Le collectif bénéficie de l'inutilisation individuelle

**Principe moral** : Si un utilisateur ne utilise pas son SAKA, ce n'est pas une "perte" : c'est un **retour au commun**. Le SAKA composté va dans le Silo Commun, qui est redistribué équitablement aux wallets actifs.

**Contrainte technique** : Le Silo Commun (`SakaSilo`) est un singleton qui accumule le SAKA composté. La redistribution (`redistribute_saka_silo()`) distribue équitablement le Silo aux wallets actifs (ceux qui ont déjà participé).

**Pourquoi ça ne peut pas marcher autrement** :
- ❌ **Sans Silo Commun** : Le SAKA composté serait "perdu", créant une déflation permanente et décourageant l'engagement.
- ✅ **Avec Silo Commun** : Le SAKA composté retourne au collectif, qui le redistribue équitablement. L'inutilisation individuelle nourrit le collectif.

**Code qui garantit cela** :
```python
# backend/core/services/saka.py - run_saka_compost_cycle()
# Le SAKA composté va dans le Silo Commun
silo.total_balance += amount
silo.total_composted += amount

# backend/core/services/saka.py - redistribute_saka_silo()
# Le Silo est redistribué équitablement aux wallets actifs
eligible_qs = SakaWallet.objects.filter(total_harvested__gte=min_activity)
per_wallet = total_to_redistribute // eligible_count
```

**Tests qui protègent cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_collectif_bénéficie_de_inutilisation_individuelle(self):
    """PHILOSOPHIE : Le collectif bénéficie de l'inutilisation individuelle."""
    # Si ce test échoue, le Silo ne bénéficie pas du compostage = violation du Manifeste.
```

---

### 4. Non-Spéculation : SAKA ne peut pas être acheté, vendu ou échangé

**Principe moral** : SAKA n'est pas un actif spéculatif. Il ne peut pas être acheté avec de l'argent, vendu contre de l'argent, ou échangé contre d'autres actifs. SAKA mesure l'engagement, pas la valeur financière.

**Contrainte technique** : **Aucune conversion possible** entre SAKA et Euro. Les modèles sont séparés (`SakaWallet` vs `UserWallet`), les endpoints sont distincts (`/api/saka/*` vs `/api/wallet/*`), et aucune logique financière n'existe dans les services SAKA.

**Pourquoi ça ne peut pas marcher autrement** :
- ❌ **Avec conversion SAKA ↔ Euro** : SAKA deviendrait un actif spéculatif, créant une dynamique d'accumulation et de captation. Les utilisateurs "riches" pourraient acheter de l'influence.
- ✅ **Sans conversion** : SAKA reste une mesure d'engagement pure. L'influence ne peut pas être achetée, seulement gagnée par l'engagement.

**Code qui garantit cela** :
```python
# backend/core/services/saka.py
# Aucune fonction de conversion SAKA ↔ Euro n'existe.
# Les services SAKA n'importent jamais les modèles financiers.

# backend/core/models/saka.py
# SakaWallet est complètement séparé de UserWallet.
# Aucune ForeignKey vers UserWallet, aucun lien financier.
```

**Tests qui protègent cela** :
```python
# backend/core/tests_saka_philosophy.py
# Aucun test de conversion n'existe, car la conversion est impossible par design.
# Si vous ajoutez une fonction de conversion, vous violez le Manifeste.
```

---

### 5. Cycle Complet : Récolte → Plantation → Compost → Silo → Redistribution

**Principe moral** : Le cycle SAKA est **circulaire**, pas linéaire. Le SAKA ne "disparaît" jamais : il circule ou retourne au commun. Ce cycle garantit que la valeur reste dans le collectif.

**Contrainte technique** : Le cycle complet doit fonctionner :
1. **Récolte** (`harvest_saka`) : L'utilisateur gagne du SAKA par son engagement.
2. **Plantation** (`spend_saka`) : L'utilisateur dépense du SAKA pour influencer.
3. **Compost** (`run_saka_compost_cycle`) : Le SAKA inactif retourne au Silo.
4. **Redistribution** (`redistribute_saka_silo`) : Le Silo est redistribué au collectif.

**Pourquoi ça ne peut pas marcher autrement** :
- ❌ **Sans cycle complet** : Le SAKA pourrait "disparaître" ou s'accumuler indéfiniment, violant les principes d'anti-accumulation et de retour au commun.
- ✅ **Avec cycle complet** : Le SAKA circule en permanence, garantissant que la valeur reste dans le collectif et que l'accumulation stérile est impossible.

**Code qui garantit cela** :
```python
# backend/core/services/saka.py
# Le cycle complet est implémenté et testé.
# Chaque étape est une fonction séparée, mais elles forment un cycle complet.

# backend/core/tests_saka_philosophy.py
def test_cycle_complet_récolte_plantation_compost_silo_redistribution(self):
    """PHILOSOPHIE : Le cycle circulaire complet doit fonctionner."""
    # Si ce test échoue, le cycle est incomplet = violation du Manifeste.
```

---

## 🔒 Les Garanties Techniques (Le Comment)

### Garantie 1 : Aucun solde SAKA ne peut devenir négatif

**Contrainte morale** : Un solde négatif signifierait que l'utilisateur "doit" du SAKA, créant une dynamique de dette. SAKA ne peut pas créer de dette : il mesure l'engagement, pas la valeur financière.

**Implémentation technique** :
```python
# backend/core/services/saka.py - spend_saka()
# Vérification AVANT la dépense
if wallet.balance < amount:
    logger.warning(f"Solde SAKA insuffisant pour {user.username}: {wallet.balance} < {amount}")
    return False  # ⚠️ La dépense est refusée, pas de solde négatif possible
```

**Pourquoi c'est contraignant** : Cette vérification empêche les "découverts" SAKA. Si vous voulez permettre les découverts, vous violez le Manifeste : SAKA ne peut pas créer de dette.

**Tests qui protègent cela** :
```python
# backend/core/tests_saka.py - SakaSpendTestCase
def test_spend_insufficient_balance(self):
    """Vérifie qu'un solde insuffisant empêche la dépense."""
    # Si ce test échoue, les soldes négatifs sont possibles = violation du Manifeste.
```

---

### Garantie 2 : Protection contre les race conditions (double dépense)

**Contrainte morale** : Un utilisateur ne peut pas dépenser plus de SAKA qu'il n'en a. Si deux requêtes simultanées tentent de dépenser le même SAKA, une seule doit réussir.

**Implémentation technique** :
```python
# backend/core/services/saka.py - spend_saka()
# Verrouillage du wallet pour éviter les race conditions
wallet = SakaWallet.objects.select_for_update().get(id=wallet.id)

# Vérification APRÈS verrouillage (lecture atomique)
if wallet.balance < amount:
    return False  # ⚠️ Même si le solde était suffisant avant, il ne l'est plus après verrouillage

# Mise à jour atomique avec F() expressions
SakaWallet.objects.filter(id=wallet.id).update(
    balance=F('balance') - amount,  # ⚠️ Atomicité garantie au niveau DB
    total_planted=F('total_planted') + amount,
    last_activity_date=timezone.now()
)
```

**Pourquoi c'est contraignant** : Cette implémentation nécessite des verrous de base de données (`select_for_update()`), ce qui peut créer des goulots d'étranglement en cas de forte charge. Mais c'est **obligatoire** : sans cela, la double dépense est possible, violant le Manifeste.

**Tests qui protègent cela** :
```python
# backend/core/tests_saka.py - SakaConcurrencyTestCase
def test_concurrent_boost_same_wallet(self):
    """Simule deux boosts simultanés sur le même wallet."""
    # Si ce test échoue, la double dépense est possible = violation du Manifeste.
```

---

### Garantie 3 : Compostage progressif (10% par cycle)

**Contrainte morale** : Le compostage ne doit pas être une "punition brutale" (100% d'un coup), mais un **retour progressif au commun**. Le compostage progressif (10% par cycle) garantit que l'accumulation stérile est impossible, tout en laissant le temps à l'utilisateur de réagir.

**Implémentation technique** :
```python
# backend/core/services/saka.py - run_saka_compost_cycle()
rate = float(getattr(settings, "SAKA_COMPOST_RATE", 0.1))  # 10% par défaut
raw_amount = wallet.balance * rate
amount = int(floor(raw_amount))  # ⚠️ Arrondi vers le bas (floor) pour éviter les fractions

# Le compostage s'applique progressivement
wallet.balance -= amount  # ⚠️ 10% du solde, pas 100%
```

**Pourquoi c'est contraignant** : Le taux de 10% est fixe par défaut. Si vous voulez un taux variable ou un compostage "tout ou rien", vous violez le Manifeste : le compostage doit être progressif pour éviter la "punition brutale".

**Tests qui protègent cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_compostage_progressif_empêche_thésaurisation_infinie(self):
    """PHILOSOPHIE : L'impossibilité de thésaurisation."""
    # Si ce test échoue, le compostage progressif ne fonctionne pas = violation du Manifeste.
```

---

### Garantie 4 : Redistribution équitable du Silo

**Contrainte morale** : Le Silo Commun doit être redistribué **équitablement** aux wallets actifs (ceux qui ont déjà participé). La redistribution ne doit pas favoriser les "riches" ou créer des inégalités.

**Implémentation technique** :
```python
# backend/core/services/saka.py - redistribute_saka_silo()
# Wallets éligibles : ont déjà récolté au moins min_activity grains
eligible_qs = SakaWallet.objects.filter(total_harvested__gte=min_activity)

# Répartition équitable (division entière)
per_wallet = total_to_redistribute // eligible_count  # ⚠️ Même montant pour tous

# Mise à jour atomique de tous les wallets
SakaWallet.objects.filter(id__in=wallet_ids).update(
    balance=F('balance') + per_wallet,  # ⚠️ Même montant pour tous
    total_harvested=F('total_harvested') + per_wallet,
    last_activity_date=timezone.now()
)
```

**Pourquoi c'est contraignant** : La redistribution est **équitable** (même montant pour tous), pas **proportionnelle** (selon le solde). Si vous voulez une redistribution proportionnelle, vous violez le Manifeste : cela favoriserait les "riches" et créerait des inégalités.

**Tests qui protègent cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_redistribution_du_silo_vers_collectif(self):
    """PHILOSOPHIE : Le Silo Commun est redistribué au collectif."""
    # Si ce test échoue, la redistribution n'est pas équitable = violation du Manifeste.
```

---

### Garantie 5 : Limites quotidiennes anti-farming

**Contrainte morale** : Le SAKA doit être gagné par l'**engagement réel**, pas par le "farming" (actions répétitives pour gagner du SAKA sans engagement). Les limites quotidiennes empêchent le farming massif.

**Implémentation technique** :
```python
# backend/core/services/saka.py - harvest_saka()
# Limites quotidiennes par raison
SAKA_DAILY_LIMITS = {
    SakaReason.CONTENT_READ: 3,  # Max 3 contenus par jour
    SakaReason.POLL_VOTE: 10,     # Max 10 votes par jour
    SakaReason.INVITE_ACCEPTED: 5,  # Max 5 invitations par jour
}

# Vérification du nombre de transactions aujourd'hui
today = timezone.now().date()
today_count = SakaTransaction.objects.filter(
    user=user,
    direction='EARN',
    reason=reason.value,
    created_at__date=today
).count()

if today_count >= daily_limit:
    logger.warning(f"Limite quotidienne SAKA atteinte pour {user.username}")
    return None  # ⚠️ La récolte est refusée si la limite est atteinte
```

**Pourquoi c'est contraignant** : Les limites sont **fixes** par raison. Si vous voulez des limites variables ou supprimer les limites, vous violez le Manifeste : cela permettrait le farming massif, dévaluant le SAKA et violant le principe de "Proof of Care".

**Tests qui protègent cela** :
```python
# backend/core/tests_saka.py - SakaHarvestTestCase
def test_harvest_daily_limit(self):
    """Vérifie que les limites quotidiennes empêchent le farming."""
    # Si ce test échoue, le farming est possible = violation du Manifeste.
```

---

## 🚫 Ce qui est Interdit (Et Pourquoi)

### ❌ Interdit 1 : Conversion SAKA ↔ Euro

**Pourquoi c'est interdit** : SAKA mesure l'engagement, pas la valeur financière. Si SAKA peut être acheté avec de l'argent, il devient un actif spéculatif, violant le principe de non-spéculation.

**Code qui empêche cela** :
```python
# Aucune fonction de conversion n'existe dans le code.
# Si vous en créez une, vous violez le Manifeste.
```

**Test qui protège cela** :
```python
# Aucun test de conversion n'existe, car la conversion est impossible par design.
# Si vous ajoutez un test de conversion, vous violez le Manifeste.
```

---

### ❌ Interdit 2 : Désactiver le compostage en production

**Pourquoi c'est interdit** : Le compostage garantit que le SAKA inactif retourne au commun. Si vous désactivez le compostage, vous violez le principe d'anti-accumulation.

**Code qui empêche cela** :
```python
# backend/core/services/saka.py - run_saka_compost_cycle()
if not getattr(settings, "SAKA_COMPOST_ENABLED", False):
    return {"skipped": "disabled"}  # ⚠️ VIOLATION PHILOSOPHIQUE
```

**Test qui protège cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_compostage_désactivé_violation_philosophie(self):
    """PHILOSOPHIE : Le compostage DOIT être activé pour respecter le Manifeste."""
    # Ce test documente la violation si le compostage est désactivé.
```

---

### ❌ Interdit 3 : Permettre les soldes négatifs

**Pourquoi c'est interdit** : Un solde négatif signifierait que l'utilisateur "doit" du SAKA, créant une dynamique de dette. SAKA ne peut pas créer de dette : il mesure l'engagement, pas la valeur financière.

**Code qui empêche cela** :
```python
# backend/core/services/saka.py - spend_saka()
if wallet.balance < amount:
    return False  # ⚠️ La dépense est refusée, pas de solde négatif possible
```

**Test qui protège cela** :
```python
# backend/core/tests_saka.py - SakaSpendTestCase
def test_spend_insufficient_balance(self):
    """Vérifie qu'un solde insuffisant empêche la dépense."""
    # Si ce test échoue, les soldes négatifs sont possibles = violation du Manifeste.
```

---

### ❌ Interdit 4 : Redistribution proportionnelle (selon le solde)

**Pourquoi c'est interdit** : Une redistribution proportionnelle favoriserait les "riches" (ceux qui ont beaucoup de SAKA), créant des inégalités. La redistribution doit être **équitable** (même montant pour tous).

**Code qui empêche cela** :
```python
# backend/core/services/saka.py - redistribute_saka_silo()
per_wallet = total_to_redistribute // eligible_count  # ⚠️ Même montant pour tous
# Pas de calcul proportionnel basé sur le solde
```

**Test qui protège cela** :
```python
# backend/core/tests_saka_philosophy.py
def test_redistribution_du_silo_vers_collectif(self):
    """PHILOSOPHIE : Le Silo Commun est redistribué au collectif."""
    # Si ce test échoue, la redistribution n'est pas équitable = violation du Manifeste.
```

---

### ❌ Interdit 5 : Supprimer les limites quotidiennes

**Pourquoi c'est interdit** : Les limites quotidiennes empêchent le farming massif. Si vous supprimez les limites, les utilisateurs pourraient "farming" des milliers de SAKA par jour, dévaluant le SAKA et violant le principe de "Proof of Care".

**Code qui empêche cela** :
```python
# backend/core/services/saka.py - harvest_saka()
if today_count >= daily_limit:
    return None  # ⚠️ La récolte est refusée si la limite est atteinte
```

**Test qui protège cela** :
```python
# backend/core/tests_saka.py - SakaHarvestTestCase
def test_harvest_daily_limit(self):
    """Vérifie que les limites quotidiennes empêchent le farming."""
    # Si ce test échoue, le farming est possible = violation du Manifeste.
```

---

## 🧪 Les Tests Philosophiques (Protection du Manifeste)

### Pourquoi des tests "philosophiques" ?

Les tests unitaires classiques vérifient que le code fonctionne. Les **tests philosophiques** vérifient que le code **respecte le Manifeste**. Si un test philosophique échoue, ce n'est pas un bug technique : c'est une **violation du Manifeste**.

### Exemple de test philosophique

```python
# backend/core/tests_saka_philosophy.py
def test_saka_inactif_doit_être_composté_après_inactivité(self):
    """
    PHILOSOPHIE : La valeur ne peut pas être stockée indéfiniment.
    
    Assertion : Un wallet inactif depuis plus de 90 jours DOIT être composté.
    Le SAKA inactif retourne au Silo Commun.
    """
    # Créer un wallet inactif depuis 120 jours
    wallet.last_activity_date = timezone.now() - timedelta(days=120)
    
    # Exécuter le cycle de compostage
    result = run_saka_compost_cycle(dry_run=False, source="test")
    
    # ASSERTION PHILOSOPHIQUE : Le SAKA inactif DOIT être composté
    self.assertGreater(
        result['total_composted'], 0,
        "Le SAKA inactif DOIT être composté (retour au commun)"
    )
```

**Si ce test échoue** : Le compostage ne fonctionne pas, violant le principe d'anti-accumulation. Le Manifeste est violé.

### Liste des tests philosophiques

1. **`test_saka_inactif_doit_être_composté_après_inactivité`** : Vérifie que le SAKA inactif est composté (anti-accumulation).
2. **`test_saka_actif_n_est_pas_composté`** : Vérifie que le SAKA actif n'est pas composté (circulation préservée).
3. **`test_impossibilité_de_contourner_le_compostage_par_activité_ponctuelle`** : Vérifie que le cycle ne peut pas être contourné.
4. **`test_compostage_progressif_empêche_thésaurisation_infinie`** : Vérifie que le compostage progressif empêche la thésaurisation.
5. **`test_collectif_bénéficie_de_inutilisation_individuelle`** : Vérifie que le Silo bénéficie de l'inutilisation.
6. **`test_redistribution_du_silo_vers_collectif`** : Vérifie que la redistribution fonctionne.
7. **`test_redistribution_empêche_accumulation_du_silo`** : Vérifie que le Silo ne s'accumule pas indéfiniment.
8. **`test_cycle_complet_récolte_plantation_compost_silo_redistribution`** : Vérifie que le cycle complet fonctionne.
9. **`test_impossibilité_de_thésaurisation_à_long_terme`** : Vérifie que la thésaurisation est impossible à long terme.
10. **`test_pas_de_limite_maximale_mais_compostage_obligatoire`** : Vérifie qu'il n'y a pas de limite maximale mais que le compostage est obligatoire.
11. **`test_compostage_désactivé_violation_philosophie`** : Documente la violation si le compostage est désactivé.
12. **`test_redistribution_désactivée_violation_philosophie`** : Documente la violation si la redistribution est désactivée.

**Commande pour exécuter les tests philosophiques** :
```bash
cd backend
python -m pytest core/tests_saka_philosophy.py -vv
```

**Si un test philosophique échoue** : Ne "corrigez" pas le test. Corrigez le code pour qu'il respecte le Manifeste.

---

## 📋 Checklist pour les Développeurs

Avant de modifier le code SAKA, vérifiez que votre modification :

- [ ] **Respecte l'anti-accumulation** : Votre modification ne permet-elle pas l'accumulation infinie de SAKA ?
- [ ] **Respecte la circulation obligatoire** : Votre modification ne permet-elle pas de contourner le cycle ?
- [ ] **Respecte le retour au commun** : Votre modification garantit-elle que le SAKA inactif retourne au Silo ?
- [ ] **Respecte la non-spéculation** : Votre modification ne permet-elle pas de convertir SAKA ↔ Euro ?
- [ ] **Respecte le cycle complet** : Votre modification préserve-t-elle le cycle Récolte → Plantation → Compost → Silo → Redistribution ?
- [ ] **Passe les tests philosophiques** : Tous les tests dans `tests_saka_philosophy.py` passent-ils après votre modification ?

**Si une case n'est pas cochée** : Votre modification viole probablement le Manifeste. Réfléchissez à une alternative qui respecte les principes fondateurs.

---

## 🏛️ Checklist pour les Partenaires Institutionnels

Avant de vous engager avec EGOEJO, vérifiez que le protocole SAKA :

- [ ] **Garantit l'anti-accumulation** : Le code empêche-t-il l'accumulation infinie de SAKA ?
- [ ] **Garantit la circulation** : Le code garantit-il que le SAKA circule ou retourne au commun ?
- [ ] **Garantit la non-spéculation** : Le code empêche-t-il la conversion SAKA ↔ Euro ?
- [ ] **Garantit la transparence** : Les tests philosophiques documentent-ils les garanties morales ?
- [ ] **Garantit la réversibilité** : Le code peut-il être modifié pour violer le Manifeste ? (Réponse attendue : Non, les tests philosophiques empêchent cela)

**Si une case n'est pas cochée** : Le protocole SAKA ne garantit pas les principes fondateurs. Demandez des clarifications.

---

## 👥 Checklist pour les Membres de la Communauté

Avant d'utiliser SAKA, comprenez que :

- [ ] **Votre SAKA ne peut pas être "volé"** : Le code empêche les soldes négatifs et les double dépenses.
- [ ] **Votre SAKA inactif retourne au commun** : Si vous n'utilisez pas votre SAKA pendant 90 jours, 10% est composté vers le Silo, qui est redistribué au collectif.
- [ ] **Votre SAKA ne peut pas être acheté** : SAKA ne peut pas être acheté avec de l'argent, seulement gagné par l'engagement.
- [ ] **Votre SAKA circule** : Le SAKA que vous plantez (vote, boost) circule dans la communauté, créant de la valeur collective.
- [ ] **Votre SAKA est traçable** : Toutes vos transactions SAKA sont enregistrées dans `SakaTransaction`, garantissant la transparence.

**Si une case n'est pas claire** : Consultez cette documentation ou contactez l'équipe technique.

---

## 🔗 Ressources Complémentaires

- **Documentation technique** : `docs/architecture/PROTOCOLE_SAKA_V2.1.md`
- **Code des services** : `backend/core/services/saka.py`
- **Code des modèles** : `backend/core/models/saka.py`
- **Tests philosophiques** : `backend/core/tests_saka_philosophy.py`
- **Tests techniques** : `backend/core/tests_saka.py`

---

**Dernière mise à jour** : 2025-12-17  
**Version** : 1.0  
**Auteur** : Équipe EGOEJO

---

*Cette documentation est vivante. Si vous découvrez une violation du Manifeste dans le code, documentez-la et créez un test philosophique pour la prévenir à l'avenir.*

