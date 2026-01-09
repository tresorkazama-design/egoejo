/**
 * Utilitaires pour la gestion précise des montants financiers
 * Utilise Decimal.js pour éviter les erreurs de précision des float
 * 
 * NOTE: Ce fichier gère l'argent réel (EUR), pas le SAKA.
 * Les symboles monétaires (€, EUR) sont autorisés ici car ils concernent l'argent réel.
 */
import { Decimal } from 'decimal.js';

/**
 * Formate un montant en string (Decimal) vers un format monétaire français
 * @param {string|Decimal} value - Montant en string (ex: "1234.56") ou Decimal
 * @param {string} currency - Code devise (défaut: 'EUR')
 * @returns {string} - Montant formaté (ex: "1 234,56 €")
 * 
 * NOTE: Cette fonction est pour l'argent réel (EUR), pas pour SAKA.
 * Pour SAKA, utiliser formatSaka() de utils/saka.ts
 */
export const formatMoney = (value, currency = 'EUR') => {
  // eslint-disable-next-line egoejo/no-monetary-symbols
  // NOTE: Symbole monétaire autorisé ici car formatMoney gère l'argent réel (EUR), pas SAKA
  if (!value) return '0,00 €';
  
  let decimal;
  try {
    decimal = value instanceof Decimal ? value : new Decimal(String(value));
  } catch (e) {
    console.error('Erreur formatMoney:', e);
    // eslint-disable-next-line egoejo/no-monetary-symbols
    // NOTE: Symbole monétaire autorisé ici car formatMoney gère l'argent réel (EUR), pas SAKA
    return '0,00 €';
  }
  
  // Formater avec séparateurs français
  const formatted = decimal.toFixed(2).replace('.', ',');
  const parts = formatted.split(',');
  const integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  
  // eslint-disable-next-line egoejo/no-monetary-symbols
  // NOTE: Les symboles monétaires sont autorisés ici car formatMoney gère l'argent réel (EUR), pas SAKA
  return `${integerPart},${parts[1]} ${currency === 'EUR' ? '€' : currency}`;
};

/**
 * Convertit un string Decimal en nombre pour les calculs (si nécessaire)
 * ATTENTION: Utiliser Decimal.js pour tous les calculs, pas cette fonction
 * @param {string|Decimal} value - Montant en string ou Decimal
 * @returns {Decimal} - Instance Decimal
 */
export const toDecimal = (value) => {
  if (value instanceof Decimal) return value;
  if (typeof value === 'string') return new Decimal(value);
  if (typeof value === 'number') return new Decimal(value);
  return new Decimal('0');
};

/**
 * Additionne deux montants avec précision
 * @param {string|Decimal} a - Premier montant
 * @param {string|Decimal} b - Deuxième montant
 * @returns {Decimal} - Somme en Decimal
 */
export const addMoney = (a, b) => {
  return toDecimal(a).plus(toDecimal(b));
};

/**
 * Soustrait deux montants avec précision
 * @param {string|Decimal} a - Premier montant
 * @param {string|Decimal} b - Deuxième montant
 * @returns {Decimal} - Différence en Decimal
 */
export const subtractMoney = (a, b) => {
  return toDecimal(a).minus(toDecimal(b));
};

/**
 * Multiplie deux montants avec précision
 * @param {string|Decimal} a - Premier montant
 * @param {string|Decimal} b - Deuxième montant
 * @returns {Decimal} - Produit en Decimal
 */
export const multiplyMoney = (a, b) => {
  return toDecimal(a).times(toDecimal(b));
};

