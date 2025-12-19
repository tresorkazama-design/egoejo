# 🏛️ EGOEJO Guardian - Script de Sécurité Robuste

**Version** : 2.0  
**Date** : 2025-12-19  
**Fichier** : `.egoejo/guardian.py`

---

## 📋 Vue d'Ensemble

Le **EGOEJO Guardian** est un script de sécurité robuste qui analyse automatiquement les Pull Requests pour garantir la conformité avec la constitution EGOEJO.

### Fonctionnalités

- ✅ Analyse du `git diff` complet (pas seulement les noms de fichiers)
- ✅ Détection des violations bloquantes (HARD FAIL)
- ✅ Messages formatés pour GitHub Actions (`::error::`)
- ✅ Vérification des tests requis pour modifications SAKA
- ✅ Exit codes standards (0 = PASS, 1 = FAIL)

---

## 🚨 Règles Bloquantes (HARD FAIL)

### 1. Détection de Conversion SAKA ↔ EUR

**Patterns détectés** :
- `convert.*saka.*eur` / `convert.*eur.*saka`
- `saka.*exchange.*rate`
- `saka.*price` / `price.*saka`
- `saka.*=.*eur` / `eur.*=.*saka`
- `saka_to_eur` / `eur_to_saka`
- `convert_saka` / `convert_eur`
- `saka.*currency` / `currency.*saka`

**Action** : ❌ **MERGE BLOQUÉ**

**Exemple de violation** :
```python
# ❌ VIOLATION
def convert_saka_to_eur(saka_amount):
    return saka_amount * 0.01  # 1 SAKA = 0.01 EUR
```

---

### 2. Détection de Rendement Financier sur SAKA

**Patterns détectés** :
- `saka.*interest` / `interest.*saka`
- `saka.*yield` / `yield.*saka`
- `saka.*profit` / `profit.*saka`
- `saka.*dividend` / `dividend.*saka`
- `saka.*roi` / `roi.*saka`
- `saka.*apy` / `apy.*saka`
- `saka.*return` / `return.*saka`
- `saka.*revenue` / `revenue.*saka`

**Action** : ❌ **MERGE BLOQUÉ**

**Exemple de violation** :
```python
# ❌ VIOLATION
def calculate_saka_interest(balance, rate):
    return balance * rate  # Rendement financier interdit
```

---

### 3. Détection d'Affichage Monétaire du SAKA

**Patterns détectés** :
- `saka.*€` / `€.*saka`
- `saka.*$` / `$.*saka`
- `saka.*euro` / `euro.*saka`
- `saka.*dollar` / `dollar.*saka`
- `saka.*currency` / `currency.*saka`
- `format.*saka.*money` / `format.*money.*saka`
- `saka.*amount.*€` / `€.*amount.*saka`
- `saka.*value.*$` / `$.*value.*saka`

**Action** : ❌ **MERGE BLOQUÉ**

**Exemple de violation** :
```python
# ❌ VIOLATION
def display_saka_balance(balance):
    return f"{balance} SAKA (équivalent {balance * 0.01} €)"
```

---

### 4. Modification SAKA sans Test

**Règle** : Si `core/services/saka.py` est modifié, au moins un fichier de test SAKA doit être modifié.

**Fichiers SAKA détectés** :
- `backend/core/services/saka.py`
- `backend/core/models/saka.py`
- `backend/core/api/saka*.py`
- Tout fichier contenant `saka` ou `Saka` dans le nom

**Fichiers de test détectés** :
- `backend/tests/compliance/test_saka*.py`
- `backend/core/tests*saka*.py`
- Tout fichier de test contenant `saka` ou `Saka` dans le nom

**Action** : ❌ **MERGE BLOQUÉ**

**Exemple de violation** :
```bash
# ❌ VIOLATION
git diff origin/main --name-only
# backend/core/services/saka.py  ← Modifié
# backend/core/models/user.py     ← Modifié
# ❌ Aucun fichier de test SAKA modifié
```

---

## 🔍 Faux Positifs Exclus

Le script exclut automatiquement les faux positifs :

- ✅ **Commentaires** : Lignes commençant par `#`
- ✅ **Docstrings** : Lignes contenant `"""` ou `'''`
- ✅ **Mots courants** : `utilisateur`, `erreur`, `redistribution`, `assureur`
- ✅ **Imports** : Lignes `import` ou `from`
- ✅ **Return simples** : `return variable` (sauf si contient `convert`)

---

## 📊 Format de Sortie

### Messages GitHub Actions

Le script utilise le format GitHub Actions pour les erreurs :

```bash
::error file=backend/core/services/saka.py,line=42::Conversion SAKA ↔ EUR interdite: def convert_saka_to_eur
```

### Messages Console

```
🏛️ EGOEJO Guardian - Analyse de conformité

📁 Fichiers modifiés: 3

❌ NON COMPATIBLE EGOEJO - VIOLATIONS CRITIQUES DÉTECTÉES

================================================================================

🚫 Règle violée: Conversion SAKA ↔ EUR interdite
   Nombre de violations: 1

   📄 backend/core/services/saka.py
      Ligne 42: def convert_saka_to_eur(saka_amount):

================================================================================

🔒 MERGE BLOQUÉ - Corriger les violations avant de continuer
```

