/**
 * Système de logging professionnel pour EGOEJO
 * Remplace tous les console.log par un système avec niveaux
 */

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

class Logger {
  constructor() {
    this.level = import.meta.env.PROD ? LOG_LEVELS.INFO : LOG_LEVELS.DEBUG;
    this.enableSentry = import.meta.env.PROD && typeof window !== 'undefined' && window.Sentry;
  }

  /**
   * Log un message de debug (seulement en développement)
   */
  debug(...args) {
    if (this.level <= LOG_LEVELS.DEBUG) {
      console.debug('[DEBUG]', ...args);
    }
  }

  /**
   * Log un message d'information
   */
  info(...args) {
    if (this.level <= LOG_LEVELS.INFO) {
      console.info('[INFO]', ...args);
    }
  }

  /**
   * Log un avertissement
   */
  warn(...args) {
    if (this.level <= LOG_LEVELS.WARN) {
      console.warn('[WARN]', ...args);
    }
  }

  /**
   * Log une erreur et l'envoie à Sentry en production
   */
  error(...args) {
    if (this.level <= LOG_LEVELS.ERROR) {
      console.error('[ERROR]', ...args);
      
      // En production, envoyer à Sentry si disponible
      if (this.enableSentry) {
        try {
          const errorMessage = args.map(arg => 
            typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
          ).join(' ');
          
          window.Sentry.captureException(new Error(errorMessage), {
            level: 'error',
            extra: args.length > 1 ? args.slice(1) : undefined,
          });
        } catch (sentryError) {
          // Ne pas bloquer si Sentry échoue
          console.error('Erreur lors de l\'envoi à Sentry:', sentryError);
        }
      }
    }
  }

  /**
   * Définir le niveau de log (pour les tests)
   */
  setLevel(level) {
    this.level = level;
  }
}

export const logger = new Logger();

