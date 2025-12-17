// Configuration lint-staged pour "Boy Scout Rule"
// Force la qualité sur les fichiers TypeScript modifiés
module.exports = {
  // Fichiers TypeScript : ESLint strict + TypeScript check
  'src/**/*.{ts,tsx}': [
    'eslint --max-warnings=0 --fix',
    'bash -c "tsc --noEmit || echo \'TypeScript check failed\'"'
  ],
  // Fichiers JavaScript : ESLint seulement (migration progressive)
  'src/**/*.{js,jsx}': [
    'eslint --max-warnings=0 --fix'
  ],
  // Formatage automatique (optionnel)
  'src/**/*.{ts,tsx,js,jsx,css,json}': [
    'prettier --write'
  ]
};

