/**
 * ESLint Rule : no-monetary-symbols
 * 
 * RÈGLE EGOEJO : Interdit les symboles monétaires (€, $, USD, EUR, GBP, CHF) dans le code.
 * 
 * Cette règle protège la philosophie EGOEJO en empêchant l'affichage monétaire du SAKA.
 * 
 * Violation du Label EGOEJO COMPLIANT si :
 * - Un symbole monétaire est utilisé dans une string
 * - Un symbole monétaire est utilisé dans un commentaire
 * - Un symbole monétaire est utilisé dans du JSX
 * 
 * @see docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md
 * @see docs/security/ACTIONS_DEFENSE_HOSTILE.md
 */

const MONETARY_SYMBOLS = [
  '€',           // Euro
  '$',           // Dollar
  'USD',         // United States Dollar
  'EUR',         // Euro (code ISO)
  'GBP',         // British Pound
  'CHF',         // Swiss Franc
  'JPY',         // Japanese Yen
  'CAD',         // Canadian Dollar
  'AUD',         // Australian Dollar
];

// Pattern regex pour détecter les symboles monétaires
const MONETARY_PATTERN = new RegExp(
  `(${MONETARY_SYMBOLS.map(s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`,
  'gi'
);

module.exports = {
  meta: {
    type: 'problem',
    docs: {
      description: 'Interdit les symboles monétaires dans les strings, commentaires et JSX (Label EGOEJO COMPLIANT)',
      category: 'EGOEJO Compliance',
      recommended: true,
      url: 'https://github.com/egoejo/egoejo/blob/main/docs/egoejo_compliance/LABEL_EGOEJO_COMPLIANT.md',
    },
    messages: {
      monetarySymbolInString: 'VIOLATION DU LABEL EGOEJO COMPLIANT : Symbole monétaire "{{symbol}}" détecté dans une string. Le SAKA ne doit jamais être affiché avec un symbole monétaire (€, $, USD, EUR, GBP, CHF). Utilisez formatSakaAmount() pour formater en "grains".',
      monetarySymbolInComment: 'VIOLATION DU LABEL EGOEJO COMPLIANT : Symbole monétaire "{{symbol}}" détecté dans un commentaire. Les commentaires ne doivent pas suggérer une valeur monétaire pour le SAKA.',
      monetarySymbolInJSX: 'VIOLATION DU LABEL EGOEJO COMPLIANT : Symbole monétaire "{{symbol}}" détecté dans du JSX. Le SAKA ne doit jamais être affiché avec un symbole monétaire. Utilisez formatSakaAmount() pour formater en "grains".',
    },
    schema: [],
  },
  create(context) {
    /**
     * Vérifie si une chaîne contient un symbole monétaire
     */
    function checkStringForMonetarySymbol(node, value, messageId) {
      if (typeof value !== 'string') {
        return;
      }

      const match = value.match(MONETARY_PATTERN);
      if (match) {
        // Éviter les doublons (plusieurs occurrences du même symbole)
        const uniqueSymbols = [...new Set(match)];
        
        uniqueSymbols.forEach(symbol => {
          context.report({
            node,
            messageId,
            data: {
              symbol: symbol,
            },
          });
        });
      }
    }

    /**
     * Vérifie les commentaires
     */
    function checkComments(comments) {
      comments.forEach(comment => {
        if (comment.type === 'Line' || comment.type === 'Block') {
          checkStringForMonetarySymbol(
            comment,
            comment.value,
            'monetarySymbolInComment'
          );
        }
      });
    }

    return {
      // Vérifier les strings littérales
      Literal(node) {
        if (typeof node.value === 'string') {
          checkStringForMonetarySymbol(
            node,
            node.value,
            'monetarySymbolInString'
          );
        }
      },

      // Vérifier les template literals
      TemplateLiteral(node) {
        // Vérifier les quasis (parties statiques)
        node.quasis.forEach(quasi => {
          checkStringForMonetarySymbol(
            quasi,
            quasi.value.raw,
            'monetarySymbolInString'
          );
        });
      },

      // Vérifier les JSX Text
      JSXText(node) {
        checkStringForMonetarySymbol(
          node,
          node.value,
          'monetarySymbolInJSX'
        );
      },

      // Vérifier les JSX Attribute values
      JSXAttribute(node) {
        if (node.value) {
          if (node.value.type === 'Literal' && typeof node.value.value === 'string') {
            checkStringForMonetarySymbol(
              node.value,
              node.value.value,
              'monetarySymbolInJSX'
            );
          } else if (node.value.type === 'JSXExpressionContainer') {
            // Pour les expressions JSX, on vérifie les strings littérales à l'intérieur
            const expression = node.value.expression;
            if (expression && expression.type === 'Literal' && typeof expression.value === 'string') {
              checkStringForMonetarySymbol(
                expression,
                expression.value,
                'monetarySymbolInJSX'
              );
            }
          }
        }
      },

      // Vérifier tous les commentaires du fichier
      Program(node) {
        const sourceCode = context.getSourceCode();
        const comments = sourceCode.getAllComments();
        checkComments(comments);
      },
    };
  },
};

