/**
 * Configuration ESLint pour forcer TypeScript sur nouveaux fichiers
 */
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
  plugins: ['react', 'react-hooks'],
  rules: {
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
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  // Ignorer les fichiers existants .jsx (migration progressive)
  ignorePatterns: [
    'node_modules/',
    'dist/',
    'build/',
    '**/*.config.js',
    '**/*.config.cjs',
    'src/**/*.jsx', // Ignorer temporairement les .jsx existants
  ],
};
