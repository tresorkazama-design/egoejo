# Script d'Audit Statique - Pages Accueil & Vision

**Fichier** : `scripts/audit-home-vision.js`  
**Usage** : `npm run audit:home-vision`

---

## 🎯 Objectif

Ce script vérifie statiquement que les pages Accueil et Vision respectent les exigences de l'audit quadripartite strict.

---

## ✅ Règles Vérifiées

### 1. Texte "100 % des dons" sans "nets" ou mention de frais

**Règle** : Toute mention de "100 % des dons" ou "100% des dons" doit inclure "nets" ou une mention de frais.

**Patterns acceptables** :
- `100% des dons nets`
- `100% des dons après frais`
- `100% des dons net`
- `100% des dons after fees`
- `100% des dons frais plateforme`
- `100% des dons platform fees`

**Fichiers scannés** :
- `src/app/pages/Home.jsx`
- `src/app/pages/Vision.jsx`
- `src/components/Layout.jsx`
- `src/locales/*.json` (clé `home.soutenir_desc`)

---

### 2. Clés i18n vision.principles_* et vision.glossary_*

**Règle** : Les clés i18n suivantes doivent exister dans tous les fichiers de traduction :

**Principes fondamentaux** :
- `vision.principles_title`
- `vision.principle_relational_title`
- `vision.principle_relational_desc`
- `vision.principle_anti_accumulation_title`
- `vision.principle_anti_accumulation_desc`
- `vision.principle_cycle_title`
- `vision.principle_cycle_desc`

**Glossaire** :
- `vision.glossary_title`
- `vision.glossary_vivant_term`
- `vision.glossary_vivant_def`
- `vision.glossary_gardiens_term`
- `vision.glossary_gardiens_def`
- `vision.glossary_alliance_term`
- `vision.glossary_alliance_def`

**Fichiers vérifiés** :
- `src/locales/fr.json`
- `src/locales/en.json`
- `src/locales/es.json`
- `src/locales/de.json`
- `src/locales/ar.json`
- `src/locales/sw.json`

---

### 3. Skip-link hardcodé en FR dans Layout.jsx

**Règle** : Le skip-link ne doit pas contenir le texte hardcodé "Aller au contenu principal" en dehors d'un appel à `t("accessibility.skip_to_main", language)`.

**Fichier vérifié** :
- `src/components/Layout.jsx`

**Pattern détecté** :
- `>Aller au contenu principal<` (texte hardcodé dans JSX)

**Solution** :
- Utiliser `{t("accessibility.skip_to_main", language)}`

---

## 📊 Format du Rapport

Le script génère un rapport structuré avec :

```
📊 RAPPORT D'AUDIT - Pages Accueil & Vision
================================================================================

❌ X violation(s) détectée(s) :

🔴 Règle violée : DONATION_TEXT_MISSING_NETS
   Nombre de violations : X

   📄 Fichier : src/locales/fr.json
   📍 Ligne   : 50
   ⚠️  Message : "100% des dons" trouvé sans "nets" ou mention de frais...
```

---

## 🚀 Usage

### Local
```bash
cd frontend/frontend
npm run audit:home-vision
```

### Dans CI/CD
Le script est automatiquement exécuté dans le workflow GitHub Actions `.github/workflows/audit-home-vision.yml`.

---

## ⚙️ Code de Sortie

- **0** : Aucune violation détectée
- **1** : Violation(s) détectée(s)

---

## 🔧 Dépannage

### Le script échoue sur "100 % des dons"

**Solution** : Modifiez le texte dans `src/locales/*.json` (clé `home.soutenir_desc`) pour inclure "nets" ou mention de frais :

```json
"soutenir_desc": "Chaque contribution alimente des actions concrètes : refuges, jardins nourriciers, ateliers de transmission, résidences de recherche, accompagnement des communautés locales. 100 % des dons nets (après frais de plateforme HelloAsso/Stripe) sont utilisés pour financer ces projets."
```

### Le script échoue sur les clés i18n manquantes

**Solution** : Ajoutez les clés manquantes dans tous les fichiers de traduction :

```json
"vision": {
  "principles_title": "Principes fondamentaux",
  "principle_relational_title": "Structure relationnelle > instrumentale",
  "principle_relational_desc": "...",
  // etc.
}
```

### Le script échoue sur le skip-link hardcodé

**Solution** : Vérifiez que `Layout.jsx` utilise `t("accessibility.skip_to_main", language)` et non un texte hardcodé.

---

## 📚 Documentation Associée

- [AUDIT_QUADRIPARTITE_STRICT_ACCUEIL_VISION.md](../../docs/reports/AUDIT_QUADRIPARTITE_STRICT_ACCUEIL_VISION.md)
- [TESTS_AUDIT_COMPLIANCE_ACCUEIL_VISION.md](../TESTS_AUDIT_COMPLIANCE_ACCUEIL_VISION.md)

---

**Dernière mise à jour** : 2025-01-27