---

## 🚀 Utilisation

### En Local

```bash
# Analyser contre origin/main
python .egoejo/guardian.py

# Analyser contre une branche spécifique
python .egoejo/guardian.py origin/develop
```

### Dans GitHub Actions

Le script est automatiquement exécuté dans le workflow `.github/workflows/pr-bot-egoejo-guardian.yml`.

**Variables d'environnement utilisées** :
- `GITHUB_BASE_REF` : Branche de base de la PR (défaut: `main`)

**Exit codes** :
- `0` : ✅ PASS - Compatible EGOEJO
- `1` : ❌ FAIL - Violation critique détectée (merge bloqué)

---

## 🧪 Tests

### Test Manuel

```bash
# Créer une branche de test avec une violation
git checkout -b test-guardian-violation
echo "def convert_saka_to_eur(saka): return saka * 0.01" >> backend/core/services/saka.py
git add backend/core/services/saka.py
git commit -m "Test violation"

# Tester le Guardian
python .egoejo/guardian.py origin/main
# Résultat attendu: Exit code 1 (FAIL)
```

### Test avec Fichier Valide

```bash
# Créer une branche de test sans violation
git checkout -b test-guardian-valid
echo "# Commentaire valide" >> backend/core/services/saka.py
git add backend/core/services/saka.py
git commit -m "Test valide"

# Tester le Guardian
python .egoejo/guardian.py origin/main
# Résultat attendu: Exit code 0 (PASS)
```

---

## 🔧 Architecture Technique

### Structure du Script

```python
class EGOEJOGuardian:
    - blocking_rules: Dict[str, Dict]  # Règles bloquantes
    - saka_file_patterns: List[str]     # Patterns fichiers SAKA
    - test_file_patterns: List[str]     # Patterns fichiers de test
    
    def get_git_diff() -> str           # Récupère le diff complet
    def scan_git_diff() -> List[Dict]   # Scanne le diff pour violations
    def check_saka_tests_required()      # Vérifie tests requis
    def analyze() -> Tuple[bool, List]   # Analyse complète
```

### Parsing du Git Diff

Le script parse le format standard de `git diff` :

```
diff --git a/file.py b/file.py
@@ -10,5 +10,5 @@
-old line
+new line
```

- Détecte les fichiers modifiés via `diff --git`
- Extrait les numéros de ligne via `@@`
- Analyse uniquement les lignes ajoutées (`+`)

---

## 📝 Exemples de Violations

### Exemple 1 : Conversion SAKA → EUR

```python
# ❌ VIOLATION DÉTECTÉE
def get_saka_eur_rate():
    return 0.01  # 1 SAKA = 0.01 EUR
```

**Message d'erreur** :
```
::error file=backend/core/services/saka.py,line=42::Conversion SAKA ↔ EUR interdite: def get_saka_eur_rate
```

---

### Exemple 2 : Rendement Financier

```python
# ❌ VIOLATION DÉTECTÉE
def calculate_saka_yield(balance, days):
    return balance * 0.05 * (days / 365)  # Rendement annuel 5%
```

**Message d'erreur** :
```
::error file=backend/core/services/saka.py,line=55::Rendement financier sur SAKA interdit: def calculate_saka_yield
```

---

### Exemple 3 : Affichage Monétaire

```python
# ❌ VIOLATION DÉTECTÉE
def format_saka_balance(balance):
    return f"{balance} SAKA (≈ {balance * 0.01} €)"
```

**Message d'erreur** :
```
::error file=frontend/src/components/SakaBalance.jsx,line=12::Affichage monétaire du SAKA interdit: return f"{balance} SAKA (≈ {balance * 0.01} €)"
```

---

### Exemple 4 : Modification SAKA sans Test

```bash
# ❌ VIOLATION DÉTECTÉE
git diff origin/main --name-only
# backend/core/services/saka.py  ← Modifié
# ❌ Aucun fichier de test SAKA modifié
```

**Message d'erreur** :
```
::error file=core/services/saka.py::Modification SAKA sans test associé: Le fichier core/services/saka.py a été modifié mais aucun fichier de test SAKA n'a été modifié.
```

---

## ✅ Checklist de Conformité

Avant de créer une PR, vérifier :

- [ ] Aucune fonction de conversion SAKA ↔ EUR
- [ ] Aucun calcul de rendement financier sur SAKA
- [ ] Aucun affichage monétaire du SAKA (€, $)
- [ ] Si `core/services/saka.py` modifié, au moins un test SAKA modifié
- [ ] Tests passent localement
- [ ] Le Guardian passe (`python .egoejo/guardian.py`)

---

## 🎯 Philosophie EGOEJO

Le Guardian enforce la **double structure économique non-négociable** :

1. **Structure Relationnelle SAKA** (Souveraine, Prioritaire)
   - Engagement, don, réputation
   - Cycle : Récolte → Usage → Compost → Silo → Redistribution
   - Anti-accumulation absolue

2. **Structure Instrumentale EUR** (Subordonnée, Dormante)
   - Finance, paiement, conformité
   - Ne doit JAMAIS contraindre ou corrompre le SAKA

**Le Guardian rend techniquement impossible la trahison du projet.**

---

*Document généré le : 2025-12-19*

