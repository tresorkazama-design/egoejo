# 🏛️ Workflow CI de Conformité EGOEJO

**Fichier** : `.github/workflows/egoejo-guardian.yml`  
**Date** : 2025-12-19  
**Statut** : 🔴 **BLOQUANT** - Le déploiement est INTERDIT si une seule étape échoue

---

## 📋 Vue d'Ensemble

Le workflow **EGOEJO Guardian CI** est un pipeline de vérification automatique qui garantit que toutes les Pull Requests respectent la **Constitution EGOEJO**.

### Comportement

**Si une seule étape échoue → DÉPLOIEMENT INTERDIT**  
La PR est marquée **🔴 NON COMPATIBLE EGOEJO**

---

## 🔄 Étapes du Workflow

### 1. 📥 Checkout Code

**Action** : `actions/checkout@v4`  
**Configuration** : `fetch-depth: 0` (nécessaire pour git diff complet)

---

### 2. 🔍 Scan Guardian - Analyse Git Diff

**Script** : `.egoejo/guardian.py`  
**Branche de base** : `origin/${{ github.base_ref }}` ou `origin/main`

**Vérifications** :
- ✅ Détection de conversion SAKA ↔ EUR
- ✅ Détection de rendement financier sur SAKA
- ✅ Détection d'affichage monétaire du SAKA
- ✅ Vérification tests requis pour modifications SAKA

**Exit Code** :
- `0` : ✅ PASS
- `1` : ❌ FAIL → **DÉPLOIEMENT INTERDIT**

**Messages GitHub Actions** :
```
::error::🚫 VIOLATION CONSTITUTION EGOEJO : Le Guardian a détecté des violations critiques
```

---

### 3. 🔒 Scan Séparation SAKA/EUR - Vérification Étanchéité

**Objectif** : Vérifier qu'aucun fichier ne contient à la fois `UserWallet` et `SakaWallet`

**Méthode** :
1. Récupère les fichiers modifiés via `git diff`
2. Pour chaque fichier modifié :
   - Vérifie si `UserWallet` ET `SakaWallet` sont présents
   - Exclut les commentaires et imports simples
   - Ignore les fichiers admin explicites

**Fichiers Admin Autorisés** :
- `admin.py`
- `tests/compliance/test_saka_eur_etancheite.py`
- `tests/compliance/test_saka_eur_separation.py`

**Scan Complet** :
- Vérifie aussi tous les fichiers du codebase (pas seulement modifiés)
- Détecte les violations existantes

**Exit Code** :
- `0` : ✅ PASS
- `1` : ❌ FAIL → **DÉPLOIEMENT INTERDIT**

**Messages GitHub Actions** :
```
::error file=path/to/file.py::🚫 VIOLATION CONSTITUTION EGOEJO : Étanchéité SAKA/EUR rompue
```

---

### 4. 🧪 Validation Tests Philosophie SAKA

**Fichier de test** : `backend/core/tests_saka_philosophy.py`

**Exécution** :
```bash
cd backend
pytest core/tests_saka_philosophy.py -v --tb=short
```

**Tests inclus** :
- ✅ Expiration : SAKA inactif doit être composté
- ✅ Compostage : SAKA inactif retourne au Silo Commun
- ✅ Retour au Silo : Le Silo bénéficie de l'inutilisation
- ✅ Impossibilité de thésaurisation : Pas d'accumulation infinie
- ✅ Cycle complet : Récolte → Plantation → Compost → Silo → Redistribution

**Exit Code** :
- `0` : ✅ PASS
- `1` : ❌ FAIL → **DÉPLOIEMENT INTERDIT**

**Messages GitHub Actions** :
```
::error::🚫 Les tests de philosophie SAKA ont échoué. La constitution EGOEJO n'est pas respectée.
```

---

## 🚨 Comportement de Blocage

### Si une étape échoue :

1. **Workflow marqué comme FAILED**
2. **PR marquée 🔴 NON COMPATIBLE EGOEJO**
3. **Déploiement INTERDIT**
4. **Message d'erreur explicite** :
   ```
   ::error::🔴 NON COMPATIBLE EGOEJO
   ::error::🚫 DÉPLOIEMENT INTERDIT - Violations de la Constitution EGOEJO détectées
   ```

