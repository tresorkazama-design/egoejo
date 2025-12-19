# 🌾 Comment Adopter la Constitution EGOEJO dans Votre Projet

**Version** : 1.0.0  
**Date** : 2025-12-19  
**Badge** : EGOEJO Compliant

---

## 📋 Vue d'Ensemble

La **Constitution EGOEJO** définit une double structure économique non-négociable :
- **Structure Relationnelle (SAKA)** : Souveraine, Prioritaire, Anti-accumulation
- **Structure Instrumentale (EUR)** : Subordonnée, Dormante, Ne doit jamais corrompre le SAKA

Ce guide explique comment adopter cette constitution dans votre projet et obtenir le badge **EGOEJO Compliant**.

---

## 🎯 Étape 1 : Comprendre la Constitution EGOEJO

### Principes Fondamentaux

1. **Séparation Absolue SAKA/EUR**
   - Aucune conversion SAKA ↔ EUR
   - Aucun lien technique entre les deux systèmes
   - Aucune fusion de données

2. **Compostage Obligatoire**
   - Le SAKA inactif DOIT être composté
   - Le compostage retourne au Silo Commun
   - Le Silo redistribue aux utilisateurs actifs

3. **Anti-Accumulation**
   - Pas d'accumulation infinie de SAKA
   - Cycle obligatoire : Récolte → Usage → Compost → Silo → Redistribution

4. **Non-Monétarité du SAKA**
   - Le SAKA n'est pas une monnaie
   - Aucun rendement financier sur SAKA
   - Aucun affichage monétaire du SAKA

---

## 📝 Étape 2 : Créer le Fichier `egoejo.json`

### Emplacement

Créez un fichier `egoejo.json` à la **racine de votre projet**.

### Structure Minimale

```json
{
  "version": "1.0.0",
  "project_name": "Mon Projet",
  "project_url": "https://mon-projet.org",
  "repository_url": "https://github.com/user/mon-projet",
  "constitution_version": "1.0",
  "saka_structure": {
    "enabled": true,
    "compost_enabled": true,
    "compost_inactivity_days": 90,
    "compost_rate": 0.1,
    "compost_min_balance": 50,
    "compost_min_amount": 10,
    "silo_redistribution_enabled": true,
    "silo_redistribution_rate": 0.1
  },
  "separation_rules": {
    "strict_separation": true,
    "no_conversion": true,
    "no_financial_return": true,
    "no_monetary_display": true,
    "relational_structure_priority": true
  }
}
```

### Exemple Complet

Voir `docs/open-source/egoejo-compliant-schema.json` pour le schéma complet avec tous les champs optionnels.

---

## 🔧 Étape 3 : Implémenter les Règles dans Votre Code

### 3.1 - Séparation Technique

**Règle** : Aucun fichier ne doit contenir à la fois des références SAKA et EUR.

**Exemple de Violation** :
```python
# ❌ VIOLATION
from saka.models import SakaWallet
from finance.models import UserWallet

def transfer_saka_to_eur(user, amount):
    saka = SakaWallet.objects.get(user=user)
    eur = UserWallet.objects.get(user=user)
    # ...
```

**Exemple Conforme** :
```python
# ✅ CONFORME - Fichier SAKA uniquement
from saka.models import SakaWallet

def harvest_saka(user, amount):
    wallet = SakaWallet.objects.get(user=user)
    wallet.balance += amount
    wallet.save()
```

```python
# ✅ CONFORME - Fichier EUR uniquement
from finance.models import UserWallet

def deposit_eur(user, amount):
    wallet = UserWallet.objects.get(user=user)
    wallet.balance += amount
    wallet.save()
```

---

### 3.2 - Compostage Obligatoire

**Règle** : Si SAKA est activé, le compostage DOIT être activé.

**Exemple Conforme** :
```python
# ✅ CONFORME
SAKA_ENABLED = True
SAKA_COMPOST_ENABLED = True  # Obligatoire si SAKA_ENABLED = True

def run_compost_cycle():
    if not SAKA_COMPOST_ENABLED:
        raise RuntimeError("Compostage obligatoire si SAKA activé")
    # ...
```

---

### 3.3 - Interdiction de Conversion

**Règle** : Aucune fonction de conversion SAKA ↔ EUR.

**Exemple de Violation** :
```python
# ❌ VIOLATION
def convert_saka_to_eur(saka_amount):
    return saka_amount * 0.01  # Interdit
```

**Exemple Conforme** :
```python
# ✅ CONFORME - Pas de conversion
def get_saka_balance(user):
    wallet = SakaWallet.objects.get(user=user)
    return wallet.balance  # Retourne uniquement le solde SAKA
```

---

### 3.4 - Interdiction de Rendement Financier

**Règle** : Aucun calcul de rendement financier sur SAKA.

**Exemple de Violation** :
```python
# ❌ VIOLATION
def calculate_saka_interest(balance, rate):
    return balance * rate  # Interdit
```

---

### 3.5 - Interdiction d'Affichage Monétaire

**Règle** : Aucun affichage du SAKA avec symbole monétaire.

**Exemple de Violation** :
```python
# ❌ VIOLATION
def display_balance(user):
    saka = get_saka_balance(user)
    return f"{saka} SAKA (≈ {saka * 0.01} €)"  # Interdit
```

