# EGOEJO Compliance - Badge pour Projets Tiers

> **Principe** : "EGOEJO n'est pas une marque. C'est une contrainte volontaire."

## Qu'est-ce que EGOEJO Compliance ?

**EGOEJO Compliance** est un système de vérification automatique qui garantit qu'un projet respecte les principes fondamentaux d'EGOEJO :

- ✅ Double structure économique (SAKA prioritaire, EUR dormante)
- ✅ Anti-accumulation absolue
- ✅ Aucune conversion SAKA ↔ EUR
- ✅ Cycle SAKA non négociable
- ✅ Primauté du collectif

## Niveaux de Badge

### 🟢 EGOEJO Compatible

**Critères** :
- ✅ Aucune conversion SAKA ↔ EUR
- ✅ Aucun rendement financier basé sur SAKA
- ✅ Cycle SAKA complet et non négociable
- ✅ Tests de conformité présents et passent
- ✅ Banque (EUR) feature-flagged et dormante

**Badge** :
```markdown
[![EGOEJO Compatible](https://img.shields.io/badge/EGOEJO-Compatible-brightgreen)](https://github.com/egoejo/egoejo-compliance)
```

### 🟠 EGOEJO Compatible (Banque Dormante)

**Critères** :
- ✅ Respecte tous les critères du badge vert
- ⚠️ Banque (EUR) activée mais strictement séparée de SAKA
- ⚠️ Aucune contrainte EUR → SAKA

**Badge** :
```markdown
[![EGOEJO Compatible (Banque Dormante)](https://img.shields.io/badge/EGOEJO-Compatible%20%28Banque%20Dormante%29-orange)](https://github.com/egoejo/egoejo-compliance)
```

### 🔴 Non Compatible EGOEJO

**Cas** :
- ❌ Conversion SAKA ↔ EUR détectée
- ❌ Rendement financier basé sur SAKA
- ❌ Cycle SAKA contourné ou désactivé
- ❌ Banque contraint SAKA

**Badge** : Aucun badge affiché

---

## Installation

### 1. Copier les fichiers

Copiez le dossier `egoejo-compliance/` dans votre projet :

```bash
# Option 1 : Cloner le repo EGOEJO et copier le dossier
git clone https://github.com/egoejo/egoejo.git
cp -r egoejo/egoejo-compliance/ votre-projet/

# Option 2 : Télécharger uniquement le dossier
# (via GitHub interface ou wget)
```

### 2. Vérifier les dépendances

Le bot utilise uniquement Python standard (pas de dépendances externes).

**Prérequis** :
- Python 3.8+
- Git (pour `git diff`)

### 3. Configurer les règles (optionnel)

Modifiez `guardian_rules.yml` pour adapter les patterns à votre projet :

```yaml
# Exemple : Adapter les patterns de fichiers SAKA
saka_file_patterns:
  - "**/saka*.py"
  - "**/Saka*.py"
  - "votre-projet/services/saka.py"  # Votre structure
```

---

## Utilisation

### Exécution locale

```bash
# Depuis la racine de votre projet
python egoejo-compliance/guardian.py
```

**Exit codes** :
- `0` : 🟢 Compatible
- `1` : 🔴 Non Compatible
- `2` : 🟠 Compatible (Banque Dormante)

### Intégration GitHub Actions

Créez `.github/workflows/egoejo-compliance.yml` :

```yaml
name: EGOEJO Compliance Check

on:
  pull_request:
    types: [opened, synchronize, reopened]
  push:
    branches: [main]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Run EGOEJO Compliance Check
        run: |
          python egoejo-compliance/guardian.py
      
      - name: Add Badge Status
        if: always()
        uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const exitCode = process.env.EXIT_CODE || '0';
            let badge = '';
            
            if (exitCode === '0') {
              badge = '🟢 EGOEJO Compatible';
            } else if (exitCode === '2') {
              badge = '🟠 EGOEJO Compatible (Banque Dormante)';
            } else {
              badge = '🔴 Non Compatible EGOEJO';
            }
            
            // Ajouter un commentaire PR avec le badge
            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.issue.number,
              body: `## ${badge}\n\nVérification EGOEJO Compliance terminée.`
            });
```

### Intégration GitLab CI

Créez `.gitlab-ci.yml` :

```yaml
egoejo_compliance:
  image: python:3.11
  before_script:
    - pip install --upgrade pip
  script:
    - python egoejo-compliance/guardian.py
  artifacts:
    when: always
    reports:
      junit: egoejo-compliance-report.xml
