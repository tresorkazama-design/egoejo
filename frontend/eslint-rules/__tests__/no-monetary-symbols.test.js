/**
 * Tests unitaires pour la règle ESLint custom : no-monetary-symbols
 * 
 * Ces tests vérifient que la règle détecte correctement les symboles monétaires
 * dans les strings, commentaires et JSX.
 * 
 * Exécution : node eslint-rules/__tests__/no-monetary-symbols.test.js
 */
const { RuleTester } = require('eslint');
const noMonetarySymbols = require('../no-monetary-symbols.cjs');

// Configurer RuleTester pour React/JSX
const ruleTester = new RuleTester({
  parserOptions: {
    ecmaVersion: 2021,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  env: {
    browser: true,
    es2021: true,
  },
});

console.log('🧪 Tests de la règle ESLint: egoejo/no-monetary-symbols\n');

// Tests : Détection dans les strings littérales
console.log('✓ Test 1: Détection de € dans une string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const price = "100 €";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: '€' },
        },
      ],
    },
  ],
});

console.log('✓ Test 2: Détection de $ dans une string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const amount = "50 $";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: '$' },
        },
      ],
    },
  ],
});

console.log('✓ Test 3: Détection de USD dans une string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const value = "100 USD";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'USD' },
        },
      ],
    },
  ],
});

console.log('✓ Test 4: Détection de EUR dans une string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const balance = "200 EUR";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'EUR' },
        },
      ],
    },
  ],
});

console.log('✓ Test 5: Détection de GBP dans une string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const cost = "75 GBP";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'GBP' },
        },
      ],
    },
  ],
});

console.log('✓ Test 6: Détection de CHF dans une string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const price = "120 CHF";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'CHF' },
        },
      ],
    },
  ],
});

console.log('✓ Test 7: Pas de violation si aucun symbole monétaire');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [
    'const text = "Hello world";',
    'const amount = "100 grains";',
    'const saka = "500 SAKA";',
  ],
  invalid: [],
});

// Tests : Détection dans les template literals
console.log('✓ Test 8: Détection de € dans un template literal');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const message = `Prix: ${price} €`;',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: '€' },
        },
      ],
    },
  ],
});

console.log('✓ Test 9: Détection de USD dans un template literal');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const display = `Value: ${amount} USD`;',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'USD' },
        },
      ],
    },
  ],
});

console.log('✓ Test 10: Pas de violation dans template literal sans symbole');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [
    'const text = `Balance: ${balance} grains`;',
    'const saka = `SAKA: ${amount}`;',
  ],
  invalid: [],
});

// Tests : Détection dans les commentaires
console.log('✓ Test 11: Détection de € dans un commentaire ligne');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: '// Prix: 100 €',
      errors: [
        {
          messageId: 'monetarySymbolInComment',
          data: { symbol: '€' },
        },
      ],
    },
  ],
});

console.log('✓ Test 12: Détection de $ dans un commentaire bloc');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: '/* Amount: 50 $ */',
      errors: [
        {
          messageId: 'monetarySymbolInComment',
          data: { symbol: '$' },
        },
      ],
    },
  ],
});

console.log('✓ Test 13: Détection de EUR dans un commentaire');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: '// Balance: 200 EUR',
      errors: [
        {
          messageId: 'monetarySymbolInComment',
          data: { symbol: 'EUR' },
        },
      ],
    },
  ],
});

console.log('✓ Test 14: Pas de violation dans commentaire sans symbole');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [
    '// Balance: 100 grains',
    '/* SAKA: 500 */',
  ],
  invalid: [],
});

// Tests : Détection dans le JSX
console.log('✓ Test 15: Détection de € dans du JSX Text');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const Component = () => <div>Prix: 100 €</div>;',
      errors: [
        {
          messageId: 'monetarySymbolInJSX',
          data: { symbol: '€' },
        },
      ],
    },
  ],
});

console.log('✓ Test 16: Détection de $ dans un attribut JSX');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const Component = () => <div title="Amount: 50 $">Text</div>;',
      errors: [
        {
          messageId: 'monetarySymbolInJSX',
          data: { symbol: '$' },
        },
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: '$' },
        },
      ],
    },
  ],
});

console.log('✓ Test 17: Pas de violation dans JSX sans symbole');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [
    'const Component = () => <div>Balance: 100 grains</div>;',
    'const Component = () => <div title="SAKA: 500">Text</div>;',
  ],
  invalid: [],
});

// Tests : Cas limites
console.log('✓ Test 18: Détection de plusieurs symboles dans une même string');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const text = "100 € ou 120 USD";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: '€' },
        },
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'USD' },
        },
      ],
    },
  ],
});

console.log('✓ Test 19: Détection insensible à la casse (eur)');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const text = "100 eur";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'eur' },
        },
      ],
    },
  ],
});

console.log('✓ Test 20: Détection insensible à la casse (usd)');
ruleTester.run('no-monetary-symbols', noMonetarySymbols, {
  valid: [],
  invalid: [
    {
      code: 'const text = "100 usd";',
      errors: [
        {
          messageId: 'monetarySymbolInString',
          data: { symbol: 'usd' },
        },
      ],
    },
  ],
});

console.log('\n✅ Tous les tests sont passés !');
console.log('La règle ESLint egoejo/no-monetary-symbols fonctionne correctement.\n');
