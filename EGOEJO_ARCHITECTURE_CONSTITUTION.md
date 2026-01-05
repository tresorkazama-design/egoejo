# 🏛️ EGOEJO : Architecture & Constitution Technique

**Document Fondateur pour Transmission d'Équipe**  
**Date** : 2025-01-27  
**Version** : 1.0  
**Public Cible** : CTO / Équipe Technique Externe

---

## 📋 Table des Matières

1. [Principe Fondamental](#principe-fondamental)
2. [Pourquoi SAKA ≠ EUR](#pourquoi-saka--eur)
3. [Pourquoi l'Accumulation est Interdite](#pourquoi-laccumulation-est-interdite)
4. [Protection Philosophique dans le Code](#protection-philosophique-dans-le-code)
5. [Garde-Fous : Tests de Compliance](#garde-fous--tests-de-compliance)
6. [Architecture Technique](#architecture-technique)
7. [Points d'Attention Critiques](#points-dattention-critiques)

---

## 🎯 Principe Fondamental

**La structure relationnelle (SAKA) prime toujours sur la structure instrumentale (EUR).**

EGOEJO est une plateforme hybride qui gère deux systèmes monétaires **strictement séparés** :

- **SAKA** : Monnaie interne d'engagement (structure relationnelle, Yin)
- **EUR** : Monnaie réelle (structure instrumentale, Yang)

**Cette séparation n'est pas cosmétique. Elle est encodée dans le code, testée automatiquement, et bloquante en CI/CD.**

---

## 🔒 Pourquoi SAKA ≠ EUR

### Raison 1 : Nature Ontologique Différente

**SAKA** est une **monnaie interne d'engagement**, non-financière, non-monétaire :
- Unité : **Grains SAKA** (entiers positifs)
- Usage : Boost de projets, votes, engagement communautaire
- **Aucune valeur fiduciaire** : Le SAKA ne peut pas être converti en EUR

**EUR** est une **monnaie réelle**, instrumentale :
- Unité : **Euros** (décimales à 2 chiffres)
- Usage : Dons, investissements (V2.0 dormant)
- **Valeur fiduciaire** : Transactions via Stripe, escrow

### Raison 2 : Protection Juridique

Si SAKA était convertible en EUR, il deviendrait :
- Un **instrument financier** (réglementation AMF applicable)
- Une **monnaie électronique** (réglementation DSP2 applicable)

**Conséquence** : EGOEJO nécessiterait des agréments bancaires, des licences financières, et serait soumis à une réglementation stricte.

**Solution** : Le SAKA est explicitement défini comme **NON-FINANCIER** et **NON-MONÉTAIRE** dans le code et les tests.

### Raison 3 : Protection Philosophique

Le SAKA représente l'**engagement relationnel** (Yin), pas l'**accumulation matérielle** (Yang).

Si SAKA = EUR, alors :
- L'engagement devient monnayable
- La relation devient transactionnelle
- La mission "dédiée au vivant" est trahie

**Solution** : Aucune conversion possible, encodée dans le code.

---

## 🚫 Pourquoi l'Accumulation est Interdite

### Raison 1 : Circulation Obligatoire

Le SAKA doit **circuler**, pas s'accumuler. L'accumulation crée :
- Des inégalités relationnelles
- Une dérive vers l'accumulation passive
- Une trahison de la mission "dédiée au vivant"

**Mécanisme** : **Compostage obligatoire** après X jours d'inactivité.

### Raison 2 : Redistribution Équitable

Le SAKA composté retourne au **Silo Commun**, qui est redistribué équitablement aux wallets actifs.

**Mécanisme** : **Redistribution périodique** du Silo vers les wallets éligibles.

### Raison 3 : Anti-Accumulation Structurelle

Le code empêche l'accumulation via :
- **Limites quotidiennes** : Max X récoltes par jour par raison
- **Compostage automatique** : SAKA inactif → Silo
- **Redistribution obligatoire** : Silo → Wallets actifs

---

## 🛡️ Protection Philosophique dans le Code

### 1. Modèles Django (Séparation Structurelle)

**Fichier** : `backend/core/models/saka.py`

```python
class SakaWallet(models.Model):
    """Portefeuille SAKA - Strictement séparé de UserWallet (EUR)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField(default=0)  # Grains SAKA (entiers)
    # Aucune ForeignKey vers UserWallet (EUR)
```

**Fichier** : `backend/finance/models.py`

```python
class UserWallet(models.Model):
    """Portefeuille EUR - Strictement séparé de SakaWallet (SAKA)"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2)  # Euros (décimales)
    # Aucune ForeignKey vers SakaWallet (SAKA)
```

**Protection** : Aucune relation directe entre `SakaWallet` et `UserWallet`. Aucune conversion possible au niveau modèle.

### 2. Services (Séparation Fonctionnelle)

**Fichier** : `backend/core/services/saka.py`

```python
def harvest_saka(user, reason: SakaReason, amount: Optional[int] = None):
    """
    Récolte SAKA - Aucune conversion EUR possible.
    Raisons valides uniquement : CONTENT_READ, POLL_VOTE, etc.
    """
    # Aucune fonction de conversion SAKA ↔ EUR
```

**Fichier** : `backend/finance/services.py`

```python
def pledge_funds(user, amount: Decimal, project_id: int):
    """
    Engagement EUR - Aucune conversion SAKA possible.
    Transactions via Stripe uniquement.
    """
    # Aucune fonction de conversion EUR ↔ SAKA
```

**Protection** : Aucune fonction de conversion dans les services. Les services SAKA et EUR sont dans des modules séparés.

### 3. Compostage Automatique (Anti-Accumulation)

**Fichier** : `backend/core/services/saka.py`

```python
def run_saka_compost_cycle(dry_run: bool = False, source: str = "celery") -> Dict:
    """
    Composte le SAKA inactif (après X jours d'inactivité).
    Le SAKA composté retourne au Silo Commun.
    """
    # Calcul du SAKA à composter
    # Transfert vers SakaSilo
    # Log de compostage
```

**Protection** : Le compostage est **automatique** et **obligatoire**. Aucun wallet ne peut accumuler indéfiniment.

### 4. Redistribution Équitable (Circulation Obligatoire)

**Fichier** : `backend/core/services/saka.py`

```python
def redistribute_saka_silo(rate: float | None = None) -> Dict:
    """
    Redistribue le Silo Commun vers les wallets éligibles.
    Redistribution équitable (division entière).
    """
    # Calcul du SAKA à redistribuer
    # Distribution équitable aux wallets actifs
    # Mise à jour du Silo
```

**Protection** : Le Silo doit être redistribué. Aucune accumulation possible du Silo.

### 5. Frontend (Affichage Non-Monétaire)

**Fichier** : `frontend/frontend/src/utils/saka.ts`

```typescript
export const formatSakaAmount = (amount: number | string): string => {
  // Format : "X grains" (jamais "X €")
  return `${numAmount.toLocaleString('fr-FR')} grains`;
};

export const containsMonetarySymbol = (text: string): boolean => {
  // Détecte les symboles monétaires (€, $, etc.)
  // Utilisé pour empêcher l'affichage monétaire du SAKA
};
```

**Protection** : Le SAKA est toujours affiché comme "grains", jamais comme monnaie.

### 6. Signaux Django (Protection Admin)

**Fichier** : `backend/core/models/saka.py`

```python
@receiver(post_save, sender=SakaWallet)
def log_saka_wallet_changes(sender, instance, created, **kwargs):
    """
    Log les modifications directes du solde SakaWallet.
    Détecte les contournements via Django Admin.
    """
    if not created and instance.pk:
        # Log toute modification directe du solde
        logger.warning(
            f"Modification directe suspecte du SakaWallet..."
        )
```

**Protection** : Toute modification directe du solde SAKA (ex: via Django Admin) est loggée comme suspecte.

---

## ✅ Garde-Fous : Tests de Compliance

### Tests Automatiques Bloquants

**Répertoire** : `backend/tests/compliance/`

Tous les tests de compliance sont tagués `@egoejo_compliance` et sont **bloquants en CI/CD**.

### Test 1 : Aucune Conversion SAKA ↔ EUR

**Fichier** : `backend/tests/compliance/test_no_saka_eur_conversion.py`

```python
@pytest.mark.egoejo_compliance
def test_aucune_fonction_conversion_saka_vers_eur():
    """
    VIOLATION DU MANIFESTE EGOEJO si :
    Une fonction calcule un taux de conversion SAKA vers EUR.
    """
    # Scan du code pour détecter les fonctions de conversion
    # Vérification des patterns interdits
```

**Garde-Fou** : Aucune fonction ne peut convertir SAKA en EUR ou vice versa.

### Test 2 : Anti-Accumulation

**Fichier** : `backend/tests/compliance/test_no_saka_accumulation.py`

```python
@pytest.mark.egoejo_compliance
def test_compostage_obligatoire_apres_inactivite():
    """
    VIOLATION DU MANIFESTE EGOEJO si :
    Un wallet peut accumuler du SAKA indéfiniment sans compostage.
    """
    # Vérification que le compostage s'applique après X jours
    # Vérification que le Silo est alimenté
```

**Garde-Fou** : L'accumulation est impossible. Le compostage est obligatoire.

### Test 3 : Redistribution Obligatoire

**Fichier** : `backend/tests/compliance/test_silo_redistribution.py`

```python
@pytest.mark.egoejo_compliance
def test_redistribution_obligatoire_du_silo():
    """
    VIOLATION DU MANIFESTE EGOEJO si :
    Le Silo peut accumuler du SAKA sans redistribution.
    """
    # Vérification que le Silo est redistribué
    # Vérification de la redistribution équitable
```

**Garde-Fou** : Le Silo doit être redistribué. Aucune accumulation possible.

### Test 4 : Séparation Structurelle

**Fichier** : `backend/tests/compliance/test_saka_eur_separation.py`

```python
@pytest.mark.egoejo_compliance
def test_aucune_relation_directe_saka_eur():
    """
    VIOLATION DU MANIFESTE EGOEJO si :
    Une ForeignKey lie SakaWallet et UserWallet.
    """
    # Vérification des modèles Django
    # Vérification de l'absence de relations directes
```

**Garde-Fou** : Aucune relation directe entre SAKA et EUR au niveau modèle.

### CI/CD Bloquante

**Fichier** : `.github/workflows/egoejo-compliance.yml`

```yaml
jobs:
  compliance_audit:
    runs-on: ubuntu-latest
    steps:
      - name: Run compliance tests
        run: |
          pytest tests/compliance/ -v --tb=short --strict-markers
```

**Garde-Fou** : Les tests de compliance sont **bloquants** en CI/CD. Aucun merge possible si les tests échouent.

### Pre-commit Hook

**Fichier** : `.git/hooks/pre-commit`

```bash
# Run backend compliance tests
pytest tests/compliance/ -v --tb=short --strict-markers
BACKEND_STATUS=$?

if [ $BACKEND_STATUS -ne 0 ]; then
    echo "Backend compliance tests FAILED. Aborting commit."
    exit 1
fi
```

**Garde-Fou** : Aucun commit possible si les tests de compliance échouent.

---

## 🏗️ Architecture Technique

### Structure des Modules

```
backend/
├── core/
│   ├── models/
│   │   └── saka.py          # Modèles SAKA (SakaWallet, SakaTransaction, SakaSilo)
│   ├── services/
│   │   └── saka.py          # Services SAKA (harvest, spend, compost, redistribute)
│   └── api/
│       └── saka_views.py    # Endpoints API SAKA
├── finance/
│   ├── models.py            # Modèles EUR (UserWallet, WalletTransaction)
│   └── services.py          # Services EUR (pledge, release, etc.)
└── tests/
    └── compliance/          # Tests de compliance (bloquants)
```

### Flux de Données

**SAKA** :
1. Récolte → `harvest_saka()` → `SakaWallet.balance` ↑
2. Dépense → `spend_saka()` → `SakaWallet.balance` ↓
3. Compostage → `run_saka_compost_cycle()` → `SakaSilo.total_balance` ↑
4. Redistribution → `redistribute_saka_silo()` → `SakaWallet.balance` ↑ (wallets actifs)

**EUR** :
1. Engagement → `pledge_funds()` → `EscrowContract` → `UserWallet.balance` ↓
2. Libération → `release_escrow()` → `UserWallet.balance` ↑ (projet)

**Aucun flux SAKA ↔ EUR** : Les deux systèmes sont strictement séparés.

---

## ⚠️ Points d'Attention Critiques

### 1. Ne Jamais Créer de Fonction de Conversion

**Interdit** :
```python
# ❌ INTERDIT
def convert_saka_to_eur(saka_amount: int) -> Decimal:
    return Decimal(saka_amount) * EXCHANGE_RATE
```

**Autorisé** :
```python
# ✅ AUTORISÉ
def harvest_saka(user, reason: SakaReason, amount: Optional[int] = None):
    # Récolte SAKA uniquement
```

### 2. Ne Jamais Afficher SAKA comme Monnaie

**Interdit** :
```typescript
// ❌ INTERDIT
const display = `${sakaAmount} €`;
```

**Autorisé** :
```typescript
// ✅ AUTORISÉ
const display = formatSakaAmount(sakaAmount); // "100 grains"
```

### 3. Ne Jamais Désactiver le Compostage

**Interdit** :
```python
# ❌ INTERDIT
SAKA_COMPOST_ENABLED = False  # En production
```

**Autorisé** :
```python
# ✅ AUTORISÉ
SAKA_COMPOST_ENABLED = True  # Toujours activé en production
```

### 4. Ne Jamais Accumuler le Silo

**Interdit** :
```python
# ❌ INTERDIT
def redistribute_saka_silo(rate: float = 0.0):  # rate=0 = pas de redistribution
    pass
```

**Autorisé** :
```python
# ✅ AUTORISÉ
def redistribute_saka_silo(rate: float = 0.05):  # 5% redistribué
    # Redistribution obligatoire
```

### 5. Toujours Exécuter les Tests de Compliance

**Interdit** :
```bash
# ❌ INTERDIT
pytest tests/compliance/ --ignore  # Ignorer les tests de compliance
```

**Autorisé** :
```bash
# ✅ AUTORISÉ
pytest tests/compliance/ -v  # Toujours exécuter les tests de compliance
```

---

## 📚 Références Techniques

### Tests de Compliance

- `backend/tests/compliance/test_no_saka_eur_conversion.py` - Aucune conversion SAKA ↔ EUR
- `backend/tests/compliance/test_no_saka_accumulation.py` - Anti-accumulation
- `backend/tests/compliance/test_silo_redistribution.py` - Redistribution obligatoire
- `backend/tests/compliance/test_saka_eur_separation.py` - Séparation structurelle

### Services Critiques

- `backend/core/services/saka.py` - Services SAKA (harvest, spend, compost, redistribute)
- `backend/finance/services.py` - Services EUR (pledge, release)

### Modèles Critiques

- `backend/core/models/saka.py` - Modèles SAKA (SakaWallet, SakaTransaction, SakaSilo)
- `backend/finance/models.py` - Modèles EUR (UserWallet, WalletTransaction)

### Protection Frontend

- `frontend/frontend/src/utils/saka.ts` - Formatage SAKA (non-monétaire)

---

## 🎯 Conclusion

**EGOEJO est une plateforme hybride qui gère deux systèmes monétaires strictement séparés.**

Cette séparation n'est pas cosmétique. Elle est :
- **Encodée dans le code** (modèles, services, frontend)
- **Testée automatiquement** (tests de compliance bloquants)
- **Protégée en CI/CD** (GitHub Actions, pre-commit hooks)
- **Documentée juridiquement** (manifeste SAKA/EUR)

**Toute modification qui viole cette séparation sera détectée par les tests de compliance et bloquera le merge.**

**Cette architecture est la constitution technique d'EGOEJO. Elle doit être préservée à tout prix.**

---

**Fin du Document**

*Dernière mise à jour : 2025-01-27*  
*Document fondateur pour transmission d'équipe*

