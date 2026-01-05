# 🛡️ Tests de Compliance EGOEJO

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Tests Bloquants - CI/CD

---

## 🎯 Philosophie des Tests

Ces tests **documentent le Manifeste EGOEJO par le code**. Ils agissent comme une **constitution exécutable** qui protège les principes fondamentaux d'EGOEJO.

### Principe Fondamental

> **"Si un test de compliance échoue, le projet n'est plus EGOEJO COMPLIANT."**

Ces tests sont **BLOQUANTS** en CI/CD. Aucun merge n'est possible si un test échoue.

---

## 📁 Structure des Tests

```
backend/tests/compliance/
├── README.md                          # Ce fichier
├── __init__.py                        # Module Python
│
├── philosophy/                        # Tests philosophiques
│   ├── __init__.py
│   ├── test_double_structure.py      # Structure relationnelle > instrumentale
│   ├── test_saka_eur_separation.py   # Séparation stricte SAKA / EUR
│   ├── test_anti_accumulation.py     # Anti-accumulation
│   └── test_circulation_obligatory.py # Circulation obligatoire
│
├── structure/                        # Tests structurels
│   ├── __init__.py
│   ├── test_models_separation.py     # Modèles SAKA / EUR séparés
│   ├── test_services_separation.py   # Services SAKA / EUR séparés
│   └── test_api_separation.py       # Endpoints API séparés
│
├── finance/                          # Tests financiers
│   ├── __init__.py
│   ├── test_no_conversion.py         # Aucune conversion SAKA ↔ EUR
│   ├── test_no_monetary_display.py   # Affichage non-monétaire
│   └── test_no_financial_return.py   # Aucun rendement financier
│
└── governance/                       # Tests de gouvernance
    ├── __init__.py
    ├── test_settings_protection.py   # Protection settings critiques
    ├── test_test_protection.py        # Protection tests compliance
    └── test_feature_flags.py          # Feature flags respectés
```

---

## 🏷️ Convention de Nommage

### Fichiers de Tests

**Format** : `test_<categorie>_<critere>.py`

**Exemples** :
- `test_philosophy_double_structure.py`
- `test_finance_no_conversion.py`
- `test_governance_settings_protection.py`

### Fonctions de Test

**Format** : `test_<description_du_verifie>`

**Exemples** :
- `test_saka_eur_separation_enforced()`
- `test_compostage_obligatory_in_production()`
- `test_no_conversion_function_exists()`

### Classes de Test

**Format** : `Test<Categorie><Critere>`

**Exemples** :
- `TestPhilosophyDoubleStructure`
- `TestFinanceNoConversion`
- `TestGovernanceSettingsProtection`

---

## 📊 Catégories de Tests

### 1. Philosophy (Philosophie)

**Objectif** : Vérifier les principes philosophiques fondamentaux.

**Critères** :
- ✅ Structure relationnelle > structure instrumentale
- ✅ Séparation stricte SAKA / EUR
- ✅ Anti-accumulation
- ✅ Circulation obligatoire

**Tests** : `backend/tests/compliance/philosophy/`

---

### 2. Structure (Structure)

**Objectif** : Vérifier la séparation structurelle dans le code.

**Critères** :
- ✅ Modèles Django séparés (SakaWallet ≠ UserWallet)
- ✅ Services séparés (saka.py ≠ finance/services.py)
- ✅ Endpoints API séparés

**Tests** : `backend/tests/compliance/structure/`

---

### 3. Finance (Finance)

**Objectif** : Vérifier l'absence de monétisation SAKA.

**Critères** :
- ✅ Aucune conversion SAKA ↔ EUR
- ✅ Affichage non-monétaire (grains, pas €)
- ✅ Aucun rendement financier

**Tests** : `backend/tests/compliance/finance/`

---

### 4. Governance (Gouvernance)

**Objectif** : Vérifier la protection des mécanismes de gouvernance.

