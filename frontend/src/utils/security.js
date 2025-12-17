/**
 * Utilitaires de sécurité pour le frontend
 */

/**
 * Sanitize une chaîne pour prévenir XSS
 */
export const sanitizeString = (str) => {
  if (typeof str !== 'string') {
    return str;
  }
  
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
};

/**
 * Valide et nettoie un email
 */
export const sanitizeEmail = (email) => {
  if (!email) {
    return null;
  }
  
  const trimmed = email.trim().toLowerCase();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  
  if (!emailRegex.test(trimmed)) {
    throw new Error('Format d\'email invalide');
  }
  
  return trimmed;
};

/**
 * Valide et nettoie une URL
 */
export const sanitizeURL = (url) => {
  if (!url) {
    return null;
  }
  
  try {
    const parsed = new URL(url);
    // Vérifier que c'est HTTP ou HTTPS
    if (!['http:', 'https:'].includes(parsed.protocol)) {
      throw new Error('Seules les URLs HTTP/HTTPS sont autorisées');
    }
    return parsed.href;
  } catch (e) {
    throw new Error('URL invalide');
  }
};

/**
 * Masque les données sensibles dans les logs
 */
export const maskSensitiveData = (data) => {
  if (typeof data !== 'object' || data === null) {
    return data;
  }
  
  const sensitiveFields = ['password', 'token', 'secret', 'apiKey', 'api_key', 'authorization'];
  const masked = { ...data };
  
  for (const key in masked) {
    const keyLower = key.toLowerCase();
    if (sensitiveFields.some(field => keyLower.includes(field))) {
      masked[key] = '***MASKED***';
    } else if (typeof masked[key] === 'object') {
      masked[key] = maskSensitiveData(masked[key]);
    }
  }
  
  return masked;
};

/**
 * Stocke un token de manière sécurisée
 */
export const storeTokenSecurely = (token) => {
  try {
    // Utiliser sessionStorage pour les tokens (plus sécurisé que localStorage)
    // Les tokens sont automatiquement supprimés à la fermeture du navigateur
    sessionStorage.setItem('token', token);
    
    // Optionnel: stocker aussi dans localStorage avec expiration
    const expiresAt = Date.now() + (60 * 60 * 1000); // 1 heure
    localStorage.setItem('token_expires', expiresAt.toString());
  } catch (e) {
    console.error('Erreur lors du stockage du token:', e);
  }
};

/**
 * Récupère un token de manière sécurisée
 */
export const getTokenSecurely = () => {
  try {
    // Vérifier l'expiration si stocké dans localStorage
    const expiresAt = localStorage.getItem('token_expires');
    if (expiresAt && Date.now() > parseInt(expiresAt)) {
      // Token expiré, nettoyer
      clearTokens();
      return null;
    }
    
    return sessionStorage.getItem('token') || localStorage.getItem('token');
  } catch (e) {
    console.error('Erreur lors de la récupération du token:', e);
    return null;
  }
};

/**
 * Supprime tous les tokens
 */
export const clearTokens = () => {
  try {
    sessionStorage.removeItem('token');
    localStorage.removeItem('token');
    localStorage.removeItem('token_expires');
  } catch (e) {
    console.error('Erreur lors de la suppression des tokens:', e);
  }
};

/**
 * Vérifie si on est en HTTPS (production)
 */
export const isHTTPS = () => {
  return window.location.protocol === 'https:';
};

/**
 * Force HTTPS en production
 */
export const enforceHTTPS = () => {
  if (import.meta.env.PROD && !isHTTPS()) {
    window.location.replace(window.location.href.replace('http:', 'https:'));
  }
};

/**
 * Valide un token JWT (vérifie l'expiration)
 */
export const isTokenValid = (token) => {
  if (!token) {
    return false;
  }
  
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return false;
    }
    
    const payload = JSON.parse(atob(parts[1]));
    const now = Math.floor(Date.now() / 1000);
    
    // Vérifier l'expiration
    if (payload.exp && payload.exp < now) {
      return false;
    }
    
    return true;
  } catch (e) {
    return false;
  }
};

/**
 * Protection CSRF - récupère le token CSRF
 */
export const getCSRFToken = () => {
  const cookies = document.cookie.split(';');
  for (const cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return null;
};

/**
 * Ajoute les headers de sécurité à une requête
 */
export const addSecurityHeaders = (headers = {}) => {
  const token = getTokenSecurely();
  const csrfToken = getCSRFToken();
  
  const securityHeaders = {
    'Content-Type': 'application/json',
    ...headers,
  };
  
  if (token && isTokenValid(token)) {
    securityHeaders['Authorization'] = `Bearer ${token}`;
  }
  
  if (csrfToken) {
    securityHeaders['X-CSRFToken'] = csrfToken;
  }
  
  return securityHeaders;
};

