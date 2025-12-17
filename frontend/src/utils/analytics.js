/**
 * Système d'analytics pour EGOEJO
 * Permet de tracker les événements utilisateur de manière centralisée
 */

/**
 * Track un événement utilisateur
 * @param {string} eventName - Nom de l'événement
 * @param {Object} properties - Propriétés de l'événement
 */
export const trackEvent = (eventName, properties = {}) => {
  // En production, envoyer à votre service d'analytics
  if (import.meta.env.PROD) {
    // Exemple avec Google Analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', eventName, properties);
    }
    
    // Envoyer aussi à votre propre endpoint si disponible
    const apiBase = import.meta.env.VITE_API_URL 
      ? `${import.meta.env.VITE_API_URL}/api` 
      : 'http://localhost:8000/api';
    
    fetch(`${apiBase}/analytics/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        event: eventName, 
        properties,
        timestamp: new Date().toISOString(),
        url: window.location.href,
        userAgent: navigator.userAgent,
      }),
    }).catch(() => {
      // Ignorer les erreurs silencieusement pour ne pas perturber l'UX
    });
  } else {
    // En développement, logger l'événement
    if (typeof window !== 'undefined') {
      console.log('[Analytics]', eventName, properties);
    }
  }
};

/**
 * Track une page view
 * @param {string} page - Nom de la page
 * @param {Object} additionalData - Données supplémentaires
 */
export const trackPageView = (page, additionalData = {}) => {
  trackEvent('page_view', {
    page,
    ...additionalData,
  });
};

/**
 * Track un clic sur un bouton
 * @param {string} buttonName - Nom du bouton
 * @param {Object} additionalData - Données supplémentaires
 */
export const trackButtonClick = (buttonName, additionalData = {}) => {
  trackEvent('button_click', {
    button: buttonName,
    ...additionalData,
  });
};

/**
 * Track une action de formulaire
 * @param {string} formName - Nom du formulaire
 * @param {string} action - Action (submit, cancel, etc.)
 * @param {Object} additionalData - Données supplémentaires
 */
export const trackFormAction = (formName, action, additionalData = {}) => {
  trackEvent('form_action', {
    form: formName,
    action,
    ...additionalData,
  });
};

/**
 * Track une erreur
 * @param {string} errorType - Type d'erreur
 * @param {string} errorMessage - Message d'erreur
 * @param {Object} additionalData - Données supplémentaires
 */
export const trackError = (errorType, errorMessage, additionalData = {}) => {
  trackEvent('error', {
    error_type: errorType,
    error_message: errorMessage,
    ...additionalData,
  });
};

/**
 * Track une conversion (ex: soumission de formulaire, don, etc.)
 * @param {string} conversionType - Type de conversion
 * @param {number} value - Valeur de la conversion (optionnel)
 * @param {Object} additionalData - Données supplémentaires
 */
export const trackConversion = (conversionType, value = null, additionalData = {}) => {
  trackEvent('conversion', {
    conversion_type: conversionType,
    value,
    ...additionalData,
  });
};

