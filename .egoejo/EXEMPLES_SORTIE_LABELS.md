# Exemples de Sortie pour les Labels Automatiques

## 🟢 COMPATIBLE EGOEJO

### Exemple 1 : PR avec changements SAKA et tests

```
## 🟢 COMPATIBLE EGOEJO

✅ **Aucune violation détectée**
✅ **Tests présents** pour changements SAKA
✅ **Feature flags respectés**

Cette PR respecte la constitution EGOEJO.
```

### Exemple 2 : PR avec changements non-SAKA

```
## 🟢 COMPATIBLE EGOEJO

✅ **Aucune violation détectée**
✅ **Aucun changement SAKA** - Pas de tests requis
✅ **Feature flags respectés**

Cette PR respecte la constitution EGOEJO.
```

---

## 🟡 COMPATIBLE SOUS CONDITIONS

### Exemple 1 : Tests manquants

```
## 🟡 COMPATIBLE SOUS CONDITIONS

⚠️ **Tests manquants** : 2 fichier(s) SAKA sans tests
⚠️ **backend/core/services/saka.py** modifié sans tests
⚠️ **backend/core/models/saka.py** modifié sans tests

**ACTION REQUISE** : Ajouter tests/documentation avant approbation.
```

### Exemple 2 : Violation importante (affichage monétaire)

```
## 🟡 COMPATIBLE SOUS CONDITIONS

⚠️ **No Monetary Display** : 1 violation(s) importante(s)
⚠️ **Fichier** : frontend/src/components/SakaBalance.jsx, Ligne 42

**ACTION REQUISE** : Corriger l'affichage monétaire du SAKA.
```

### Exemple 3 : Documentation manquante

```
## 🟡 COMPATIBLE SOUS CONDITIONS

⚠️ **Documentation manquante** : Changements SAKA sans docstrings
⚠️ **backend/core/services/saka.py** : Fonction `new_saka_feature()` sans docstring

**ACTION REQUISE** : Ajouter docstrings explicites pour les changements SAKA.
```

---

## 🔴 NON COMPATIBLE EGOEJO

### Exemple 1 : Conversion SAKA ↔ EUR

```
## 🔴 NON COMPATIBLE EGOEJO

❌ **No Conversion** : backend/core/services/saka.py (ligne 42)
❌ **Pattern détecté** : `convert_saka_to_eur(saka_amount)`

**ACTION REQUISE** : SUPPRIMER toute logique de conversion SAKA ↔ EUR.
```

### Exemple 2 : Désactivation du compostage

```
## 🔴 NON COMPATIBLE EGOEJO

❌ **Saka Cycle Mandatory** : backend/core/services/saka.py (ligne 318)
❌ **Pattern détecté** : `if user.is_premium: skip_compost = True`

**ACTION REQUISE** : RESTAURER le compostage obligatoire (cycle SAKA non négociable).
```

### Exemple 3 : Référence EUR dans SAKA

```
## 🔴 NON COMPATIBLE EGOEJO

❌ **No Eur Reference In Saka Services** : backend/core/services/saka.py (ligne 15)
❌ **Import détecté** : `from finance.services import pledge_funds`

**ACTION REQUISE** : SUPPRIMER toute dépendance SAKA → EUR.
```

### Exemple 4 : Multiple violations critiques

```
## 🔴 NON COMPATIBLE EGOEJO

❌ **No Conversion** : backend/core/services/saka.py (ligne 42)
❌ **Saka Cycle Mandatory** : backend/core/services/saka.py (ligne 318)
... et 2 autre(s) violation(s) critique(s)

**ACTION REQUISE** : Corriger les violations critiques avant merge.
```

---

## Format du Commentaire GitHub

Le commentaire est automatiquement posté sur la PR avec :

1. **Label automatique** : Ajouté via GitHub API
2. **Commentaire de justification** : Max 5 lignes, format markdown
3. **Rapport détaillé** : Disponible dans les artefacts CI/CD

### Structure du Commentaire

```markdown
## [LABEL]

[Justification en 5 lignes max]

[Action requise si nécessaire]
```

---

## Règles de Génération

1. **🟢** : Généré si AUCUNE violation (critique ou importante)
2. **🟡** : Généré si violations importantes UNIQUEMENT (pas de critiques)
3. **🔴** : Généré si AU MOINS UNE violation critique

**Priorité absolue** : Toute violation critique = 🔴 immédiat, même si tout le reste est OK.

