# 🚀 Intégration CI/CD - Tests de Compliance EGOEJO

**Version** : 1.0  
**Date** : 2025-01-27

---

## 🎯 Objectif

Intégrer les tests de compliance EGOEJO dans la CI/CD pour **bloquer automatiquement** les merges qui violent la philosophie EGOEJO.

---

## 📋 Recommandations d'Intégration

### 1. Workflow GitHub Actions Bloquant

**Fichier** : `.github/workflows/egoejo-compliance.yml`

**Configuration** :
```yaml
name: 🛡️ EGOEJO Compliance Philosophique

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  egoejo-compliance:
    name: Tests de Compliance Philosophique SAKA/EUR
    runs-on: ubuntu-latest
    timeout-minutes: 15
    
    steps:
      - name: 📥 Checkout code
        uses: actions/checkout@v4
      
      - name: 🐍 Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: 📦 Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: 🛡️ Run Compliance Tests (BLOQUANT)
        env:
          DJANGO_SECRET_KEY: test-secret-key-for-ci-compliance-testing-min-50-chars-required
          ENABLE_SAKA: 'True'
          SAKA_COMPOST_ENABLED: 'True'
        run: |
          cd backend
          python manage.py migrate --noinput
          pytest -m egoejo_compliance -v --tb=short --strict-markers
```

**Résultat** : Si un test échoue, le workflow échoue et le merge est bloqué.

---

### 2. Pre-commit Hook (Optionnel mais Recommandé)

**Fichier** : `.git/hooks/pre-commit`

**Configuration** :
```bash
#!/bin/bash
echo "Running EGOEJO pre-commit hook..."

# Run compliance tests
cd backend
DJANGO_SECRET_KEY="pre-commit-secret-key-for-testing-only-min-50-chars-required" \
ENABLE_SAKA="True" \
SAKA_COMPOST_ENABLED="True" \
python manage.py migrate --noinput > /dev/null 2>&1

DJANGO_SECRET_KEY="pre-commit-secret-key-for-testing-only-min-50-chars-required" \
ENABLE_SAKA="True" \
SAKA_COMPOST_ENABLED="True" \
pytest -m egoejo_compliance -v --tb=short --strict-markers

if [ $? -ne 0 ]; then
    echo "❌ Compliance tests FAILED. Aborting commit."
    exit 1
fi

echo "✅ Compliance tests PASSED."
exit 0
```

**Résultat** : Empêche les commits locaux qui violent la philosophie.

---

### 3. Branch Protection Rules

**Configuration GitHub** :

1. Aller dans **Settings** → **Branches**
2. Ajouter une règle pour `main` et `develop`
3. Activer :
   - ✅ **Require status checks to pass before merging**
   - ✅ **Require branches to be up to date before merging**
4. Sélectionner `egoejo-compliance` dans la liste des status checks

**Résultat** : Les merges sont bloqués si les tests de compliance échouent.

---

## 🔍 Exécution des Tests

### Local

```bash
# Exécuter tous les tests de compliance
cd backend
pytest -m egoejo_compliance -v

# Exécuter une catégorie spécifique
pytest tests/compliance/philosophy/ -v
pytest tests/compliance/structure/ -v
pytest tests/compliance/finance/ -v
pytest tests/compliance/governance/ -v
```

### CI/CD

```bash
# Commande dans GitHub Actions
pytest -m egoejo_compliance -v --tb=short --strict-markers
```

---

## 📊 Structure des Tests par Catégorie

### Philosophy (Philosophie)

**Tests** :
- `test_double_structure.py` : Structure relationnelle > instrumentale
- `test_anti_accumulation.py` : Anti-accumulation

**Commande** :
```bash
pytest tests/compliance/philosophy/ -v
```

---

### Structure (Structure)

**Tests** :
- `test_models_separation.py` : Modèles SAKA / EUR séparés

**Commande** :
```bash
pytest tests/compliance/structure/ -v
```

---

### Finance (Finance)

**Tests** :
- `test_no_conversion.py` : Aucune conversion SAKA ↔ EUR

**Commande** :
```bash
pytest tests/compliance/finance/ -v
```

---

### Governance (Gouvernance)

**Tests** :
- `test_feature_flags.py` : Feature flags respectés
- `test_transparency.py` : Transparence des métriques

**Commande** :
```bash
pytest tests/compliance/governance/ -v
```

---

## 🚫 Blocage Automatique

### Conditions de Blocage

Le merge est **automatiquement bloqué** si :

1. ❌ **Un test de compliance échoue** : `pytest -m egoejo_compliance` retourne un code d'erreur
2. ❌ **Workflow CI échoue** : Le workflow GitHub Actions échoue
3. ❌ **Branch Protection activée** : Les règles de protection de branche bloquent le merge

### Messages d'Erreur

**Exemple** :
```
❌ ==========================================
❌ VIOLATION CONSTITUTION EGOEJO DÉTECTÉE
❌ ==========================================

Les tests de compliance philosophique ont échoué.
Ce commit viole la séparation stricte SAKA/EUR ou la philosophie EGOEJO.

Action requise :
1. Corriger le code pour respecter la séparation SAKA/EUR
2. Relancer les tests : pytest -m egoejo_compliance -v
3. Recommiter
```

---

## 📝 Checklist d'Intégration

### Configuration CI/CD

- [ ] Workflow GitHub Actions créé (`.github/workflows/egoejo-compliance.yml`)
- [ ] Tests tagués `@egoejo_compliance`
- [ ] Workflow exécute `pytest -m egoejo_compliance`
- [ ] Workflow échoue si tests échouent

### Configuration Branch Protection

- [ ] Branch Protection activée pour `main` et `develop`
- [ ] Status check `egoejo-compliance` requis
- [ ] Branches doivent être à jour avant merge

### Configuration Pre-commit (Optionnel)

- [ ] Pre-commit hook créé (`.git/hooks/pre-commit`)
- [ ] Hook exécute les tests de compliance
- [ ] Hook bloque le commit si tests échouent

---

## 🔧 Dépannage

### Tests Échouent en CI mais Passent Localement

**Causes possibles** :
- Variables d'environnement différentes
- Base de données non migrée
- Dépendances manquantes

**Solution** :
```bash
# Vérifier les variables d'environnement
echo $ENABLE_SAKA
echo $SAKA_COMPOST_ENABLED

# Vérifier les migrations
python manage.py migrate --noinput

# Réinstaller les dépendances
pip install -r requirements.txt
```

### Tests Trop Lents

**Solution** :
```bash
# Exécuter en parallèle
pytest -m egoejo_compliance -v -n auto

# Limiter aux tests critiques
pytest -m egoejo_compliance -v --maxfail=1
```

---

## 📚 Références

- [Architecture des Tests](../tests/COMPLIANCE_TESTS_ARCHITECTURE.md)
- [README Compliance](../../backend/tests/compliance/README.md)
- [Label EGOEJO COMPLIANT](../../egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)

---

**Fin de l'Intégration CI/CD**

*Dernière mise à jour : 2025-01-27*

