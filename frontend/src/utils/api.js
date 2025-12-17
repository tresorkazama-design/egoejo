// Utilitaires API
import { addSecurityHeaders, isTokenValid, getTokenSecurely } from './security.js';

export const API_BASE = import.meta.env.VITE_API_URL 
  ? `${import.meta.env.VITE_API_URL}/api` 
  : 'http://localhost:8000/api';

export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  
  // Utiliser les headers de sécurité
  const securityHeaders = addSecurityHeaders(options.headers);
  
  const config = {
    headers: securityHeaders,
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
      throw new Error(error.detail || `Erreur ${response.status}`);
    }

    return response.json();
  } catch (error) {
    // Améliorer les messages d'erreur pour "failed to fetch"
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      throw new Error(
        `Impossible de se connecter au serveur. Vérifiez que le backend est démarré sur ${API_BASE.replace('/api', '')}`
      );
    }
    throw error;
  }
};

export const handleAPIError = (error) => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'Une erreur est survenue';
};

