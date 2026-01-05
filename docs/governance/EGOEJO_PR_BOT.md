# 🤖 EGOEJO PR Bot - Documentation

**Version** : 1.0  
**Date** : 2025-01-27  
**Statut** : Bot de Gouvernance Automatisée

---

## 🎯 Objectif

Le **EGOEJO PR Bot** agit comme un **Comité de Mission automatisé** qui analyse chaque Pull Request selon les règles de gouvernance EGOEJO et attribue un label de conformité **BLOQUANT** ou **NON**.

---

## 🏗️ Architecture

### Composants

1. **Script Python** (`.github/scripts/egoejo_pr_bot.py`)
   - Analyse le diff Git
   - Détecte les violations philosophiques et techniques
   - Génère un commentaire de PR
   - Détermine le niveau de conformité

2. **Workflow GitHub Actions** (`.github/workflows/egoejo-pr-bot.yml`)
   - Déclenché sur chaque PR (opened, synchronize, reopened)
   - Exécute le script Python
   - Poste le commentaire sur la PR
   - Définit le label de conformité
   - Bloque le merge si nécessaire

### Flux d'Exécution

```
PR ouverte/modifiée
    ↓
GitHub Actions déclenché
    ↓
Checkout code + Setup Python
    ↓
Exécution egoejo_pr_bot.py
    ↓
Analyse diff Git
    ↓
Détection violations
    ↓
Génération commentaire
    ↓
Post commentaire PR
    ↓
Définition label
    ↓
Blocage merge (si nécessaire)
```

---

## 📊 Niveaux de Conformité

### 🟢 COMPATIBLE EGOEJO

**Critères** :
- ✅ Aucun risque philosophique détecté
- ✅ Aucun risque technique détecté

**Action** :
- Label : `🟢 COMPATIBLE EGOEJO`
- Recommandation : `accept`
- Merge : ✅ **AUTORISÉ**

---

### 🟡 COMPATIBLE SOUS CONDITIONS

**Critères** :
- ✅ Aucun risque philosophique détecté
- ⚠️ Risques techniques détectés

**Action** :
- Label : `🟡 COMPATIBLE SOUS CONDITIONS`
- Recommandation : `refactor`
- Merge : ✅ **AUTORISÉ** (mais review technique recommandée)

---

### 🔴 NON COMPATIBLE EGOEJO

**Critères** :
- ❌ Risques philosophiques détectés

**Action** :
- Label : `🔴 NON COMPATIBLE EGOEJO`
- Recommandation : `refuse`
- Merge : 🚫 **BLOQUÉ**

---

## 🔍 Critères d'Analyse

### 1. Double Structure (SAKA / EUR)

**Vérifications** :
- ❌ Aucune fonction de conversion SAKA ↔ EUR
- ❌ Aucun endpoint API de conversion
- ❌ Aucun affichage monétaire du SAKA (€, $, USD, EUR, GBP)

**Patterns Détectés** :
```python
# Patterns interdits
"convert.*saka.*eur"
"saka.*€"
"formatSakaAmount.*€"
```

---

### 2. Cycle SAKA

**Vérifications** :
- ❌ Compostage non désactivé (`SAKA_COMPOST_ENABLED=False`)
- ❌ Taux de compostage non nul (`SAKA_COMPOST_RATE=0`)
- ❌ Jours d'inactivité raisonnables (`SAKA_COMPOST_INACTIVITY_DAYS <= 365`)
- ❌ Aucune accumulation passive possible

**Patterns Détectés** :
```python
# Patterns interdits
"SAKA_COMPOST_ENABLED\s*=\s*False"
"SAKA_COMPOST_RATE\s*=\s*0"
"#.*disable.*compost"
```

---

### 3. Gouvernance

**Vérifications** :
- ❌ Aucune modification directe du wallet SAKA (`wallet.balance =`)
- ❌ V2.0 non activée (`ENABLE_INVESTMENT_FEATURES=True`)
- ❌ Tests de compliance non supprimés

**Patterns Détectés** :
```python
# Patterns interdits
"wallet\.balance\s*="
"ENABLE_INVESTMENT_FEATURES\s*=\s*True"
"^-.*test.*compliance"
```

---

### 4. Transparence

