/**
 * Configuration ESLint pour forcer TypeScript sur nouveaux fichiers
 */
const path = require('path');

module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true,
  },
  extends: [
    'eslint:recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  // Les plugins 'react' et 'react-hooks' sont chargés automatiquement via 'extends'
  // Note: Le plugin custom EGOEJO 'egoejo/no-monetary-symbols' est désactivé temporairement
  // car ESLint 8.x ne supporte pas les objets dans 'plugins' lors de la validation.
  // La vérification des symboles monétaires est effectuée via le script audit-home-vision.mjs
  plugins: [],
  rules: {
    // NOTE: Règle EGOEJO custom désactivée (problème de compatibilité ESLint 8.x)
    // La vérification des symboles monétaires est effectuée via audit-home-vision.mjs
    // 'egoejo/no-monetary-symbols': 'error',
    // Interdire les nouveaux fichiers .jsx (forcer .tsx)
    'no-restricted-imports': [
      'error',
      {
        patterns: [
          {
            group: ['**/*.jsx'],
            message: 'Les nouveaux fichiers doivent être en .tsx (TypeScript). Utilisez .tsx pour les nouvelles features.',
          },
        ],
      },
    ],
    // Avertir sur les fichiers .jsx existants
    'react/prop-types': 'warn',
    // RÈGLE EGOEJO : Détecter les symboles monétaires avec SAKA (règle documentée dans ACTIONS_DEFENSE_HOSTILE.md)
    // Note: ESLint ne peut pas scanner le contenu des strings directement, mais on peut détecter les patterns suspects
    'no-restricted-syntax': [
      'warn',
      {
        selector: 'TemplateLiteral[expressions.length>0]',
        message: 'Vérifiez que SAKA n\'est pas affiché avec un symbole monétaire (€, $, USD, EUR, GBP, CHF). Utilisez formatSakaAmount() pour formater en "grains".',
      },
    ],
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  // Ignorer uniquement les fichiers de configuration et build
  ignorePatterns: [
    'node_modules/',
    'dist/',
    'build/',
    '**/*.config.js',
    '**/*.config.cjs',
    // ❌ RETIRÉ : 'src/**/*.jsx' - Tous les fichiers JSX doivent être scannés pour la conformité EGOEJO
  ],
};
