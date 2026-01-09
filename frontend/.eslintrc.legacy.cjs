/**
 * Configuration ESLint pour forcer TypeScript sur nouveaux fichiers
 * 
 * VERSION LEGACY : Utilise la syntaxe objet pour les plugins locaux
 * (compatible ESLint 8.x mais peut causer des problèmes de sérialisation)
 */
const path = require('path');

// Charger le plugin custom EGOEJO via un loader pour éviter les problèmes de sérialisation
const egoejoPlugin = require('./eslint-rules/plugin-loader.cjs');

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
  // Plugin custom EGOEJO : utiliser un objet avec le plugin chargé directement
  // Note: ESLint 8.x accepte les objets pour les plugins locaux (syntaxe legacy)
  // IMPORTANT: La syntaxe objet est correcte pour les plugins locaux dans ESLint 8.x
  plugins: {
    egoejo: egoejoPlugin,
  },
  rules: {
    // RÈGLE EGOEJO CUSTOM : Interdire les symboles monétaires
    'egoejo/no-monetary-symbols': 'error',
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

