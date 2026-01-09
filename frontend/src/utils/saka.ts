/**
 * Utilitaires pour la gestion du SAKA (monnaie interne d'engagement)
 * 
 * PHILOSOPHIE EGOEJO :
 * RÈGLE ABSOLUE : Aucun affichage monétaire du SAKA (pas de formatMoney pour SAKA)
 * Le SAKA est une monnaie interne d'engagement (Yin), strictement séparée de l'Euro (Yang).
 */

// Type pour distinguer SAKA de EUR (protection TypeScript)
export type SakaAmount = number & { __brand: 'SAKA' };
export type EurAmount = number & { __brand: 'EUR' };

/**
 * Formate un montant SAKA (grains) - JAMAIS en format monétaire
 * 
 * RÈGLE ABSOLUE : Le SAKA ne doit jamais être affiché comme une monnaie.
 * 
 * @param amount - Montant SAKA (grains)
 * @returns String formatée (ex: "150 grains SAKA")
 */
export function formatSaka(amount: number): string {
  return `${amount} grains SAKA`;
}

/**
 * Protection : Empêche l'utilisation de formatMoney pour SAKA
 * 
 * Cette fonction ne devrait jamais être appelée en production.
 * Elle sert de garde-fou TypeScript pour empêcher l'utilisation accidentelle
 * de formatMoney avec SAKA.
 * 
 * @param amount - Montant SAKA (grains)
 * @throws Error si tentative d'utiliser formatMoney pour SAKA
 */
export function preventSakaMonetaryFormat(amount: SakaAmount): never {
  throw new Error(
    'VIOLATION CONSTITUTION EGOEJO : Le SAKA ne doit jamais être affiché comme une monnaie. ' +
    'Utilisez formatSaka() au lieu de formatMoney().'
  );
}

/**
 * Vérifie qu'un montant SAKA n'est pas formaté comme une monnaie
 * 
 * @param formatted - String formatée à vérifier
 * @returns True si le format est correct (pas de symbole monétaire)
 */
export function isSakaFormatValid(formatted: string): boolean {
  // Vérifier qu'il n'y a pas de symbole monétaire
  const hasMonetarySymbol = /€|EUR|euro/i.test(formatted);
  
  // Vérifier que c'est bien formaté comme "grains SAKA"
  const hasSakaFormat = /grains?\s+SAKA/i.test(formatted);
  
  return !hasMonetarySymbol && hasSakaFormat;
}

