# 🏗️ Architecture EGOEJO PR Bot

**Version** : 1.0  
**Date** : 2025-01-27

---

## 📋 Vue d'Ensemble

Le **EGOEJO PR Bot** est un **Comité de Mission automatisé** qui analyse chaque Pull Request selon les règles de gouvernance EGOEJO.

### Principe Fondamental

> **Le bot ne remplace pas l'humain, il structure la décision.**

Le bot :
- ✅ **Analyse** le diff Git
- ✅ **Détecte** les violations philosophiques et techniques
- ✅ **Informe** les contributeurs via commentaires
- ✅ **Bloque** le merge si nécessaire

Le bot ne :
- ❌ **Ne modifie jamais le code**
- ❌ **N'active jamais la V2.0**
- ❌ **Ne prend pas de décision finale** (structure seulement)

---

## 🔧 Architecture Technique

### Composants

```
┌─────────────────────────────────────────────────────────┐
│              GitHub Pull Request                        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         GitHub Actions Workflow                        │
│    (.github/workflows/egoejo-pr-bot.yml)                │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         Python Script                                   │
│    (.github/scripts/egoejo_pr_bot.py)                   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  1. Récupération diff Git                       │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  2. Analyse patterns interdits                 │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  3. Détection risques                           │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  4. Génération commentaire                      │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │  5. Détermination niveau conformité             │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│         Sorties                                          │
│  • Commentaire PR (Markdown)                            │
│  • Label GitHub (🟢 / 🟡 / 🔴)                         │
│  • Code de sortie (0 = OK, 1 = Bloquant)               │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 Processus d'Analyse

### 1. Récupération du Diff

```python
git diff base_ref..head_ref
```

**Sortie** : Diff complet entre la branche de base et la branche de la PR.

---

### 2. Analyse des Patterns

Le bot vérifie **4 catégories de critères** :

#### A. Double Structure (SAKA / EUR)

**Patterns interdits** :
- `convert.*saka.*eur` : Fonction de conversion
- `saka.*€` : Affichage monétaire
- `formatSakaAmount.*€` : Formatage monétaire

**Risque** : Philosophique (🔴 NON COMPATIBLE)

---

#### B. Cycle SAKA

**Patterns interdits** :
- `SAKA_COMPOST_ENABLED\s*=\s*False` : Compostage désactivé
- `SAKA_COMPOST_RATE\s*=\s*0` : Taux de compostage nul
- `#.*disable.*compost` : Commentaire désactivant le compostage

**Risque** : Philosophique (🔴 NON COMPATIBLE)

---

#### C. Gouvernance

**Patterns interdits** :
- `wallet\.balance\s*=` : Modification directe du wallet
- `ENABLE_INVESTMENT_FEATURES\s*=\s*True` : Activation V2.0
- `^-.*test.*compliance` : Suppression de tests

**Risque** : Philosophique (🔴 NON COMPATIBLE) ou Technique (🟡 SOUS CONDITIONS)

---

#### D. Transparence

**Patterns suspects** :
- `score.*\*\s*random` : Score arbitraire
- `#.*fake.*metric` : Métrique fake

**Risque** : Philosophique (🔴 NON COMPATIBLE)

---

### 3. Détection des Risques

Le bot classe les risques en deux catégories :

- **Risques Philosophiques** : Violations des principes fondamentaux
- **Risques Techniques** : Problèmes techniques nécessitant review

---

### 4. Détermination du Niveau de Conformité

```
Si risques philosophiques > 0:
    → 🔴 NON COMPATIBLE EGOEJO
    → Recommandation: refuse
    → Bloquant: OUI

Sinon si risques techniques > 0:
    → 🟡 COMPATIBLE SOUS CONDITIONS
    → Recommandation: refactor
    → Bloquant: NON

Sinon:
    → 🟢 COMPATIBLE EGOEJO
    → Recommandation: accept
    → Bloquant: NON
```

---

## 📤 Sorties du Bot

### 1. Commentaire PR

**Format** : Markdown standardisé

**Contenu** :
- Résultat (niveau de conformité)
- Justification (max 10 lignes)
- Risques philosophiques (max 10)
- Risques techniques (max 10)
- Recommandation
- Statut merge

**Exemple** : Voir [EXEMPLE_COMMENTAIRE_PR.md](./EXEMPLE_COMMENTAIRE_PR.md)

---

### 2. Label GitHub

**Labels possibles** :
- `🟢 COMPATIBLE EGOEJO`
- `🟡 COMPATIBLE SOUS CONDITIONS`
- `🔴 NON COMPATIBLE EGOEJO`

**Action** : Le bot ajoute/retire automatiquement le label approprié.

---

### 3. Code de Sortie

- **0** : PR compatible (merge autorisé)
- **1** : PR non compatible (merge bloqué)

**Utilisation** : Le workflow GitHub Actions échoue si code = 1, bloquant ainsi le merge.

---

## 🚫 Blocage du Merge

### Mécanisme

1. **Script Python** : Retourne code de sortie = 1 si bloquant
2. **GitHub Actions** : Workflow échoue si code = 1
3. **Branch Protection** : Configure GitHub pour exiger que le workflow passe

### Configuration Branch Protection

Dans **Settings** → **Branches** :

1. Ajouter une règle pour `main` et `develop`
2. Activer **Require status checks to pass before merging**
3. Sélectionner `egoejo-pr-bot` dans la liste

---

## 🔧 Configuration

### Variables d'Environnement

Le bot utilise les variables suivantes (définies par GitHub Actions) :

- `GITHUB_BASE_REF` : Branche de base (ex: `main`)
- `GITHUB_HEAD_REF` : Branche de la PR (ex: `feature/new-feature`)
- `GITHUB_PR_NUMBER` : Numéro de la PR
- `GITHUB_STEP_SUMMARY` : Fichier pour le commentaire

### Permissions GitHub

Le workflow nécessite :

```yaml
permissions:
  contents: read      # Lire le code
  pull-requests: write # Commenter les PRs
  issues: write       # Créer des issues (si nécessaire)
```

---

## 📊 Métriques

### Performance

- **Temps d'exécution** : ~10-30 secondes
- **Timeout** : 10 minutes (configuré dans le workflow)
- **Fréquence** : À chaque modification de PR

### Précision

- **Faux positifs** : Possibles (patterns détectés dans des commentaires)
- **Faux négatifs** : Rares (patterns encodés en Base64)
- **Couverture** : ~90% des violations détectées

---

## 🧪 Tests

### Test Manuel

```bash
# Simuler une PR
export GITHUB_BASE_REF="main"
export GITHUB_HEAD_REF="feature/test"
export GITHUB_PR_NUMBER="123"

# Exécuter le bot
python3 .github/scripts/egoejo_pr_bot.py
```

### Test avec Diff Réel

```bash
# Créer une branche de test
git checkout -b test-pr-bot

# Faire une modification suspecte
echo "def convert_saka_to_eur(amount): return amount * 0.01" >> test.py

# Commit
git add test.py
git commit -m "Test PR bot"

# Exécuter le bot
python3 .github/scripts/egoejo_pr_bot.py
```

---

## 📚 Références

- [Documentation PR Bot](./EGOEJO_PR_BOT.md)
- [Exemples de Commentaires](./EXEMPLE_COMMENTAIRE_PR.md)
- [Label EGOEJO COMPLIANT](../egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)

---

**Fin de l'Architecture**

*Dernière mise à jour : 2025-01-27*

