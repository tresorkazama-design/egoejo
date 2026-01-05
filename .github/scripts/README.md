# EGOEJO PR Bot

Bot de gouvernance automatisé pour analyser les Pull Requests selon les règles de conformité EGOEJO.

## 🎯 Objectif

Le bot agit comme un **Comité de Mission automatisé** qui :
- Analyse automatiquement chaque PR
- Détecte les violations philosophiques et techniques
- Poste des commentaires sur GitHub
- Applique des labels de conformité
- Bloque le merge si violation critique

## 🚀 Fonctionnalités

### 1. Analyse Automatique

Le bot scanne automatiquement :
- **Double structure** (SAKA / EUR) : Conversion interdite
- **Cycle SAKA** : Compostage, anti-accumulation
- **Gouvernance** : Modification directe wallet, activation V2.0
- **Transparence** : Scores arbitraires, métriques suspectes
- **Tests** : Suppression de tests de compliance

### 2. Commentaire GitHub

Le bot poste automatiquement un commentaire sur chaque PR avec :
- Niveau de conformité (🟢 / 🟡 / 🔴)
- Liste des risques détectés
- Recommandation (accept / refactor / refuse)
- Statut de blocage

### 3. Labels Automatiques

Le bot applique automatiquement les labels :
- `egoejo:compliant` (vert) : PR conforme
- `egoejo:violation` (rouge) : Violation critique détectée
- `egoejo:review-needed` (jaune) : Risques techniques nécessitant review

### 4. Blocage du Merge

Si une violation critique est détectée :
- Le bot crée une review `REQUEST_CHANGES`
- Le merge est bloqué jusqu'à correction
- Le code de sortie est `1` (échec)

## 📋 Utilisation

### Variables d'Environnement Requises

```bash
GITHUB_TOKEN          # Token GitHub avec permissions PR
GITHUB_REPOSITORY     # Format: owner/repo
GITHUB_PR_NUMBER      # Numéro de la PR
GITHUB_BASE_REF       # Branche de base (ex: main)
GITHUB_HEAD_REF       # Branche de la PR
```

### Exécution Locale

```bash
# Installer les dépendances
pip install requests

# Exécuter le bot
export GITHUB_TOKEN="your_token"
export GITHUB_REPOSITORY="owner/repo"
export GITHUB_PR_NUMBER="123"
export GITHUB_BASE_REF="main"
export GITHUB_HEAD_REF="feature/branch"

python .github/scripts/egoejo_pr_bot.py
```

### Exécution via GitHub Actions

Le workflow `.github/workflows/egoejo-pr-bot.yml` s'exécute automatiquement sur :
- `opened` : PR ouverte
- `synchronize` : Nouveau commit sur la PR
- `reopened` : PR rouverte

## 🧪 Tests

Les tests simulent des PRs fautives pour vérifier la détection :

```bash
python .github/scripts/__tests__/test_egoejo_pr_bot.py
```

### Tests Inclus

1. **test_pr_with_saka_eur_conversion** : Conversion SAKA ↔ EUR
2. **test_pr_with_monetary_display** : Affichage monétaire SAKA
3. **test_pr_with_compost_disabled** : Désactivation compostage
4. **test_pr_with_investment_activation** : Activation V2.0 sans contrôle
5. **test_pr_with_test_removal** : Suppression de tests compliance
6. **test_pr_with_direct_wallet_modification** : Modification directe wallet
7. **test_pr_compliant** : PR conforme (aucune violation)

## 🔍 Patterns Détectés

### Violations Philosophiques (Bloquantes)

- Conversion SAKA ↔ EUR
- Affichage monétaire SAKA (€, $, USD, EUR, GBP)
- Désactivation du compostage
- Activation V2.0 sans feature flag
- Suppression de tests de compliance

### Risques Techniques (Review Nécessaire)

- Modification directe du wallet
- Modification des services SAKA critiques
- Modification des settings SAKA

## 📊 Niveaux de Conformité

### 🟢 COMPATIBLE EGOEJO

- Aucun risque détecté
- Merge autorisé
- Label : `egoejo:compliant`

### 🟡 COMPATIBLE SOUS CONDITIONS

- Risques techniques détectés
- Review technique recommandée
- Merge autorisé après review
- Label : `egoejo:review-needed`

### 🔴 NON COMPATIBLE EGOEJO

- Violations philosophiques détectées
- Merge bloqué
- Correction obligatoire
- Label : `egoejo:violation`

## 🛡️ Philosophie du Bot

Le bot respecte strictement la **Constitution EGOEJO** :
- Aucun assouplissement temporaire
- Détection stricte des violations
- Blocage automatique si violation critique
- Rapport détaillé avec actions requises

## 📚 Références

- [Label EGOEJO COMPLIANT](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)
- [Constitution EGOEJO](../../EGOEJO_ARCHITECTURE_CONSTITUTION.md)
- [Actions de Défense Hostile](../../docs/security/ACTIONS_DEFENSE_HOSTILE.md)
