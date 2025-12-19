# EGOEJO Guardian - Bot de Vérification de Conformité

## Description

Le **EGOEJO Guardian** est un bot de vérification automatique qui analyse chaque Pull Request pour détecter les violations de la constitution EGOEJO.

## Installation

Aucune installation requise. Le bot utilise uniquement Python standard (pas de dépendances externes).

## Usage

### Exécution locale

```bash
# Depuis la racine du projet
python .egoejo/guardian.py
```

### Exécution en CI

Le bot est automatiquement exécuté via GitHub Actions (`.github/workflows/egoejo-guardian.yml`).

## Fonctionnalités

### 1. Détection de violations

Le bot détecte automatiquement :

- ❌ **Conversion SAKA ↔ EUR** : Patterns `convert.*saka.*eur`, `saka_to_eur`, etc.
- ❌ **Rendement financier SAKA** : Patterns `saka.*interest`, `saka.*yield`, etc.
- ❌ **Affichage monétaire SAKA** : Patterns `saka.*€`, `saka.*euro`, etc.
- ⚠️ **Tests manquants** : Modifications SAKA sans tests associés

### 2. Vérification des tests

Si un fichier SAKA est modifié, le bot vérifie qu'au moins un fichier de test SAKA a également été modifié.

### 3. Verdicts

- 🟢 **COMPATIBLE EGOEJO** : Aucune violation critique
- 🟡 **COMPATIBLE SOUS CONDITIONS** : Violations importantes uniquement
- 🔴 **NON COMPATIBLE EGOEJO** : Violation critique = blocage

## Exit Codes

- `0` : COMPATIBLE EGOEJO (merge autorisé)
- `1` : NON COMPATIBLE EGOEJO (merge bloqué)

## Configuration

Les règles sont définies dans `.egoejo/guardian_rules.yml`.

## Exemples

### Exemple 1 : Violation critique

```python
# backend/core/services/saka.py
def convert_saka_to_eur(saka_amount):
    return saka_amount * 0.01
```

**Résultat** :
```
🔴 NON COMPATIBLE EGOEJO

Violations critiques détectées:

  ❌ No Conversion
     Fichier: backend/core/services/saka.py (ligne 42)
     Contenu: def convert_saka_to_eur(saka_amount):
```

### Exemple 2 : Conformité

```python
# backend/core/services/saka.py
def harvest_saka(user, reason, amount):
    wallet = user.saka_wallet
    wallet.balance += amount
    wallet.save()
```

**Résultat** :
```
🟢 COMPATIBLE EGOEJO

✅ Aucune violation détectée
✅ Tests présents pour modifications SAKA
✅ Feature flags respectés

Cette PR respecte la constitution EGOEJO.
```

## Dépannage

### Erreur : "git n'est pas installé"

Le bot nécessite `git` pour récupérer les fichiers modifiés. Installez git ou exécutez depuis un repo git.

### Erreur : "Fichier de règles non trouvé"

Assurez-vous que `.egoejo/guardian_rules.yml` existe dans la racine du projet.

### Faux positifs

Si le bot détecte un faux positif, vérifiez que le pattern n'est pas dans :
- Un commentaire
- Une docstring
- Un mot contenant "eur" (utilisateur, erreur, etc.)

## Contribution

Pour ajouter une nouvelle règle :

1. Ajoutez le pattern dans `.egoejo/guardian_rules.yml`
2. Ajoutez la logique de détection dans `guardian.py`
3. Testez localement : `python .egoejo/guardian.py`

## Références

- Constitution EGOEJO : `docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md`
- Critères labels : `.egoejo/CRITERES_LABELS.md`
- Exemples sortie : `.egoejo/EXEMPLES_SORTIE_LABELS.md`

