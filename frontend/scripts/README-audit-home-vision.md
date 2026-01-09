# Script d'audit BLOQUANT Home/Vision

## Description

Script Node.js qui scanne le code et échoue (`exit 1`) si des violations de conformité EGOEJO sont détectées.

## Installation

Le script est déjà intégré dans `package.json` :

```json
{
  "scripts": {
    "audit:home-vision": "node scripts/audit-home-vision.mjs"
  }
}
```

## Usage

### Mode texte (par défaut)

```bash
npm run audit:home-vision
```

### Mode JSON (machine-readable)

```bash
npm run audit:home-vision -- --json
```

## Règles vérifiées

### 1. Règle DONATION_TEXT_MISSING_NETS

**Objectif** : Détecter "100% des dons" sans précision "nets" ou mention de frais.

**Pattern détecté** : `100\s*%\s*des?\s*dons?` (insensible à la casse)

**Acceptable si contient** :
- `nets` ou `net`
- `frais`, `fees`, `helloasso`, `stripe`, `plateforme`, `platform`

**Fichiers scannés** : Tous les fichiers JSON dans `src/locales/`

### 2. Règle SKIP_LINK_HARDCODED_FR

**Objectif** : Détecter le skip-link hardcodé en français dans `Layout.jsx`.

**Patterns interdits** :
- `"Aller au contenu principal"`
- `"Aller au contenu"`
- `"Passer au contenu"`

**Acceptable si** : Utilise `t()` ou `i18n` pour la traduction.

**Fichier scanné** : `src/components/Layout.jsx`

### 3. Règle I18N_KEY_MISSING

**Objectif** : Vérifier l'existence des clés i18n minimales.

**Clés requises** :
- `accessibility.skip_to_main`
- `vision.principles_title`
- `vision.glossary_title`
- `vision.citations_disclaimer` (ou alternatives : `vision.disclaimer`, `vision.citations_note`)
- `home.saka_eur_note` (ou alternatives : `home.saka_eur_note_title`, `home.saka_eur_separation`)
- `home.soutenir_desc`

**Fichiers scannés** : Tous les fichiers JSON dans `src/locales/`

## Exemple de sortie (mode texte)

```
🔍 Audit BLOQUANT Home/Vision - EGOEJO Compliance

❌ VIOLATIONS DÉTECTÉES

================================================================================

🔴 Règle: DONATION_TEXT_MISSING_NETS
--------------------------------------------------------------------------------

  Violation 1:
  Fichier: C:\Users\treso\Downloads\egoejo\frontend\frontend\src\locales\fr.json
  Ligne: 50
  Clé: home.soutenir_desc
  Extrait: Chaque contribution alimente des actions concrètes : refuges, jardins nourriciers, ateliers de transmission, résidences de recherche, accompagnement d
  Description: "100% des dons" trouvé sans "nets" ou mention de frais dans home.soutenir_desc

🔴 Règle: I18N_KEY_MISSING
--------------------------------------------------------------------------------

  Violation 1:
  Fichier: C:\Users\treso\Downloads\egoejo\frontend\frontend\src\locales\ar.json
  Clé: accessibility.skip_to_main
  Description: Clé i18n manquante: accessibility.skip_to_main

  Violation 2:
  Fichier: C:\Users\treso\Downloads\egoejo\frontend\frontend\src\locales\ar.json
  Clé: vision.principles_title
  Description: Clé i18n manquante: vision.principles_title

================================================================================

❌ Total: 23 violation(s) détectée(s)
```

## Exemple de sortie (mode JSON)

```json
{
  "status": "non-compliant",
  "violations_count": 23,
  "violations": [
    {
      "rule": "DONATION_TEXT_MISSING_NETS",
      "file": "C:\\Users\\treso\\Downloads\\egoejo\\frontend\\frontend\\src\\locales\\fr.json",
      "line": 50,
      "key": "home.soutenir_desc",
      "content": "Chaque contribution alimente des actions concrètes : refuges, jardins nourriciers, ateliers de transmission, résidences de recherche, accompagnement d",
      "description": "\"100% des dons\" trouvé sans \"nets\" ou mention de frais dans home.soutenir_desc"
    },
    {
      "rule": "I18N_KEY_MISSING",
      "file": "C:\\Users\\treso\\Downloads\\egoejo\\frontend\\frontend\\src\\locales\\ar.json",
      "line": 0,
      "key": "accessibility.skip_to_main",
      "content": null,
      "description": "Clé i18n manquante: accessibility.skip_to_main"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

## Codes de sortie

- `0` : Aucune violation détectée (conformité OK)
- `1` : Violations détectées (non-conformité)

## Intégration CI/CD

Le script peut être intégré dans un workflow GitHub Actions :

```yaml
- name: Audit Home/Vision
  run: npm run audit:home-vision
```

Si des violations sont détectées, le workflow échouera automatiquement.

## Correction des violations

### Violation DONATION_TEXT_MISSING_NETS

**Exemple de correction** :

```json
// ❌ Avant
"home.soutenir_desc": "100 % des dons sont utilisés pour financer ces projets."

// ✅ Après
"home.soutenir_desc": "100% des dons nets (après frais de plateforme) sont utilisés pour financer ces projets."
```

### Violation SKIP_LINK_HARDCODED_FR

**Exemple de correction** :

```jsx
// ❌ Avant
<a href="#main-content">Aller au contenu principal</a>

// ✅ Après
<a href="#main-content">{t("accessibility.skip_to_main", language)}</a>
```

### Violation I18N_KEY_MISSING

**Exemple de correction** :

```json
{
  "accessibility": {
    "skip_to_main": "Aller au contenu principal"
  },
  "vision": {
    "principles_title": "Principes fondamentaux",
    "glossary_title": "Glossaire",
    "citations_disclaimer": "Note sur les citations autochtones..."
  },
  "home": {
    "saka_eur_note": "Note explicative sur SAKA et EUR...",
    "soutenir_desc": "100% des dons nets (après frais de plateforme)..."
  }
}
```

## Notes techniques

- Le script utilise des modules ES (`import`/`export`)
- Format de fichier : `.mjs` (ES Module)
- Compatible Node.js 14+
- Aucune dépendance externe requise (utilise uniquement les modules Node.js natifs)