**Vérifications** :
- ❌ Aucun score arbitraire (`score * random`)
- ❌ Aucune métrique fake (`# fake metric`)

**Patterns Détectés** :
```python
# Patterns suspects
"score.*\*\s*random"
"#.*fake.*metric"
```

---

## 💬 Format de Commentaire

Le bot génère un commentaire standardisé avec :

1. **Résultat** : Niveau de conformité (🟢 / 🟡 / 🔴)
2. **Justification** : Explication courte (max 10 lignes)
3. **Risques Philosophiques** : Liste des violations philosophiques
4. **Risques Techniques** : Liste des risques techniques
5. **Recommandation** : `accept` / `refactor` / `refuse`
6. **Statut Merge** : Autorisé ou Bloqué

### Exemple de Commentaire

```markdown
## 🤖 EGOEJO PR Bot - Analyse de Conformité

### 📊 Résultat

**🔴 NON COMPATIBLE EGOEJO**

❌ VIOLATION PHILOSOPHIQUE DÉTECTÉE

2 risque(s) philosophique(s) identifié(s). 
Cette PR viole les principes fondamentaux d'EGOEJO.

### 🔍 Détails

#### ⚠️ Risques Philosophiques (2)

1. **Pattern 'conversion_saka_eur' détecté: def convert_saka_to_eur**
   - 📁 `backend/core/services/saka_conversion.py` (ligne 15)

2. **Pattern 'compost_disabled' détecté: SAKA_COMPOST_ENABLED = False**
   - 📁 `backend/config/settings.py` (ligne 499)

### 💡 Recommandation

**REFUSE**

🚫 **MERGE BLOQUÉ** - Cette PR ne peut pas être mergée sans correction.

---

*Ce commentaire est généré automatiquement par le bot de gouvernance EGOEJO.*
```

---

## 🚫 Blocage du Merge

### Mécanisme

Le bot bloque le merge si :
- ❌ Risques philosophiques détectés
- ❌ Label `🔴 NON COMPATIBLE EGOEJO` attribué
- ❌ Code de sortie du script = 1

### Implémentation

1. **GitHub Actions** : Le workflow échoue si le bot retourne un code d'erreur
2. **Branch Protection** : Configurer GitHub pour exiger que le workflow `egoejo-pr-bot` passe
3. **Commentaire** : Le bot poste un commentaire expliquant le blocage

### Configuration Branch Protection

Dans les paramètres GitHub du repository :

1. Aller dans **Settings** → **Branches**
2. Ajouter une règle pour `main` et `develop`
3. Activer **Require status checks to pass before merging**
4. Sélectionner `egoejo-pr-bot` dans la liste

---

## 🔧 Configuration

### Variables d'Environnement

Le bot utilise les variables d'environnement suivantes :

- `GITHUB_BASE_REF` : Branche de base (ex: `main`)
- `GITHUB_HEAD_REF` : Branche de la PR (ex: `feature/new-feature`)
- `GITHUB_PR_NUMBER` : Numéro de la PR
- `GITHUB_STEP_SUMMARY` : Fichier pour le commentaire

### Permissions GitHub

Le workflow nécessite les permissions suivantes :

```yaml
permissions:
  contents: read
  pull-requests: write
  issues: write
```

---

## 📝 Limitations

### Ce que le Bot NE FAIT PAS

- ❌ **Ne modifie jamais le code** : Le bot est en lecture seule
- ❌ **N'active jamais la V2.0** : Le bot ne peut pas activer des features
- ❌ **Ne remplace pas l'humain** : Le bot structure la décision, ne la prend pas

### Ce que le Bot FAIT

- ✅ **Analyse le diff** : Détecte les patterns interdits
- ✅ **Génère un commentaire** : Informe les contributeurs
- ✅ **Définit un label** : Facilite le tri des PRs
- ✅ **Bloque le merge** : Protège la philosophie EGOEJO

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

- [Label EGOEJO COMPLIANT](../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)
- [Simulation Hostile](../../docs/security/SIMULATION_HOSTILE_INVESTISSEUR.md)
- [Architecture Constitution](../../EGOEJO_ARCHITECTURE_CONSTITUTION.md)

---

**Fin de la Documentation**

*Dernière mise à jour : 2025-01-27*

