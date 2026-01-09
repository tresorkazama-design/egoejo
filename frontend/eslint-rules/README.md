# Règles ESLint Custom EGOEJO

Ce dossier contient les règles ESLint custom pour garantir la conformité au **Label EGOEJO COMPLIANT**.

## Règle : `no-monetary-symbols`

### Description

Interdit l'utilisation de symboles monétaires (€, $, USD, EUR, GBP, CHF, JPY, CAD, AUD) dans le code frontend.

**Violation du Label EGOEJO COMPLIANT** si :
- Un symbole monétaire est utilisé dans une string
- Un symbole monétaire est utilisé dans un commentaire
- Un symbole monétaire est utilisé dans du JSX

### Objectif

Protéger la philosophie EGOEJO en empêchant l'affichage monétaire du SAKA. Le SAKA est un "grain d'engagement", non une monnaie. Il doit être affiché en "grains", jamais avec un symbole monétaire.

### Utilisation

La règle est automatiquement activée dans `.eslintrc.cjs` :

```javascript
rules: {
  'egoejo/no-monetary-symbols': 'error',
}
```

### Exemples de violations

```javascript
// ❌ VIOLATION : Symbole monétaire dans une string
const price = "100 €";

// ❌ VIOLATION : Symbole monétaire dans un template literal
const message = `Prix: ${amount} USD`;

// ❌ VIOLATION : Symbole monétaire dans un commentaire
// Balance: 200 EUR

// ❌ VIOLATION : Symbole monétaire dans du JSX
const Component = () => <div>Prix: 100 €</div>;
```

### Exemples valides

```javascript
// ✅ VALIDE : Utilisation de "grains" pour SAKA
const amount = "100 grains";
const message = `Balance: ${balance} grains`;

// ✅ VALIDE : Utilisation de formatSakaAmount()
import { formatSakaAmount } from '../utils/saka';
const display = formatSakaAmount(100); // "100 grains"

// ✅ VALIDE : Commentaire sans symbole monétaire
// Balance: 100 grains
```

### Messages d'erreur

La règle génère des messages d'erreur clairs :

- **`monetarySymbolInString`** : "VIOLATION DU LABEL EGOEJO COMPLIANT : Symbole monétaire "{{symbol}}" détecté dans une string. Le SAKA ne doit jamais être affiché avec un symbole monétaire (€, $, USD, EUR, GBP, CHF). Utilisez formatSakaAmount() pour formater en "grains"."

- **`monetarySymbolInComment`** : "VIOLATION DU LABEL EGOEJO COMPLIANT : Symbole monétaire "{{symbol}}" détecté dans un commentaire. Les commentaires ne doivent pas suggérer une valeur monétaire pour le SAKA."

- **`monetarySymbolInJSX`** : "VIOLATION DU LABEL EGOEJO COMPLIANT : Symbole monétaire "{{symbol}}" détecté dans du JSX. Le SAKA ne doit jamais être affiché avec un symbole monétaire. Utilisez formatSakaAmount() pour formater en "grains"."

### Symboles interdits

- `€` (Euro)
- `$` (Dollar)
- `USD` (United States Dollar)
- `EUR` (Euro - code ISO)
- `GBP` (British Pound)
- `CHF` (Swiss Franc)
- `JPY` (Japanese Yen)
- `CAD` (Canadian Dollar)
- `AUD` (Australian Dollar)

### Tests

Les tests unitaires sont disponibles dans `__tests__/no-monetary-symbols.test.js`.

Exécution :
```bash
node eslint-rules/__tests__/no-monetary-symbols.test.js
```

### Références

- [Label EGOEJO COMPLIANT](../../../docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md)
- [Actions de Défense Hostile](../../../docs/security/ACTIONS_DEFENSE_HOSTILE.md)
- [Utils SAKA](../../src/utils/saka.ts)

