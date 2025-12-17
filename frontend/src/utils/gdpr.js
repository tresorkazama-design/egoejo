/**
 * Utilitaires pour la conformité GDPR/RGPD
 */

const CONSENT_KEY = 'gdpr_consent';
const CONSENT_VERSION = '1.0';

/**
 * Types de consentement
 */
export const ConsentType = {
  NECESSARY: 'necessary',
  ANALYTICS: 'analytics',
  MARKETING: 'marketing',
  FUNCTIONAL: 'functional',
};

/**
 * Vérifie si l'utilisateur a donné son consentement
 */
export const hasConsent = (type = ConsentType.NECESSARY) => {
  try {
    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) {
      return false;
    }
    
    const consentData = JSON.parse(consent);
    
    // Vérifier la version
    if (consentData.version !== CONSENT_VERSION) {
      return false;
    }
    
    // Le consentement nécessaire est toujours vrai
    if (type === ConsentType.NECESSARY) {
      return true;
    }
    
    return consentData.types?.includes(type) || false;
  } catch (e) {
    return false;
  }
};

/**
 * Enregistre le consentement de l'utilisateur
 */
export const setConsent = (types, metadata = {}) => {
  try {
    const consentData = {
      version: CONSENT_VERSION,
      types: [ConsentType.NECESSARY, ...types], // Toujours inclure nécessaire
      timestamp: new Date().toISOString(),
      ...metadata,
    };
    
    localStorage.setItem(CONSENT_KEY, JSON.stringify(consentData));
    
    // Déclencher un événement personnalisé
    window.dispatchEvent(new CustomEvent('gdpr-consent-updated', {
      detail: consentData,
    }));
  } catch (e) {
    console.error('Erreur lors de l\'enregistrement du consentement:', e);
  }
};

/**
 * Récupère les données de consentement
 */
export const getConsent = () => {
  try {
    const consent = localStorage.getItem(CONSENT_KEY);
    if (!consent) {
      return null;
    }
    return JSON.parse(consent);
  } catch (e) {
    return null;
  }
};

/**
 * Supprime le consentement (droit à l'oubli)
 */
export const revokeConsent = () => {
  try {
    localStorage.removeItem(CONSENT_KEY);
    
    // Supprimer aussi les données d'analytics si présentes
    if (hasConsent(ConsentType.ANALYTICS)) {
      // Supprimer les cookies d'analytics
      document.cookie.split(';').forEach(cookie => {
        const name = cookie.split('=')[0].trim();
        if (name.includes('_ga') || name.includes('_gid')) {
          document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
        }
      });
    }
    
    window.dispatchEvent(new CustomEvent('gdpr-consent-revoked'));
  } catch (e) {
    console.error('Erreur lors de la révocation du consentement:', e);
  }
};

/**
 * Anonymise une adresse email
 */
export const anonymizeEmail = (email) => {
  if (!email || !email.includes('@')) {
    return '***@***';
  }
  
  const [local, domain] = email.split('@');
  const maskedLocal = local.length > 2 
    ? `${local[0]}***${local[local.length - 1]}`
    : '***';
  
  return `${maskedLocal}@${domain}`;
};

/**
 * Anonymise un numéro de téléphone
 */
export const anonymizePhone = (phone) => {
  if (!phone) {
    return '***';
  }
  
  const digits = phone.replace(/\D/g, '');
  if (digits.length < 4) {
    return '***';
  }
  
  return `***${digits.slice(-4)}`;
};

/**
 * Exporte les données utilisateur (droit à la portabilité)
 */
export const exportUserData = async () => {
  try {
    // Récupérer les données depuis l'API
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (!token) {
      throw new Error('Non authentifié');
    }
    
    const API_BASE = import.meta.env.VITE_API_URL 
      ? `${import.meta.env.VITE_API_URL}/api` 
      : 'http://localhost:8000/api';
    
    const response = await fetch(`${API_BASE}/user/data-export/`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de l\'export');
    }
    
    const data = await response.json();
    
    // Créer un fichier JSON téléchargeable
    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `egoejo-data-export-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    return data;
  } catch (e) {
    console.error('Erreur lors de l\'export des données:', e);
    throw e;
  }
};

/**
 * Supprime les données utilisateur (droit à l'oubli)
 */
export const deleteUserData = async () => {
  try {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token');
    if (!token) {
      throw new Error('Non authentifié');
    }
    
    const API_BASE = import.meta.env.VITE_API_URL 
      ? `${import.meta.env.VITE_API_URL}/api` 
      : 'http://localhost:8000/api';
    
    const response = await fetch(`${API_BASE}/user/data-delete/`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });
    
    if (!response.ok) {
      throw new Error('Erreur lors de la suppression');
    }
    
    // Nettoyer les données locales
    localStorage.clear();
    sessionStorage.clear();
    
    return true;
  } catch (e) {
    console.error('Erreur lors de la suppression des données:', e);
    throw e;
  }
};