**Exemple Conforme** :
```python
# ✅ CONFORME
def display_balance(user):
    saka = get_saka_balance(user)
    return f"{saka} SAKA"  # Pas de valeur monétaire
```

---

## 🧪 Étape 4 : Créer des Tests de Conformité

### Tests Minimaux Requis

Créez des tests qui vérifient :

1. **Séparation SAKA/EUR**
```python
def test_no_saka_eur_conversion():
    """Vérifie qu'aucune fonction de conversion n'existe"""
    # Scan du code pour détecter les violations
    assert no_conversion_functions_exist()

def test_no_saka_eur_link():
    """Vérifie qu'aucun lien DB entre SAKA et EUR"""
    assert no_foreign_key_between_saka_and_eur()
```

2. **Compostage Obligatoire**
```python
def test_compost_mandatory_if_saka_enabled():
    """Vérifie que le compostage est activé si SAKA activé"""
    assert SAKA_ENABLED == True
    assert SAKA_COMPOST_ENABLED == True  # Obligatoire
```

3. **Anti-Accumulation**
```python
def test_compost_cycle_runs():
    """Vérifie que le cycle de compostage s'exécute"""
    result = run_compost_cycle()
    assert result['composted'] > 0
```

---

## ✅ Étape 5 : Valider la Conformité

### Installation du Validateur

```bash
# Télécharger le validateur
wget https://egoejo.org/tools/egoejo-validator.py
chmod +x egoejo-validator.py
```

### Exécution de la Validation

```bash
# Valider le projet
python tools/egoejo-validator.py --project-path .

# Mode strict (warnings = violations)
python tools/egoejo-validator.py --strict

# Sortie JSON
python tools/egoejo-validator.py --json
```

### Résultat Attendu

```
================================================================================
EGOEJO Compliant Validator - Rapport de Validation
================================================================================

✅ PROJET CONFORME À LA CONSTITUTION EGOEJO

================================================================================
```

---

## 🏆 Étape 6 : Obtenir le Badge EGOEJO Compliant

### Conditions

1. ✅ Fichier `egoejo.json` présent et valide
2. ✅ Validation réussie avec `egoejo-validator.py`
3. ✅ Tests de conformité présents et passants
4. ✅ Code respecte les règles déclarées

### Badge Markdown

Ajoutez le badge dans votre `README.md` :

```markdown
[![EGOEJO Compliant](https://egoejo.org/badges/egoejo-compliant.svg)](https://egoejo.org/compliant)
```

### Badge HTML

```html
<a href="https://egoejo.org/compliant">
  <img src="https://egoejo.org/badges/egoejo-compliant.svg" alt="EGOEJO Compliant" />
</a>
```

---

## 🔄 Étape 7 : Intégration CI/CD

### GitHub Actions

Créez `.github/workflows/egoejo-validation.yml` :

```yaml
name: EGOEJO Compliant Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate EGOEJO Compliance
        run: |
          python tools/egoejo-validator.py --strict
```

### GitLab CI

Créez `.gitlab-ci.yml` :

```yaml
egoejo_validation:
  script:
    - python tools/egoejo-validator.py --strict
  only:
    - main
    - merge_requests
```

---

## 📚 Ressources

### Documentation

- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Schéma JSON** : `docs/open-source/egoejo-compliant-schema.json`
- **Validateur** : `tools/egoejo-validator.py`

### Exemples

- **Projet de référence** : [EGOEJO](https://github.com/egoejo/egoejo)
- **Fichier egoejo.json** : Voir la racine du projet EGOEJO

---

## ❓ FAQ

### Q: Puis-je adapter les règles à mon projet ?

**R:** Oui, mais les règles fondamentales sont **non-négociables** :
- `strict_separation: true`
- `no_conversion: true`
- `no_financial_return: true`
- `no_monetary_display: true`

Vous pouvez adapter les paramètres (taux de compostage, jours d'inactivité, etc.).

---

### Q: Mon projet n'utilise pas Python. Puis-je être conforme ?

**R:** Oui ! Le validateur est en Python, mais la constitution EGOEJO est **agnostique du langage**. Vous devez :
1. Créer un fichier `egoejo.json`
2. Respecter les règles dans votre code
3. Créer des tests de conformité dans votre langage

---

### Q: Que faire si ma validation échoue ?

**R:** 
1. Consultez le rapport de validation
2. Corrigez les violations détectées
3. Ré-exécutez la validation
4. Si besoin, consultez la documentation EGOEJO

---

### Q: Le badge est-il permanent ?

**R:** Non. Le badge doit être **revalidé régulièrement**. Nous recommandons :
- Validation automatique en CI/CD
- Revalidation manuelle lors des releases majeures

---

## 🎯 Checklist Finale

Avant de déclarer votre projet conforme :

- [ ] Fichier `egoejo.json` créé et valide
- [ ] Règles fondamentales respectées dans le code
- [ ] Tests de conformité créés et passants
- [ ] Validation réussie avec `egoejo-validator.py`
- [ ] CI/CD configuré pour validation automatique
- [ ] Badge ajouté au README
- [ ] Documentation mise à jour

---

## 📞 Support

Pour toute question :
- **Documentation** : https://egoejo.org/docs
- **Issues** : https://github.com/egoejo/egoejo/issues
- **Email** : compliant@egoejo.org

---

**Bienvenue dans l'écosystème EGOEJO Compliant ! 🌾**

*Document généré le : 2025-12-19*

