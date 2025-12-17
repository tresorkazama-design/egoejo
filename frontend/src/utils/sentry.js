/**
 * Configuration Sentry pour le monitoring d'erreurs
 * 
 * Pour activer Sentry :
 * 1. Installer @sentry/react : npm install @sentry/react
 * 2. Créer un compte sur https://sentry.io
 * 3. Créer un projet et obtenir le DSN
 * 4. Ajouter VITE_SENTRY_DSN dans .env
 * 5. Importer et initialiser dans main.jsx
 */

/**
 * Initialise Sentry si le DSN est configuré
 */
export const initSentry = () => {
  // Désactiver complètement Sentry en développement
  // Vite analyse les imports dynamiques même en dev, donc on doit éviter l'import
  if (import.meta.env.DEV || import.meta.env.MODE === 'development') {
    return;
  }
  
  const dsn = import.meta.env.VITE_SENTRY_DSN;
  
  // Sentry désactivé si DSN non configuré
  if (!dsn) {
    return;
  }
  
  // Utiliser une fonction async pour éviter l'analyse statique de Vite
  // et charger Sentry uniquement en production
  (async () => {
    try {
      // Lazy load Sentry seulement en production
      // Utiliser une variable pour éviter l'analyse statique
      const sentryModule = '@sentry/react';
      const Sentry = await import(/* @vite-ignore */ sentryModule);
      
      Sentry.init({
        dsn,
        environment: import.meta.env.MODE,
        integrations: [
          Sentry.browserTracingIntegration(),
          Sentry.replayIntegration({
            maskAllText: true,
            blockAllMedia: true,
          }),
        ],
        tracesSampleRate: 0.1, // 10% des transactions
        replaysSessionSampleRate: 0.1, // 10% des sessions
        replaysOnErrorSampleRate: 1.0, // 100% des sessions avec erreurs
        beforeSend(event, hint) {
          // Filtrer les erreurs sensibles
          if (event.exception) {
            const error = hint.originalException;
            if (error && error.message && error.message.includes('token')) {
              // Ne pas envoyer les erreurs liées aux tokens
              return null;
            }
          }
          return event;
        },
      });
    } catch (error) {
      // Ignorer silencieusement les erreurs de chargement de Sentry
      // pour ne pas polluer la console en développement
      if (import.meta.env.PROD) {
        console.error('Erreur lors du chargement de Sentry:', error);
      }
    }
  })();
};

