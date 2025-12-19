# Constitution EGOEJO : Exécutable par le Code

> **La philosophie EGOEJO n'est pas une promesse marketing. Elle est encodée dans le logiciel et vérifiée automatiquement.**

## 📋 Table des matières

1. [Double Structure Économique](#double-structure-économique)
2. [Règles Absolues](#règles-absolues)
3. [Vérification Automatique](#vérification-automatique)
4. [Exemples de Violations](#exemples-de-violations)
5. [Exemples de Conformité](#exemples-de-conformité)
6. [Références Techniques](#références-techniques)

---

## Double Structure Économique

### Structure Relationnelle (SAKA) — PRIORITAIRE

**Définition** : La structure relationnelle est le cœur d'EGOEJO. Elle gère l'engagement, le don, la circulation et les cycles de valeur.

**Cycle complet** : Récolte → Usage → Compost → Silo → Redistribution

**Caractéristiques** :
- Anti-accumulation absolue (compostage obligatoire)
- Circulation permanente (redistribution du Silo)
- Non négociable (aucune étape ne peut être supprimée)

**Fichiers concernés** :
- `backend/core/services/saka.py`
- `backend/core/models/saka.py`
- `backend/core/api/saka_views.py`
- `frontend/**/saka*`

**Vérification** :
- Tests CI : `backend/tests/compliance/test_saka_cycle_incompressible.py`
- PR Bot : Règle `saka_cycle_mandatory` dans `.egoejo/guardian.yml`

---

### Structure Instrumentale (EUR) — DORMANTE

**Définition** : La structure instrumentale gère la finance, les wallets EUR, les escrows et l'investissement. Elle est **dormante** par défaut.

**Caractéristiques** :
- Toujours derrière feature flag (`ENABLE_INVESTMENT_FEATURES`)
- Jamais souveraine (ne peut pas contraindre SAKA)
- Strictement séparée de SAKA

**Fichiers concernés** :
- `backend/finance/**`
- `backend/investment/**`
- `frontend/**/finance*`

**Vérification** :
- Tests CI : `backend/tests/compliance/test_banque_dormante_strict.py`
- PR Bot : Règles `no_conversion`, `saka_priority` dans `.egoejo/guardian.yml`

---

## Règles Absolues

### Règle 1 : Aucune conversion SAKA ↔ EUR

**Principe** : SAKA et EUR sont strictement séparés. Aucune conversion n'est autorisée.

**Patterns interdits** :
- `convert_saka_to_eur()` ou `convert_eur_to_saka()`
- `saka_price`, `saka_exchange_rate`
- Affichage monétaire du SAKA (€, euro, currency)

**Vérification** :
- **Test CI** : `backend/tests/compliance/test_saka_eur_separation.py::test_aucune_conversion_saka_eur_dans_code`
- **PR Bot** : Règle `no_conversion` (CRITICAL) dans `.egoejo/guardian.yml`

**Exemple de violation** :
```python
# ❌ VIOLATION
def convert_saka_to_eur(saka_amount):
    return saka_amount * 0.01  # 1 SAKA = 0.01 EUR
```

**Exemple de conformité** :
```python
# ✅ CONFORME
def get_saka_balance(user):
    wallet = user.saka_wallet
    return wallet.balance  # Retourne des grains SAKA, pas d'EUR
```

---

### Règle 2 : Aucun rendement financier basé sur SAKA

**Principe** : Le SAKA est une monnaie d'engagement, pas d'investissement. Aucun rendement financier n'est autorisé.

**Patterns interdits** :
- `saka_interest_rate`, `saka_dividend`
- `calculate_saka_yield()`, `saka_roi`
- Champs de rendement dans modèles SAKA

**Vérification** :
- **Test CI** : `backend/tests/compliance/test_saka_no_financial_return.py::test_aucun_rendement_financier_saka`
- **PR Bot** : Règle `no_financial_return` (CRITICAL) dans `.egoejo/guardian.yml`

**Exemple de violation** :
```python
# ❌ VIOLATION
def calculate_saka_interest(wallet, rate):
    return wallet.balance * rate  # Rendement financier interdit
```

**Exemple de conformité** :
```python
# ✅ CONFORME
def harvest_saka(user, reason, amount):
    wallet = user.saka_wallet
    wallet.balance += amount  # Récolte d'engagement, pas de rendement
    wallet.save()
```

---

### Règle 3 : Le cycle SAKA est non négociable

**Principe** : Le cycle complet (Récolte → Usage → Compost → Silo → Redistribution) est obligatoire. Aucune étape ne peut être supprimée ou contournée.

**Patterns interdits** :
- `disable_compost()`, `skip_compost()`, `bypass_compost()`
- Conditions pour éviter le compostage
- Suppression du Silo ou de la redistribution

**Vérification** :
- **Test CI** : `backend/tests/compliance/test_saka_cycle_incompressible.py::test_compostage_ne_peut_pas_etre_desactive`
- **Test CI** : `backend/tests/compliance/test_saka_cycle_incompressible.py::test_silo_doit_etre_alimente_apres_compost`
- **PR Bot** : Règle `saka_cycle_mandatory` (CRITICAL) dans `.egoejo/guardian.yml`

**Exemple de violation** :
```python
# ❌ VIOLATION
if user.is_premium:
    skip_compost = True  # Contournement interdit
```

**Exemple de conformité** :
```python
# ✅ CONFORME
def run_saka_compost_cycle():
    # Compostage obligatoire pour tous les wallets inactifs
    wallets = SakaWallet.objects.filter(
        last_activity_date__lt=cutoff,
        balance__gte=min_balance
    )
    for wallet in wallets:
        amount = int(wallet.balance * rate)
        wallet.balance -= amount
        silo.total_balance += amount  # Retour au Silo obligatoire
```

---

### Règle 4 : En cas de conflit : SAKA > EUR

**Principe** : La structure relationnelle (SAKA) est prioritaire. La structure instrumentale (EUR) ne peut jamais contraindre SAKA.

**Patterns interdits** :
- Conditions `if ENABLE_INVESTMENT_FEATURES` qui désactivent SAKA
- Logique qui privilégie EUR sur SAKA
- Dépendances SAKA → EUR

**Vérification** :
- **Test CI** : `backend/tests/compliance/test_banque_dormante_strict.py::test_structure_instrumentale_ne_contraint_pas_relationnelle`
- **PR Bot** : Règle `saka_priority` (HIGH) dans `.egoejo/guardian.yml`

**Exemple de violation** :
```python
# ❌ VIOLATION
if settings.ENABLE_INVESTMENT_FEATURES:
    # Désactiver SAKA si investment est activé
    ENABLE_SAKA = False
```

**Exemple de conformité** :
```python
# ✅ CONFORME
# SAKA fonctionne indépendamment de ENABLE_INVESTMENT_FEATURES
def harvest_saka(user, reason, amount):
    if not is_saka_enabled():  # Vérifie uniquement ENABLE_SAKA
        return None
    # ... logique SAKA indépendante
```

---

### Règle 5 : La banque dormante ne touche pas SAKA

**Principe** : Les modules finance/investment ne doivent jamais importer ou utiliser SAKA.

**Patterns interdits** :
- `from core.services.saka import *` dans `finance/` ou `investment/`
- `SakaWallet`, `SakaTransaction` dans services finance
- ForeignKey vers SAKA dans modèles finance

**Vérification** :
- **Test CI** : `backend/tests/compliance/test_banque_dormante_ne_touche_pas_saka.py::test_finance_ne_importe_pas_saka`
- **Test CI** : `backend/tests/compliance/test_banque_dormante_strict.py::test_aucune_feature_financiere_impacte_saka`
- **PR Bot** : Règles `no_eur_reference_in_saka_services` dans `.egoejo/guardian.yml`

**Exemple de violation** :
```python
# ❌ VIOLATION (dans finance/services.py)
from core.services.saka import harvest_saka

def pledge_funds(user, project, amount):
    # Donner du SAKA en bonus
    harvest_saka(user, SakaReason.INVEST_BONUS, amount=100)
```

**Exemple de conformité** :
```python
# ✅ CONFORME (dans finance/services.py)
# Aucun import SAKA
def pledge_funds(user, project, amount):
    wallet = UserWallet.objects.get(user=user)
    wallet.balance -= amount
    wallet.save()
    # Aucune référence à SAKA
```

---

## Vérification Automatique

### 🤖 PR Bot : EGOEJO Guardian

**Rôle** : Analyse automatiquement chaque Pull Request pour détecter les violations de la constitution.

**Fichier** : `.egoejo/guardian.py`

**Fonctionnement** :
1. Analyse le diff de la PR
2. Détecte les patterns interdits (regex)
3. Classifie les fichiers (SAKA vs EUR)
4. Vérifie les tests manquants
5. Génère un verdict : 🟢 / 🟡 / 🔴

**Intégration** : GitHub Actions (`.github/workflows/egoejo-guardian.yml`)

**Verdicts** :
- 🟢 **COMPATIBLE EGOEJO** : Aucune violation, tests présents
- 🟡 **COMPATIBLE SOUS CONDITIONS** : Violations importantes uniquement, tests manquants
- 🔴 **NON COMPATIBLE EGOEJO** : Violation critique = blocage immédiat

**Exemple de sortie** :
```
## 🔴 NON COMPATIBLE EGOEJO

❌ **No Conversion** : backend/core/services/saka.py (ligne 42)
❌ **Pattern détecté** : convert_saka_to_eur(saka_amount)

**ACTION REQUISE** : SUPPRIMER toute logique de conversion SAKA ↔ EUR.
```

**Documentation** :
- Configuration : `.egoejo/guardian.yml`
- Critères : `.egoejo/CRITERES_LABELS.md`
- Exemples : `.egoejo/EXEMPLES_SORTIE_LABELS.md`

---

### 🧪 Tests CI : Tests de Conformité

**Rôle** : Vérifient que le code respecte la constitution EGOEJO à chaque commit.

**Emplacement** : `backend/tests/compliance/`

**Fonctionnement** :
1. Analyse le code source (pas de mocks)
2. Détecte les violations par patterns regex
3. Vérifie les comportements fonctionnels
4. Échoue si une violation est détectée

**Tests disponibles** :

#### Séparation SAKA ↔ EUR
- `test_saka_eur_separation.py` (4 tests)
  - `test_aucune_conversion_saka_eur_dans_code`
  - `test_aucun_affichage_monetaire_saka`
  - `test_aucune_reference_eur_dans_services_saka`
  - `test_aucune_reference_eur_dans_modeles_saka`

#### Pas de rendement financier
- `test_saka_no_financial_return.py` (2 tests)
  - `test_aucun_rendement_financier_saka`
  - `test_aucun_champ_rendement_dans_modeles_saka`

#### Cycle SAKA incompressible
- `test_saka_cycle_incompressible.py` (3 tests)
  - `test_compostage_ne_peut_pas_etre_desactive`
  - `test_silo_doit_etre_alimente_apres_compost`
  - `test_cycle_saka_incompressible`

#### Banque dormante
- `test_banque_dormante_ne_touche_pas_saka.py` (4 tests)
  - `test_finance_ne_importe_pas_saka`
  - `test_finance_ne_reference_pas_saka`
  - `test_finance_modeles_ne_reference_pas_saka`
  - `test_investment_ne_touche_pas_saka`

- `test_banque_dormante_strict.py` (8 tests)
  - `test_pledge_funds_bloque_equity_si_flag_desactive`
  - `test_saka_non_impacte_par_finance_desactivee`
  - `test_aucun_impact_saka_si_finance_desactivee`
  - `test_tous_acces_investment_proteges_par_feature_flag`
  - `test_aucune_feature_financiere_impacte_saka`
  - `test_escrow_ne_impacte_pas_saka`
  - `test_aucune_feature_financiere_sans_flag_actif`
  - `test_structure_instrumentale_ne_contraint_pas_relationnelle`

**Exécution** :
```bash
# Tous les tests de conformité
python -m pytest backend/tests/compliance/ -v

# Un test spécifique
python -m pytest backend/tests/compliance/test_saka_eur_separation.py -v
```

**Résultat** : Un seul échec = CI rouge (blocage du merge)

---

## Exemples de Violations

### Violation 1 : Conversion SAKA ↔ EUR

**Code** :
```python
# backend/core/services/saka.py
def convert_saka_to_eur(saka_amount):
    """Convertit des grains SAKA en euros"""
    return saka_amount * 0.01  # 1 SAKA = 0.01 EUR
```

**Détection** :
- **PR Bot** : Pattern `convert.*saka.*eur` détecté → 🔴 NON COMPATIBLE
- **Test CI** : `test_aucune_conversion_saka_eur_dans_code` → FAILED

**Action requise** : Supprimer la fonction de conversion.

---

### Violation 2 : Désactivation du compostage

**Code** :
```python
# backend/core/services/saka.py
def run_saka_compost_cycle():
    if user.is_premium:
        skip_compost = True  # Les utilisateurs premium ne compostent pas
        return
    # ... compostage normal
```

**Détection** :
- **PR Bot** : Pattern `skip.*compost` détecté → 🔴 NON COMPATIBLE
- **Test CI** : `test_compostage_ne_peut_pas_etre_desactive` → FAILED

**Action requise** : Supprimer la condition de contournement. Le compostage est obligatoire pour tous.

---

### Violation 3 : Feature financière impacte SAKA

**Code** :
```python
# backend/finance/services.py
from core.services.saka import harvest_saka

def pledge_funds(user, project, amount):
    # Donner du SAKA en bonus pour chaque don
    harvest_saka(user, SakaReason.INVEST_BONUS, amount=100)
    # ... logique finance
```

**Détection** :
- **PR Bot** : Import SAKA dans finance détecté → 🔴 NON COMPATIBLE
- **Test CI** : `test_aucune_feature_financiere_impacte_saka` → FAILED

**Action requise** : Supprimer l'import et toute référence SAKA dans finance.

---

### Violation 4 : Feature investment sans flag

**Code** :
```python
# backend/investment/views.py
class ShareholderRegisterViewSet(viewsets.ReadOnlyModelViewSet):
    # Pas de vérification de ENABLE_INVESTMENT_FEATURES
    queryset = ShareholderRegister.objects.all()
```

**Détection** :
- **PR Bot** : Pas de vérification de feature flag → 🟡 COMPATIBLE SOUS CONDITIONS
- **Test CI** : `test_tous_acces_investment_proteges_par_feature_flag` → FAILED

**Action requise** : Ajouter `permission_classes = [IsInvestmentFeatureEnabled]`.

---

## Exemples de Conformité

### Exemple 1 : Service SAKA conforme

**Code** :
```python
# backend/core/services/saka.py
def harvest_saka(user, reason, amount):
    """Récolter des grains SAKA"""
    if not is_saka_enabled():
        return None
    wallet = get_or_create_wallet(user)
    wallet.balance += amount
    wallet.total_harvested += amount
    wallet.save()
    return SakaTransaction.objects.create(...)
```

**Vérification** :
- ✅ Aucun import finance/investment
- ✅ Aucune conversion SAKA ↔ EUR
- ✅ Aucun rendement financier
- ✅ Fonctionne indépendamment de `ENABLE_INVESTMENT_FEATURES`

**Résultat** : 🟢 COMPATIBLE EGOEJO

---

### Exemple 2 : Service Finance conforme

**Code** :
```python
# backend/finance/services.py
@transaction.atomic
def pledge_funds(user, project, amount, pledge_type='DONATION'):
    """Engager des fonds (don ou investissement)"""
    # Vérification feature flag pour EQUITY
    if pledge_type == 'EQUITY' and not settings.ENABLE_INVESTMENT_FEATURES:
        raise ValidationError("L'investissement n'est pas encore ouvert.")
    
    wallet = UserWallet.objects.select_for_update().get(user=user)
    wallet.balance -= amount
    wallet.save()
    # ... création escrow
    # Aucune référence à SAKA
```

**Vérification** :
- ✅ Feature flag vérifié pour EQUITY
- ✅ Aucun import SAKA
- ✅ Aucune référence SAKA
- ✅ Ne contraint pas SAKA

**Résultat** : 🟢 COMPATIBLE EGOEJO

---

### Exemple 3 : Cycle SAKA complet conforme

**Code** :
```python
# backend/core/services/saka.py
def run_saka_compost_cycle():
    """Composte les wallets inactifs vers le Silo"""
    wallets = SakaWallet.objects.filter(
        last_activity_date__lt=cutoff,
        balance__gte=min_balance
    )
    for wallet in wallets:
        amount = int(wallet.balance * rate)
        wallet.balance -= amount
        wallet.total_composted += amount
        silo.total_balance += amount  # Retour au Silo obligatoire
        wallet.save()
    silo.save()
```

**Vérification** :
- ✅ Compostage obligatoire (pas de condition de skip)
- ✅ Silo alimenté après compost
- ✅ Cycle complet respecté

**Résultat** : 🟢 COMPATIBLE EGOEJO

---

## Références Techniques

### Fichiers de Configuration

- **PR Bot** : `.egoejo/guardian.yml`
- **Critères labels** : `.egoejo/CRITERES_LABELS.md`
- **Exemples sortie** : `.egoejo/EXEMPLES_SORTIE_LABELS.md`

### Tests de Conformité

- **Emplacement** : `backend/tests/compliance/`
- **Exécution** : `python -m pytest backend/tests/compliance/ -v`
- **Documentation** : `backend/tests/compliance/__init__.py`

### Intégration CI/CD

- **GitHub Actions** : `.github/workflows/egoejo-guardian.yml`
- **Exécution** : Automatique sur chaque PR
- **Résultat** : Label + commentaire automatique

### Feature Flags

- **SAKA** : `ENABLE_SAKA` (obligatoire en production)
- **Compostage** : `SAKA_COMPOST_ENABLED` (obligatoire en production)
- **Silo** : `SAKA_SILO_REDIS_ENABLED` (obligatoire en production)
- **Investment** : `ENABLE_INVESTMENT_FEATURES` (dormant par défaut)

---

## Garanties

### Pour les Développeurs

✅ **Aucune violation ne peut être mergée** : Les tests CI bloquent automatiquement

✅ **Feedback immédiat** : Le PR Bot commente chaque PR avec le verdict

✅ **Documentation claire** : Chaque règle est liée à un test ou une règle du bot

✅ **Exemples concrets** : Violations et conformité documentées

### Pour les Partenaires

✅ **Transparence totale** : La constitution est publique et vérifiable

✅ **Pas de promesses vides** : Les règles sont encodées dans le logiciel

✅ **Audit possible** : Tous les tests sont exécutables et reproductibles

### Pour la Gouvernance

✅ **Protection automatique** : Impossible de violer la constitution par erreur

✅ **Traçabilité** : Chaque violation est détectée et documentée

✅ **Évolution contrôlée** : Toute modification doit passer les tests de conformité

---

## Conclusion

**La philosophie EGOEJO n'est pas une déclaration d'intention. Elle est exécutable.**

Chaque règle de la constitution est :
- ✅ **Encodée** dans le code (patterns interdits)
- ✅ **Testée** automatiquement (tests CI)
- ✅ **Vérifiée** à chaque PR (PR Bot)
- ✅ **Documentée** avec exemples

**Un seul échec = CI rouge = Blocage du merge.**

La constitution EGOEJO est **Code-Enforced**.

---

## Questions Fréquentes

### Q : Que se passe-t-il si je viole une règle par erreur ?

**R** : Le PR Bot détectera la violation et bloquera la PR avec un message explicite. Vous devrez corriger avant de pouvoir merger.

### Q : Puis-je désactiver temporairement les tests de conformité ?

**R** : Non. Les tests de conformité sont obligatoires et ne peuvent pas être désactivés. C'est une garantie de protection de la constitution.

### Q : Comment savoir si mon code est conforme ?

**R** : Exécutez les tests de conformité localement :
```bash
python -m pytest backend/tests/compliance/ -v
```

### Q : Que faire si le PR Bot détecte une fausse alerte ?

**R** : Les patterns sont précis, mais si vous pensez qu'il s'agit d'une fausse alerte, ouvrez une issue avec le contexte. Les patterns peuvent être affinés si nécessaire.

### Q : Les tests de conformité ralentissent-ils le CI ?

**R** : Non. Les tests de conformité sont rapides (analyse de code source) et s'exécutent en quelques secondes.

---

**Dernière mise à jour** : 2025-12-18

**Version** : 1.0

**Mainteneurs** : Équipe EGOEJO

