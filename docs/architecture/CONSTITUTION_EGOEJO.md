# 🏛️ CONSTITUTION EGOEJO
## Règles Absolues et Non-Négociables

**Date de création** : 2025-12-19  
**Statut** : **ACTIVE ET ENFORCÉE**

---

## 📋 PRÉAMBULE

Le projet EGOEJO repose sur une **DOUBLE STRUCTURE ÉCONOMIQUE NON-NÉGOCIABLE** :

1. **Structure Relationnelle (Souveraine, Prioritaire)**
   - SAKA : Engagement, don, réputation
   - Cycle : Récolte → Usage → Compost → Silo → Redistribution
   - Règle : Anti-accumulation absolue

2. **Structure Instrumentale (Subordonnée, Dormante par défaut)**
   - EUR : Finance, paiement, conformité
   - Règle : Peut exister mais ne doit JAMAIS contraindre ou corrompre le SAKA

---

## 🚫 RÈGLES ABSOLUES

### RÈGLE 1 : Aucune Conversion SAKA ↔ EUR

**Interdiction** :
- ❌ Aucune fonction de conversion SAKA → EUR
- ❌ Aucune fonction de conversion EUR → SAKA
- ❌ Aucun calcul de taux de change SAKA/EUR
- ❌ Aucun affichage d'équivalent monétaire du SAKA
- ❌ Aucun endpoint API de conversion

**Justification** :
- SAKA et EUR sont **strictement séparés**
- SAKA est une unité d'engagement **non monétaire**
- EUR est un outil **instrumental** qui ne doit pas corrompre SAKA

**Détection** :
- Patterns interdits : `convert.*saka.*eur`, `saka.*to.*eur`, `saka.*exchange.*rate`, `saka.*price`, `saka.*value.*eur`

---

### RÈGLE 2 : Aucun Rendement Financier sur SAKA

**Interdiction** :
- ❌ Aucun calcul de ROI sur SAKA
- ❌ Aucun calcul de yield sur SAKA
- ❌ Aucun calcul d'intérêt sur SAKA
- ❌ Aucun calcul de dividendes sur SAKA
- ❌ Aucun mécanisme de profit sur SAKA

**Justification** :
- SAKA est une unité d'engagement **non monétaire**
- SAKA ne peut pas générer de **rendement financier**
- SAKA circule, ne s'accumule pas, ne génère pas de profit

**Détection** :
- Patterns interdits : `saka.*roi`, `saka.*yield`, `saka.*interest`, `saka.*dividend`, `saka.*profit`

---

### RÈGLE 3 : Priorité de la Structure Relationnelle (SAKA)

**Interdiction** :
- ❌ Aucune désactivation de SAKA
- ❌ Aucune subordination de SAKA à EUR
- ❌ Aucune condition EUR requise pour SAKA
- ❌ Aucun feature flag SAKA désactivé en production

**Justification** :
- SAKA est la structure **PRIORITAIRE** et **SOUVERAINE**
- SAKA ne peut pas être désactivé ou subordonné à EUR
- En cas de conflit, SAKA **PRIME TOUJOURS**

**Détection** :
- Patterns interdits : `disable.*saka`, `saka.*depends.*on.*eur`, `ENABLE_SAKA.*=.*False`

---

### RÈGLE 4 : Anti-Accumulation Absolue

**Interdiction** :
- ❌ Aucune accumulation infinie de SAKA
- ❌ Aucune désactivation du compostage
- ❌ Aucun contournement du cycle compostage
- ❌ Aucune limite maximale supprimée sans compostage

**Justification** :
- L'accumulation SAKA est **INTERDITE**
- Le compostage est **OBLIGATOIRE** et **NON NÉGOCIABLE**
- Le SAKA doit **CIRCULER**, pas s'accumuler

**Détection** :
- Patterns interdits : `saka.*accumulate.*infinite`, `disable.*compost`, `skip.*compost`, `bypass.*compost`

---

### RÈGLE 5 : Cycle SAKA Incompressible

**Interdiction** :
- ❌ Aucun contournement du cycle SAKA
- ❌ Aucun raccourci Récolte → Usage (sans Compost)
- ❌ Aucun compostage sans alimentation du Silo
- ❌ Aucune redistribution sans compostage préalable

