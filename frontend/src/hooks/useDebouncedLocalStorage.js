/**
 * Hook personnalisé pour sauvegarder automatiquement dans localStorage avec debounce
 * 
 * Sauvegarde les valeurs dans localStorage avec un délai (debounce)
 * pour éviter les écritures excessives lors de changements rapides.
 * 
 * Usage : Appelé comme un effet, sauvegarde automatiquement quand key/value changent
 * 
 * @param {string|null} key - Clé du localStorage (null pour désactiver)
 * @param {any} value - Valeur à sauvegarder
 * @param {number} delay - Délai en millisecondes avant la sauvegarde (défaut: 300ms)
 */
import { useEffect, useRef } from 'react';

export const useDebouncedLocalStorage = (key, value, delay = 300) => {
  // Ref pour stocker le timeout du debounce
  const timeoutRef = useRef(null);
  // Ref pour stocker la valeur précédente (éviter les sauvegardes inutiles)
  const previousValueRef = useRef(value);

  useEffect(() => {
    // Si key est null, ne rien faire (désactivation)
    if (!key || typeof window === 'undefined') {
      return;
    }

    // Si la valeur n'a pas changé, ne rien faire
    if (previousValueRef.current === value) {
      return;
    }

    // Mettre à jour la référence
    previousValueRef.current = value;

    // Annuler le timeout précédent si existe
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Créer un nouveau timeout pour sauvegarder après le délai
    timeoutRef.current = setTimeout(() => {
      try {
        // Sauvegarder dans localStorage
        // Si value est null, supprimer la clé
        if (value === null || value === undefined) {
          window.localStorage.removeItem(key);
        } else {
          // Sauvegarder la valeur (stringify si nécessaire)
          const valueToStore = typeof value === 'string' ? value : JSON.stringify(value);
          window.localStorage.setItem(key, valueToStore);
        }
      } catch (error) {
        console.error(`Erreur écriture localStorage pour "${key}":`, error);
      }
    }, delay);

    // Nettoyer le timeout au démontage ou changement de dépendances
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [key, value, delay]);
};