### Résumé GitHub Actions

Le workflow génère automatiquement un résumé dans `$GITHUB_STEP_SUMMARY` :

```markdown
## 🏛️ Rapport de Conformité Constitution EGOEJO

### ✅ Vérifications Effectuées :

1. ✅ **Guardian Scan** : PASS - Aucune violation détectée
2. ✅ **Séparation SAKA/EUR** : PASS - Étanchéité respectée
3. ✅ **Tests Philosophie SAKA** : PASS - Tous les tests passent

### ✅ **STATUT FINAL : COMPATIBLE EGOEJO**

Cette PR respecte la constitution EGOEJO. Le déploiement est autorisé.
```

---

## 📊 Exemples de Violations

### Exemple 1 : Conversion SAKA ↔ EUR

**Fichier** : `backend/core/services/saka.py`
```python
def convert_saka_to_eur(saka_amount):
    return saka_amount * 0.01  # ❌ VIOLATION
```

**Résultat** :
- ❌ Guardian Scan : FAIL
- 🔴 DÉPLOIEMENT INTERDIT

---

### Exemple 2 : Violation de Séparation

**Fichier** : `backend/core/services/wallet.py`
```python
from finance.models import UserWallet
from core.models.saka import SakaWallet

def transfer_saka_to_eur(user, amount):
    saka_wallet = SakaWallet.objects.get(user=user)
    user_wallet = UserWallet.objects.get(user=user)
    # ❌ VIOLATION : Les deux wallets dans le même fichier
```

**Résultat** :
- ❌ Scan Séparation : FAIL
- 🔴 DÉPLOIEMENT INTERDIT

---

### Exemple 3 : Test Philosophie Échoué

**Fichier** : `backend/core/tests_saka_philosophy.py`
```python
def test_saka_compost_required():
    # Test échoue car le compostage est désactivé
    assert compost_enabled == True  # ❌ FAIL
```

**Résultat** :
- ❌ Tests Philosophie : FAIL
- 🔴 DÉPLOIEMENT INTERDIT

---

## ✅ Checklist de Conformité

Avant de créer une PR, vérifier :

- [ ] Le Guardian passe : `python .egoejo/guardian.py`
- [ ] Aucun fichier ne contient à la fois `UserWallet` et `SakaWallet` (sauf admin)
- [ ] Les tests de philosophie passent : `pytest backend/core/tests_saka_philosophy.py`
- [ ] Aucune conversion SAKA ↔ EUR
- [ ] Aucun rendement financier sur SAKA
- [ ] Aucun affichage monétaire du SAKA

---

## 🔧 Configuration

### Déclencheurs

Le workflow se déclenche automatiquement sur :
- **Pull Request** : `opened`, `synchronize`, `reopened`, `edited`
- **Push** : `main`, `develop`

### Variables d'Environnement

- `GITHUB_BASE_REF` : Branche de base de la PR (défaut: `main`)
- `DJANGO_SETTINGS_MODULE` : Module Django settings (défaut: `config.settings`)

---

## 📖 Documentation Associée

- **Constitution EGOEJO** : `docs/architecture/CONSTITUTION_EGOEJO.md`
- **Guardian Script** : `docs/architecture/GUARDIAN_EGOEJO_REFERENCE.md`
- **Tests Philosophie** : `backend/core/tests_saka_philosophy.py`

---

## 🎯 Philosophie EGOEJO

Le workflow enforce la **double structure économique non-négociable** :

1. **Structure Relationnelle SAKA** (Souveraine, Prioritaire)
   - Engagement, don, réputation
   - Cycle : Récolte → Usage → Compost → Silo → Redistribution
   - Anti-accumulation absolue

2. **Structure Instrumentale EUR** (Subordonnée, Dormante)
   - Finance, paiement, conformité
   - Ne doit JAMAIS contraindre ou corrompre le SAKA

**Le workflow rend techniquement impossible la trahison du projet.**

---

*Document généré le : 2025-12-19*

