# 🤖 EGOEJO Guardian

Bot d'analyse des Pull Requests pour garantir la conformité avec la constitution EGOEJO.

## 📋 Objectif

Le Guardian EGOEJO analyse automatiquement chaque Pull Request pour vérifier qu'elle respecte :

- **Double structure économique** : SAKA prioritaire, EUR dormante
- **Règles absolues** : Pas de conversion SAKA ↔ EUR, pas de rendement, cycle non négociable
- **Tests obligatoires** : Les changements SAKA doivent avoir des tests associés

## 🚀 Usage

### Analyser une PR GitHub

```bash
# Avec token dans variable d'environnement
export GITHUB_TOKEN=your_token_here
python .egoejo/guardian.py <pr_number>

# Avec token en argument
python .egoejo/guardian.py <pr_number> --github-token your_token

# Spécifier le repository
python .egoejo/guardian.py <pr_number> --repo owner/repo
```

### Analyser un diff local

```bash
python .egoejo/guardian.py --diff path/to/diff.patch
```

### Sauvegarder le rapport

```bash
python .egoejo/guardian.py <pr_number> --output rapport.md
```

## 📊 Verdicts

### 🟢 COMPATIBLE EGOEJO
La PR respecte toutes les règles de la constitution EGOEJO.

**Action** : Approbation automatique

### 🟡 COMPATIBLE SOUS CONDITIONS
La PR est compatible mais nécessite des ajustements :
- Tests manquants pour changements SAKA
- Documentation manquante
- Feature flags non vérifiés

**Action** : Demande de changements

### 🔴 NON COMPATIBLE EGOEJO
La PR viole les règles absolues de la constitution EGOEJO :
- Conversion SAKA ↔ EUR
- Rendement financier basé sur SAKA
- Suppression ou contournement du compostage
- Optimisation au détriment du commun
- Priorité donnée à EUR sur SAKA

**Action** : Blocage de la PR

## 🔍 Règles vérifiées

### Règle 1 : Aucune conversion SAKA ↔ EUR
- Détecte : `saka.*eur`, `convert.*saka`, `saka.*price`, `saka.*exchange`, `saka.*rate`
- Sévérité : **CRITICAL**

### Règle 2 : Aucun rendement financier basé sur SAKA
- Détecte : `saka.*interest`, `saka.*dividend`, `saka.*yield`, `saka.*profit`, `saka.*return`
- Sévérité : **CRITICAL**

### Règle 3 : Aucun affichage monétaire du SAKA
- Détecte : `saka.*€`, `saka.*euro`, `saka.*currency`, `format.*saka.*money`
- Sévérité : **HIGH**

### Règle 4 : Le cycle SAKA est non négociable
- Détecte : `disable.*compost`, `skip.*compost`, `bypass.*compost`, `remove.*compost`
- Sévérité : **CRITICAL**

### Règle 5 : En cas de conflit : SAKA > EUR
- Détecte : `eur.*priority`, `saka.*disabled.*eur`
- Sévérité : **HIGH**

## 📁 Structure

```
.egoejo/
├── guardian.yml      # Configuration des règles
├── guardian.py       # Script d'analyse
└── README.md         # Documentation
```

## 🔧 Configuration

Le fichier `.egoejo/guardian.yml` contient :
- Règles de double structure (SAKA vs EUR)
- Patterns de détection des violations
- Règles de test
- Configuration des verdicts

## 🧪 Tests

Pour tester le Guardian localement :

```bash
# Créer un diff de test
git diff main > test.diff

# Analyser le diff
python .egoejo/guardian.py --diff test.diff
```

## 🔐 Intégration CI/CD

### GitHub Actions

```yaml
name: EGOEJO Guardian

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  guardian:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install requests pyyaml
      - name: Run EGOEJO Guardian
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .egoejo/guardian.py ${{ github.event.pull_request.number }}
```

## 📝 Exemple de rapport

Le Guardian génère un rapport markdown détaillé avec :
- Verdict final
- Violations détectées (avec code et suggestions)
- Fichiers SAKA/EUR modifiés
- Tests manquants
- Résumé statistique

## ⚠️ Important

Le Guardian est un outil de protection, pas de validation complète. Il détecte les violations évidentes mais ne remplace pas :
- La revue de code humaine
- Les tests d'intégration
- La vérification manuelle de la logique métier

## 🛡️ Philosophie

Le Guardian incarne la constitution EGOEJO dans le code :
- **SAKA est prioritaire** : Toute violation du cycle SAKA est bloquante
- **EUR est dormante** : Les features EUR ne doivent pas perturber SAKA
- **Transparence** : Chaque violation est expliquée avec suggestions