```

---

## Obtenir le Badge

### Étape 1 : Exécuter le bot

```bash
python egoejo-compliance/guardian.py
```

### Étape 2 : Vérifier le résultat

- **Exit code 0** → 🟢 Compatible
- **Exit code 2** → 🟠 Compatible (Banque Dormante)
- **Exit code 1** → 🔴 Non Compatible

### Étape 3 : Ajouter le badge dans votre README

**Badge vert** :
```markdown
[![EGOEJO Compatible](https://img.shields.io/badge/EGOEJO-Compatible-brightgreen)](https://github.com/egoejo/egoejo-compliance)
```

**Badge orange** :
```markdown
[![EGOEJO Compatible (Banque Dormante)](https://img.shields.io/badge/EGOEJO-Compatible%20%28Banque%20Dormante%29-orange)](https://github.com/egoejo/egoejo-compliance)
```

### Étape 4 : Lier vers vos tests de conformité

Ajoutez un lien vers vos tests de conformité dans votre README :

```markdown
## EGOEJO Compliance

Ce projet respecte les principes EGOEJO :
- ✅ Double structure économique (SAKA prioritaire, EUR dormante)
- ✅ Anti-accumulation absolue
- ✅ Aucune conversion SAKA ↔ EUR

[Tests de conformité](egoejo-compliance/)
```

---

## Clause Anti-Capture

### Interdiction d'usage marketing abusif

**RÈGLE** : Le badge EGOEJO Compliant ne peut pas être utilisé pour :
- ❌ Promettre un rendement financier
- ❌ Garantir une performance économique
- ❌ Impliquer une valeur monétaire du SAKA
- ❌ Faire de la publicité mensongère

**Violation** : Le badge peut être révoqué si usage abusif détecté.

### Badge révocable

**Conditions de révocation** :
- Usage marketing abusif
- Violation des principes EGOEJO
- Tests de conformité non publics
- Refus de corriger les violations

**Processus** : Ouvrir une issue sur le repo EGOEJO avec preuves.

### Badge basé sur tests publics

**RÈGLE** : Le badge n'est valide que si :
- ✅ Les tests de conformité sont publics
- ✅ Les tests passent en CI
- ✅ Les résultats sont traçables

**Vérification** : Toute personne peut exécuter `python egoejo-compliance/guardian.py` et obtenir le même résultat.

---

## Licence

### Code

**MIT License** : Le code du bot est sous licence MIT, libre d'utilisation.

### Badge

**Creative Commons Attribution-NoDerivatives 4.0** : Le badge peut être utilisé librement, mais :
- ✅ Attribution requise
- ❌ Pas de modification du badge
- ❌ Pas d'usage commercial sans autorisation

### Principe

> "EGOEJO n'est pas une marque. C'est une contrainte volontaire."

Le badge atteste d'une **contrainte volontaire**, pas d'une certification officielle.

---

## Exemples d'Intégration

### Exemple 1 : Projet Python/Django

```yaml
# .github/workflows/egoejo-compliance.yml
name: EGOEJO Compliance

on: [pull_request, push]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Check EGOEJO Compliance
        run: python egoejo-compliance/guardian.py
```

### Exemple 2 : Projet Node.js/TypeScript

```yaml
# .github/workflows/egoejo-compliance.yml
name: EGOEJO Compliance

on: [pull_request, push]

jobs:
  compliance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Check EGOEJO Compliance
        run: python egoejo-compliance/guardian.py
        # Note : Le bot fonctionne même pour des projets non-Python
        # Il analyse les fichiers modifiés via git diff
```

### Exemple 3 : GitLab CI

```yaml
# .gitlab-ci.yml
egoejo_compliance:
  image: python:3.11
  script:
    - python egoejo-compliance/guardian.py
  allow_failure: false
```

---

## FAQ

### Q : Puis-je utiliser le badge sans être un projet EGOEJO ?

**R** : Oui. Le badge atteste que votre projet respecte les principes EGOEJO, pas qu'il fait partie de la plateforme EGOEJO.

### Q : Le badge est-il une certification officielle ?

**R** : Non. Le badge atteste d'une **contrainte volontaire** vérifiée automatiquement, pas d'une certification officielle.

### Q : Puis-je modifier le bot pour mon projet ?

**R** : Oui, le code est sous licence MIT. Vous pouvez l'adapter à vos besoins.

### Q : Dois-je payer pour utiliser le badge ?

**R** : Non. Le badge est gratuit et open-source. Aucun SaaS obligatoire.

### Q : Y a-t-il un serveur central à contacter ?

**R** : Non. Le bot fonctionne localement. Aucun serveur central requis.

### Q : Comment signaler un usage abusif du badge ?

**R** : Ouvrir une issue sur le repo EGOEJO avec preuves. Le badge peut être révoqué.

---

## Références

- **Constitution EGOEJO** : [docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md](../docs/compliance/EGOEJO_CONSTITUTION_EXECUTABLE.md)
- **Gouvernance EGOEJO** : [docs/governance/GOVERNANCE_EGOEJO.md](../docs/governance/GOVERNANCE_EGOEJO.md)
- **Principe Fondamental** : [docs/governance/PRINCIPE_FONDAMENTAL.md](../docs/governance/PRINCIPE_FONDAMENTAL.md)

---

## Support

Pour toute question ou problème :
- Ouvrir une issue sur le repo EGOEJO
- Consulter la documentation EGOEJO
- Examiner les exemples d'intégration

---

**Dernière mise à jour** : 2025-12-18

**Version** : 1.0