**Justification** :
- Le cycle SAKA est **NON NÉGOCIABLE** : Récolte → Usage → Compost → Silo → Redistribution
- Aucune étape ne peut être supprimée ou contournée
- Le cycle est **INCOMPRESSIBLE**

**Détection** :
- Patterns interdits : `skip.*saka.*cycle`, `bypass.*saka.*cycle`, `compost.*without.*silo`

---

## 🛡️ PROTECTION AUTOMATIQUE

### GitHub Actions PR Bot

**Fichier** : `.github/workflows/pr-bot-egoejo-guardian.yml`

**Vérifications** :
1. ✅ Absence de conversion SAKA ↔ EUR
2. ✅ Absence de mécanismes de rendement financier
3. ✅ Priorité de la structure relationnelle (SAKA)
4. ✅ Anti-accumulation SAKA
5. ✅ Cycle SAKA incompressible

**Action** : **BLOQUE** la PR si violations détectées

---

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

**Raison** : Conversion SAKA ↔ EUR interdite

---

### ❌ VIOLATION 2 : Rendement Financier sur SAKA

```python
# ❌ INTERDIT
def calculate_saka_roi(saka_balance, days):
    interest_rate = 0.05  # 5% par an
    return saka_balance * (interest_rate / 365) * days
```

**Raison** : SAKA ne peut pas générer de rendement financier

---

### ❌ VIOLATION 3 : Désactivation SAKA

```python
# ❌ INTERDIT
if user.has_eur_balance():
    ENABLE_SAKA = False  # Désactiver SAKA si EUR présent
```

**Raison** : SAKA est prioritaire, ne peut pas être désactivé

---

### ❌ VIOLATION 4 : Accumulation Infinie

```python
# ❌ INTERDIT
def harvest_saka(user, amount):
    wallet = get_wallet(user)
    wallet.balance += amount  # Pas de limite, pas de compostage
    wallet.save()
```

**Raison** : Accumulation infinie interdite, compostage obligatoire

---

### ❌ VIOLATION 5 : Contournement Cycle SAKA

```python
# ❌ INTERDIT
def quick_harvest_and_spend(user, amount):
    harvest_saka(user, amount)
    spend_saka(user, amount)
    # Pas de compostage, pas de Silo
```

**Raison** : Cycle SAKA incompressible, toutes les étapes sont obligatoires

---

## ✅ EXEMPLES CONFORMES

### ✅ CONFORME 1 : Séparation SAKA/EUR

```python
# ✅ CONFORME
def get_saka_balance(user):
    wallet = get_wallet(user)
    return {
        'balance': wallet.balance,
        'total_harvested': wallet.total_harvested,
        'total_planted': wallet.total_planted
    }
    # Pas d'équivalent EUR, pas de conversion
```

---

### ✅ CONFORME 2 : Cycle SAKA Complet

```python
# ✅ CONFORME
def run_saka_cycle(user):
    # 1. Récolte
    harvest_saka(user, SakaReason.CONTENT_READ, amount=100)
    
    # 2. Usage
    spend_saka(user, amount=30, reason="project_boost")
    
    # 3. Compost (automatique après inactivité)
    run_saka_compost_cycle()
    
    # 4. Silo alimenté (automatique)
    # 5. Redistribution (automatique)
    redistribute_saka_silo()
```

---

### ✅ CONFORME 3 : Anti-Accumulation

```python
# ✅ CONFORME
def harvest_saka(user, reason, amount):
    wallet = get_wallet(user)
    
    # Vérifier limites anti-farming
    if exceeds_daily_limit(user, reason):
        return None
    
    # Créditer avec traçabilité
    wallet.balance += amount
    wallet.total_harvested += amount
    wallet.last_activity_date = timezone.now()
    wallet.save()
    
    # Le compostage s'appliquera automatiquement après 90 jours d'inactivité
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
- **Architecture SAKA** : `docs/architecture/ARCHITECTURE_SAKA.md`
- **Tests de Conformité** : `backend/tests/compliance/`

---

**Cette Constitution est ENFORCÉE par des vérifications automatiques.  
Aucune exception n'est autorisée.  
La trahison du projet est techniquement impossible.**

---

*Dernière mise à jour : 2025-12-19*

