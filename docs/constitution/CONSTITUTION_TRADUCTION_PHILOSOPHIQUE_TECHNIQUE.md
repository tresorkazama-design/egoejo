# 🏛️ CONSTITUTION EGOEJO
## Traduction Philosophique → Technique

**Version** : 1.0.0  
**Date** : 2025-01-05  
**Hash SHA-256** : `088119f02c70175dac5aa27d7b03f1c76ca53d4f512538d2f17e7a6638dee7c4`  
**Statut** : **ACTIVE ET ENFORCÉE**

---

## 📋 PRÉAMBULE PHILOSOPHIQUE

Cette Constitution traduit les concepts fondamentaux de **Subsistance** (Ghisi/Lescabot) et de **Non-Accumulation** en règles techniques opposables et vérifiables par le code.

### Principes Fondamentaux

1. **Subsistance** : L'économie relationnelle (SAKA) prime sur l'économie instrumentale (EUR)
2. **Non-Accumulation** : Le SAKA circule, ne s'accumule pas, se composte
3. **Inaliénabilité** : Les actifs de la mission ne peuvent être détournés

---

## 🚧 RÈGLE 1 : SÉPARATION SAKA / EUR (Mur de Béton)

### Traduction Technique

**Interdiction Absolue** :
- ❌ Aucune fonction de conversion SAKA ↔ EUR
- ❌ Aucun calcul de taux de change SAKA/EUR
- ❌ Aucun affichage d'équivalent monétaire du SAKA
- ❌ Aucun endpoint API de conversion

**Implémentation** :
```python
# ✅ CONFORME : Séparation stricte
class SakaWallet(models.Model):
    balance = models.DecimalField(...)  # SAKA uniquement
    # Pas de champ EUR, pas de conversion

class UserWallet(models.Model):
    balance = models.DecimalField(...)  # EUR uniquement
    # Pas de champ SAKA, pas de conversion
```

**Vérification Automatique** :
- Pattern regex : `convert.*saka.*eur|saka.*to.*eur|saka.*exchange.*rate`
- Test : `backend/tests/compliance/test_saka_eur_separation.py`
- PR Bot : Bloque toute PR contenant ces patterns

---

## 🚧 RÈGLE 2 : CLAUSE ANTI-CAPTURE (Inaliénabilité)

### Traduction Technique

**Interdiction Absolue** :
- ❌ Aucune extraction de fonds vers des comptes externes sans validation
- ❌ Aucune modification de la mission sans vote unanime
- ❌ Aucune conversion des actifs de la mission en actifs privés

**Implémentation** :
```python
# ✅ CONFORME : Escrow avec validation
class EscrowContract(models.Model):
    status = models.CharField(choices=[
        ('LOCKED', 'Verrouillé - Inaliénable'),
        ('RELEASED', 'Libéré - Validation requise'),
    ])
    
    def release(self, validator_signature):
        # Validation requise pour libérer
        if not self.validate_signature(validator_signature):
            raise ValidationError("Signature invalide")
        self.status = 'RELEASED'
```

**Vérification Automatique** :
- Test : `backend/tests/compliance/test_escrow_inalienability.py`
- Audit : Vérification des transactions sortantes

---

## 🚧 RÈGLE 3 : MÉCANISME DE COMPOSTAGE (Demurrage)

### Traduction Technique

**Obligation Absolue** :
- ✅ Compostage automatique après 90 jours d'inactivité
- ✅ Redistribution vers le Silo communautaire
- ✅ Aucune accumulation infinie possible

**Implémentation** :
```python
# ✅ CONFORME : Compostage automatique
def run_saka_compost_cycle():
    """
    Composte les SAKA inactifs depuis 90 jours.
    Redistribue vers le Silo communautaire.
    """
    inactive_wallets = SakaWallet.objects.filter(
        last_activity_date__lt=timezone.now() - timedelta(days=90)
    )
    
    for wallet in inactive_wallets:
        composted = wallet.balance * Decimal('0.1')  # 10% composté
        wallet.balance -= composted
        SakaSilo.objects.create(
            amount=composted,
            source_wallet=wallet,
            reason='COMPOST_AUTOMATIC'
        )
        wallet.save()
```