**Critères** :
- ✅ Settings critiques protégés
- ✅ Tests compliance non supprimables
- ✅ Feature flags respectés

**Tests** : `backend/tests/compliance/governance/`

---

## 🚫 Tests Bloquants

### Tag `@egoejo_compliance`

**Tous les tests de compliance** doivent être tagués avec `@pytest.mark.egoejo_compliance`.

**Exemple** :
```python
@pytest.mark.egoejo_compliance
def test_saka_eur_separation_enforced():
    """Vérifie que la séparation SAKA / EUR est respectée."""
    # ...
```

### Exécution en CI

**Commande** :
```bash
pytest -m egoejo_compliance -v --tb=short
```

**Résultat** : Si un test échoue, la CI échoue et le merge est bloqué.

---

## 📝 Documentation des Tests

### Format Standard

Chaque test doit documenter :

1. **LOI EGOEJO** : Le principe philosophique vérifié
2. **Ce que le test vérifie** : Description précise
3. **Violation du Manifeste si** : Conditions de violation

**Exemple** :
```python
"""
EGOEJO Compliance Test : Séparation SAKA / EUR

LOI EGOEJO :
"Aucune conversion SAKA ↔ EUR n'est autorisée."

Ce test vérifie que :
- Aucune fonction de conversion n'existe
- Aucun endpoint API de conversion n'existe

Violation du Manifeste EGOEJO si :
- Une fonction convert_saka_to_eur() existe
- Un endpoint /api/saka/convert/ existe
"""
```

---

## 🔍 Exemples de Tests

### Test Philosophique

```python
@pytest.mark.egoejo_compliance
def test_structure_relationnelle_prime_sur_instrumentale():
    """
    Vérifie que la structure relationnelle (SAKA) prime sur la structure instrumentale (EUR).
    """
    # Vérifier qu'aucune fonction ne permet de convertir SAKA en EUR
    # Vérifier que SAKA n'est jamais affiché comme monnaie
    # ...
```

### Test Structurel

```python
@pytest.mark.egoejo_compliance
def test_models_saka_eur_separes():
    """
    Vérifie que les modèles SAKA et EUR sont strictement séparés.
    """
    # Vérifier qu'aucune ForeignKey ne lie SakaWallet et UserWallet
    # ...
```

### Test Financier

```python
@pytest.mark.egoejo_compliance
def test_aucune_conversion_saka_eur():
    """
    Vérifie qu'aucune conversion SAKA ↔ EUR n'est possible.
    """
    # Scanner le code pour détecter les fonctions de conversion
    # ...
```

### Test de Gouvernance

```python
@pytest.mark.egoejo_compliance
def test_settings_critiques_proteges():
    """
    Vérifie que les settings critiques sont protégés.
    """
    # Vérifier que SAKA_COMPOST_ENABLED ne peut pas être False en production
    # ...
```

---

## 🚀 Intégration CI/CD

### Workflow GitHub Actions

**Fichier** : `.github/workflows/egoejo-compliance.yml`

**Commande** :
```yaml
- name: Run compliance tests
  run: |
    pytest -m egoejo_compliance -v --tb=short --strict-markers
```

**Résultat** : Si un test échoue, le workflow échoue et le merge est bloqué.

---

## 📚 Références

- [Label EGOEJO COMPLIANT](../../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)
- [Tableau de Conformité](../../../docs/egoejo_compliance/TABLEAU_CONFORMITE.md)
- [Manifeste SAKA/EUR](../../../docs/philosophie/MANIFESTE_SAKA_EUR.md)

---

## ⚠️ Règles Absolues

1. **Aucun test de compliance ne peut être désactivé** sans justification
2. **Tous les tests doivent être tagués** `@egoejo_compliance`
3. **Tous les tests doivent documenter** le principe philosophique vérifié
4. **Si un test échoue, le projet n'est plus EGOEJO COMPLIANT**

---

**Fin du README**

*Dernière mise à jour : 2025-01-27*

