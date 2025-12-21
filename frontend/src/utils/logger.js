/**
 * Système de logging professionnel pour EGOEJO
 * OPTIMISATION PERFORMANCE : Ne logue que si import.meta.env.DEV est true
 * Remplace tous les console.log par un système avec niveaux
 */

const LOG_LEVELS = {
  DEBUG: 0,
  INFO: 1,
  WARN: 2,
  ERROR: 3,
};

// OPTIMISATION PERFORMANCE : Ne logue que en développement
const IS_DEV = import.meta.env.DEV;

class Logger {
  constructor() {
    this.level = import.meta.env.PROD ? LOG_LEVELS.INFO : LOG_LEVELS.DEBUG;
    this.enableSentry = import.meta.env.PROD && typeof window !== 'undefined' && window.Sentry;
  }

  /**
   * Log un message de debug (seulement en développement)
   */
  debug(...args) {
    // OPTIMISATION PERFORMANCE : Ne logue que si DEV est true
    if (!IS_DEV) return;
    if (this.level <= LOG_LEVELS.DEBUG) {
      console.debug('[DEBUG]', ...args);
    }
  }

  /**
   * Log un message d'information
   */
  info(...args) {
    // OPTIMISATION PERFORMANCE : Ne logue que si DEV est true
    if (!IS_DEV) return;
    if (this.level <= LOG_LEVELS.INFO) {
      console.info('[INFO]', ...args);
    }
  }

  /**
   * Log un avertissement
   */
  warn(...args) {
    // OPTIMISATION PERFORMANCE : Ne logue que si DEV est true
    if (!IS_DEV) return;
    if (this.level <= LOG_LEVELS.WARN) {
      console.warn('[WARN]', ...args);
    }
  }

  /**
   * Log une erreur et l'envoie à Sentry en production
   * NOTE : Les erreurs sont toujours envoyées à Sentry en production, même si les logs sont désactivés
   */
  error(...args) {
    // OPTIMISATION PERFORMANCE : Ne logue que si DEV est true
    if (IS_DEV && this.level <= LOG_LEVELS.ERROR) {
      console.error('[ERROR]', ...args);
    }
    
    // En production, envoyer à Sentry si disponible (même si les logs sont désactivés)
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
        if (IS_DEV) {
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

