/**
 * Plugin ESLint custom EGOEJO
 * 
 * Contient les règles de conformité EGOEJO COMPLIANT.
 */
const noMonetarySymbols = require('./no-monetary-symbols.cjs');

module.exports = {
  rules: {
    'no-monetary-symbols': noMonetarySymbols,
  },
};