**Vérification Automatique** :
- Test : `backend/tests/compliance/test_saka_compost.py`
- Cron : Exécution quotidienne du compostage
- Monitoring : Alertes si compostage désactivé

---

## 🛡️ PROTECTION AUTOMATIQUE

### GitHub Actions PR Bot

**Fichier** : `.github/workflows/egoejo-pr-bot.yml`

**Vérifications** :
1. ✅ Absence de conversion SAKA ↔ EUR
2. ✅ Absence de mécanismes de rendement financier
3. ✅ Priorité de la structure relationnelle (SAKA)
4. ✅ Anti-accumulation SAKA (compostage actif)
5. ✅ Cycle SAKA incompressible

**Action** : **BLOQUE** la PR si violations détectées

### Pre-commit Hook

**Fichier** : `.git/hooks/pre-commit-egoejo-guardian`

**Vérifications** : Identiques au PR Bot

**Action** : **BLOQUE** le commit si violations détectées

---

## 📊 EXEMPLES DE VIOLATIONS

### ❌ VIOLATION 1 : Conversion SAKA → EUR

```python
# ❌ INTERDIT
def convert_saka_to_eur(saka_amount):
    rate = get_saka_eur_rate()
    return saka_amount * rate
```

**Raison** : Conversion SAKA ↔ EUR interdite par la Constitution

---

### ❌ VIOLATION 2 : Désactivation Compostage

```python
# ❌ INTERDIT
ENABLE_SAKA_COMPOST = False  # Désactiver compostage
```

**Raison** : Compostage obligatoire pour éviter l'accumulation

---

### ❌ VIOLATION 3 : Extraction Non Validée

```python
# ❌ INTERDIT
def extract_funds(amount):
    escrow.balance -= amount  # Sans validation
    external_account.balance += amount
```

**Raison** : Inaliénabilité - validation requise

---

## ✅ EXEMPLES CONFORMES

### ✅ CONFORME 1 : Séparation SAKA/EUR

```python
# ✅ CONFORME
def get_saka_balance(user):
    wallet = SakaWallet.objects.get(user=user)
    return {
        'balance': wallet.balance,
        'total_harvested': wallet.total_harvested,
    }
    # Pas d'équivalent EUR, pas de conversion
```

---

### ✅ CONFORME 2 : Compostage Automatique

```python
# ✅ CONFORME
@periodic_task(run_every=crontab(hours=0, minute=0))
def daily_compost_cycle():
    run_saka_compost_cycle()  # Compostage automatique
    redistribute_saka_silo()  # Redistribution
```

---

### ✅ CONFORME 3 : Escrow Inaliénable

```python
# ✅ CONFORME
def release_escrow(contract_id, validator_signature):
    contract = EscrowContract.objects.get(id=contract_id)
    if not contract.validate_signature(validator_signature):
        raise ValidationError("Signature invalide")
    contract.status = 'RELEASED'
    contract.save()
```

---

## 🚨 SANCTIONS

### Niveau 1 : Avertissement
- **Violation mineure** : Pattern détecté mais non exécuté
- **Action** : Commentaire PR avec avertissement

### Niveau 2 : Blocage PR
- **Violation majeure** : Code non conforme détecté
- **Action** : PR bloquée, commit refusé

### Niveau 3 : Rejet Automatique
- **Violation critique** : Tentative de conversion SAKA ↔ EUR
- **Action** : PR automatiquement fermée, commit rejeté

---

## 📚 RÉFÉRENCES

- **Manifeste EGOEJO** : `docs/philosophie/MANIFESTE_EGOEJO.md`
- **Architecture SAKA** : `docs/architecture/PROTOCOLE_SAKA_V2.1.md`
- **Tests de Conformité** : `backend/tests/compliance/`
- **Constitution Juridique** : `docs/legal/CONSTITUTION_JURIDIQUE_FINALE_EGOEJO.md`

---

**Cette Constitution est ENFORCÉE par des vérifications automatiques.  
Aucune exception n'est autorisée.  
La trahison du projet est techniquement impossible.**

---

*Dernière mise à jour : 2025-01-05*  
*Hash SHA-256 : `088119f02c70175dac5aa27d7b03f1c76ca53d4f512538d2f17e7a6638dee7c4`*

