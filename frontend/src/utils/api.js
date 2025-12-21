// Utilitaires API
import { addSecurityHeaders, isTokenValid, getTokenSecurely } from './security.js';
import { logger } from './logger';

export const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : 'http://localhost:8000/api';

// OPTIMISATION RÉSEAU : Retry avec Backoff Exponentiel pour les erreurs réseau ou 5xx
const MAX_RETRY_ATTEMPTS = 3;
const INITIAL_RETRY_DELAY = 1000; // 1 seconde

/**
 * Fonction de retry avec backoff exponentiel
 * @param {Function} fn - Fonction à exécuter
 * @param {number} retries - Nombre de tentatives restantes
 * @param {number} delay - Délai initial en ms
 * @returns {Promise}
 */
const retryWithBackoff = async (fn, retries = MAX_RETRY_ATTEMPTS, delay = INITIAL_RETRY_DELAY) => {
  try {
    return await fn();
  } catch (error) {
    // Ne retry que pour les erreurs réseau ou 5xx
    const isNetworkError = error.message === 'Failed to fetch' || error.name === 'TypeError';
    const isServerError = error.status >= 500 && error.status < 600;
    
    if ((isNetworkError || isServerError) && retries > 0) {
      const nextDelay = delay * Math.pow(2, MAX_RETRY_ATTEMPTS - retries); // Backoff exponentiel
      logger.warn(`Tentative de retry (${MAX_RETRY_ATTEMPTS - retries + 1}/${MAX_RETRY_ATTEMPTS}) dans ${nextDelay}ms...`);
      
      await new Promise(resolve => setTimeout(resolve, nextDelay));
      return retryWithBackoff(fn, retries - 1, delay);
    }
    throw error;
  }
};

/**
 * Fonction centrale pour les appels API avec gestion automatique de l'authentification et retry
 * @param {string} endpoint - Endpoint API (ex: '/auth/me/')
 * @param {object} options - Options fetch (method, body, headers, etc.)
 * @returns {Promise}
 */
export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  
  // OPTIMISATION RÉSEAU : Gérer automatiquement les headers Auth
  const token = getTokenSecurely();
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Ajouter le token d'authentification si disponible
  if (token && isTokenValid(token)) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Utiliser les headers de sécurité
  const securityHeaders = addSecurityHeaders(headers);
  
  const config = {
    headers: securityHeaders,
    ...options,
  };

  // OPTIMISATION RÉSEAU : Retry avec backoff exponentiel pour les erreurs réseau ou 5xx
  return retryWithBackoff(async () => {
    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
        const apiError = new Error(error.detail || `Erreur ${response.status}`);
        apiError.status = response.status; // Ajouter le status pour le retry
        throw apiError;
      }

      return response.json();
    } catch (error) {
      // Améliorer les messages d'erreur pour "failed to fetch"
      if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
        const networkError = new Error(
          `Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur ${API_BASE.replace('/api', '')}`
        );
        networkError.status = 0; // Status 0 pour erreur réseau
        throw networkError;
      }
      throw error;
    }
  });
};

/**
 * Mappe les erreurs techniques vers des messages humains et compréhensibles
 * @param {Error|string} error - Erreur à mapper
 * @returns {string} Message d'erreur humain
 */
export const handleAPIError = (error) => {
  // Si c'est déjà une string, vérifier si c'est un message humain
  if (typeof error === 'string') {
    // Si le message contient déjà des termes techniques, le mapper
    if (error.includes('401') || error.includes('Unauthorized')) {
      return 'Votre session a expiré. Veuillez vous reconnecter.';
    }
    if (error.includes('403') || error.includes('Forbidden')) {
      return 'Vous n\'avez pas les permissions nécessaires pour cette action.';
    }
    if (error.includes('insuffisant') || error.includes('Solde') || error.includes('SAKA')) {
      return error; // Garder les messages SAKA tels quels (déjà humains)
    }
    if (error.includes('Failed to fetch') || error.includes('NetworkError')) {
      return 'Problème de connexion. Vérifiez votre réseau et réessayez.';
    }
    return error;
  }

  // Si c'est un objet Error
  if (error instanceof Error) {
    const message = error.message;
    const status = error.status || error.code;

    // Mapping par status code
    if (status === 401 || message.includes('401') || message.includes('Unauthorized')) {
      return 'Votre session a expiré. Veuillez vous reconnecter.';
    }
    if (status === 403 || message.includes('403') || message.includes('Forbidden')) {
      return 'Vous n\'avez pas les permissions nécessaires pour cette action.';
    }
    if (status === 404 || message.includes('404') || message.includes('Not Found')) {
      return 'La ressource demandée n\'existe pas ou a été supprimée.';
    }
    if (status === 429 || message.includes('429') || message.includes('Too Many Requests')) {
      return 'Trop de requêtes. Veuillez patienter quelques instants avant de réessayer.';
    }
    if (status >= 500 || message.includes('500') || message.includes('Internal Server Error')) {
      return 'Une erreur serveur est survenue. Notre équipe a été notifiée. Veuillez réessayer plus tard.';
    }
    if (status === 0 || message.includes('Failed to fetch') || message.includes('NetworkError')) {
      return 'Problème de connexion. Vérifiez votre réseau et réessayez.';
    }

    // Messages spécifiques SAKA
    if (message.includes('insuffisant') || message.includes('Solde SAKA')) {
      return message; // Garder les messages SAKA tels quels
    }

    // Messages spécifiques avec suggestions
    if (message.includes('insuffisant') && message.includes('SAKA')) {
      return 'Il vous manque des SAKA. Lisez un contenu pour en gagner !';
    }

    // Par défaut, retourner le message original
    return message || 'Une erreur est survenue. Veuillez réessayer.';
  }

  return 'Une erreur est survenue. Veuillez réessayer.';
};

