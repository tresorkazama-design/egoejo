/**
 * Configuration du monitoring pour détecter les problèmes rapidement
 * Intègre Sentry, métriques de performance, et alertes
 */

/**
 * Initialise le monitoring complet
 */
export const initMonitoring = () => {
  if (typeof window === 'undefined') {
    return;
  }

  // Initialiser Sentry (déjà fait dans main.jsx, mais on peut vérifier)
  initSentryIfNeeded();

  // Initialiser le tracking des métriques de performance
  initPerformanceMonitoring();

  // Initialiser le monitoring des erreurs JavaScript
  initErrorMonitoring();

  // Initialiser le monitoring des requêtes API
  initAPIMonitoring();

  // Initialiser les alertes
  initAlerts();
};

/**
 * Initialise Sentry si nécessaire
 */
const initSentryIfNeeded = () => {
  // Sentry est déjà initialisé dans main.jsx
  // On vérifie juste qu'il est bien chargé
  if (import.meta.env.PROD && import.meta.env.VITE_SENTRY_DSN) {
    // Sentry devrait être déjà initialisé
    console.log('[Monitoring] Sentry configuré');
  }
};

/**
 * Initialise le monitoring des métriques de performance
 */
const initPerformanceMonitoring = () => {
  if (!window.performance || !window.PerformanceObserver) {
    return;
  }

  // Mesurer les Core Web Vitals
  measureCoreWebVitals();

  // Mesurer les temps de chargement
  measureLoadTimes();

  // Détecter les composants lents
  detectSlowComponents();
};

/**
 * Mesure les Core Web Vitals (LCP, FID, CLS)
 */
const measureCoreWebVitals = () => {
  try {
    // Largest Contentful Paint (LCP)
    const lcpObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      const lastEntry = entries[entries.length - 1];
      const lcp = lastEntry.renderTime || lastEntry.loadTime;

      if (lcp) {
        sendMetric('LCP', lcp);
        // Alerte si LCP > 2.5s
        if (lcp > 2500) {
          sendAlert('performance', `LCP lent: ${lcp.toFixed(0)}ms (objectif: <2500ms)`);
        }
      }
    });
    lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });

    // First Input Delay (FID)
    const fidObserver = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach((entry) => {
        const fid = entry.processingStart - entry.startTime;
        sendMetric('FID', fid);
        // Alerte si FID > 100ms
        if (fid > 100) {
          sendAlert('performance', `FID lent: ${fid.toFixed(0)}ms (objectif: <100ms)`);
        }
      });
    });
    fidObserver.observe({ entryTypes: ['first-input'] });

    // Cumulative Layout Shift (CLS)
    let clsValue = 0;
    const clsObserver = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      }
      if (clsValue > 0) {
        sendMetric('CLS', clsValue);
        // Alerte si CLS > 0.1
        if (clsValue > 0.1) {
          sendAlert('performance', `CLS élevé: ${clsValue.toFixed(3)} (objectif: <0.1)`);
        }
      }
    });
    clsObserver.observe({ entryTypes: ['layout-shift'] });
  } catch (e) {
    console.warn('[Monitoring] Erreur lors de la mesure des Core Web Vitals:', e);
  }
};

/**
 * Mesure les temps de chargement
 */
const measureLoadTimes = () => {
  window.addEventListener('load', () => {
    if (window.performance && window.performance.timing) {
      const timing = window.performance.timing;
      const loadTime = timing.loadEventEnd - timing.navigationStart;
      const domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
      const firstByte = timing.responseStart - timing.navigationStart;

      sendMetric('PageLoad', loadTime);
      sendMetric('DOMContentLoaded', domContentLoaded);
      sendMetric('TTFB', firstByte);

      // Alertes si les temps sont trop longs
      if (loadTime > 3000) {
        sendAlert('performance', `Temps de chargement lent: ${loadTime}ms`);
      }
      if (firstByte > 600) {
        sendAlert('performance', `TTFB lent: ${firstByte}ms`);
      }
    }
  });
};

/**
 * Détecte les composants qui se rendent lentement
 */
const detectSlowComponents = () => {
  if (import.meta.env.DEV) {
    // En développement, on peut logger les composants lents
    const originalConsoleWarn = console.warn;
    console.warn = (...args) => {
      if (args[0] && typeof args[0] === 'string' && args[0].includes('Performance')) {
        sendAlert('performance', args.join(' '));
      }
      originalConsoleWarn.apply(console, args);
    };
  }
};

/**
 * Initialise le monitoring des erreurs JavaScript
 */
const initErrorMonitoring = () => {
  // Erreurs JavaScript non capturées
  window.addEventListener('error', (event) => {
    sendError({
      message: event.message,
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno,
      error: event.error,
      type: 'javascript',
    });
  });

  // Promesses rejetées non capturées
  window.addEventListener('unhandledrejection', (event) => {
    sendError({
      message: event.reason?.message || 'Unhandled Promise Rejection',
      error: event.reason,
      type: 'promise',
    });
  });
};

/**
 * Initialise le monitoring des requêtes API
 */
const initAPIMonitoring = () => {
  // Intercepter les requêtes fetch pour monitorer les erreurs API
  if (typeof window === 'undefined' || !window.fetch) {
    return;
  }
  
  const originalFetch = window.fetch;
  window.fetch = async (...args) => {
    const startTime = performance.now();
    const url = args[0];

    try {
      const response = await originalFetch(...args);
      const duration = performance.now() - startTime;

      // Envoyer la métrique de durée
      if (typeof url === 'string' && url.includes('/api/')) {
        sendMetric('API_Duration', duration, { endpoint: url });

        // Alerte si la requête est lente (> 2s)
        if (duration > 2000) {
          sendAlert('api', `Requête API lente: ${url} (${duration.toFixed(0)}ms)`);
        }

        // Alerte si erreur serveur (5xx)
        if (response.status >= 500) {
          sendAlert('api', `Erreur serveur ${response.status} sur ${url}`);
        }
      }

      return response;
    } catch (error) {
      const duration = performance.now() - startTime;
      sendError({
        message: `Erreur API: ${url}`,
        error: error,
        type: 'api',
        duration: duration,
      });
      throw error;
    }
  };
};

/**
 * Initialise les alertes
 */
const initAlerts = () => {
  // Vérifier périodiquement la santé de l'application
  setInterval(() => {
    checkApplicationHealth();
  }, 60000); // Toutes les minutes
};

/**
 * Vérifie la santé de l'application
 */
const checkApplicationHealth = () => {
  // Vérifier que React est toujours monté
  const root = document.getElementById('root');
  if (!root || !root.hasChildNodes()) {
    sendAlert('critical', 'Application React non montée');
  }

  // Vérifier la mémoire (si disponible)
  if (performance.memory) {
    const usedMB = performance.memory.usedJSHeapSize / 1048576;
    const limitMB = performance.memory.jsHeapSizeLimit / 1048576;
    const usagePercent = (usedMB / limitMB) * 100;

    if (usagePercent > 80) {
      sendAlert('performance', `Utilisation mémoire élevée: ${usagePercent.toFixed(1)}%`);
    }
  }
};

/**
 * Envoie une métrique
 */
const sendMetric = (name, value, metadata = {}) => {
  if (!import.meta.env.PROD) {
    console.log(`[Metric] ${name}: ${value}`, metadata);
    return;
  }

  // Envoyer à Sentry (si disponible)
  try {
    if (typeof window !== 'undefined' && window.Sentry && window.Sentry.metrics) {
      window.Sentry.metrics.distribution(name, value, {
        unit: 'millisecond',
        tags: metadata,
      });
    }
  } catch (e) {
    // Ignorer silencieusement si Sentry n'est pas disponible
  }

  // Envoyer à l'API (si disponible)
  const apiBase = import.meta.env.VITE_API_URL 
    ? `${import.meta.env.VITE_API_URL}/api` 
    : 'http://localhost:8000/api';

  // Envoyer à l'API (si disponible)
  try {
    if (typeof window !== 'undefined' && window.fetch) {
      const apiBase = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api` 
        : 'http://localhost:8000/api';

      fetch(`${apiBase}/analytics/metrics/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          metric: name,
          value: value,
          metadata: metadata,
          timestamp: new Date().toISOString(),
          url: typeof window !== 'undefined' ? window.location.href : '',
        }),
      }).catch(() => {
        // Ignorer silencieusement les erreurs
      });
    }
  } catch (e) {
    // Ignorer silencieusement les erreurs
  }
};

/**
 * Envoie une erreur
 */
const sendError = (errorData) => {
  if (!import.meta.env.PROD) {
    console.error('[Error]', errorData);
    return;
  }

  // Envoyer à Sentry (si disponible)
  try {
    if (typeof window !== 'undefined' && window.Sentry && window.Sentry.captureException) {
      window.Sentry.captureException(errorData.error || new Error(errorData.message), {
        tags: {
          type: errorData.type,
          filename: errorData.filename,
          lineno: errorData.lineno,
        },
        extra: errorData,
      });
    }
  } catch (e) {
    // Ignorer silencieusement si Sentry n'est pas disponible
  }
};

/**
 * Envoie une alerte
 */
const sendAlert = (level, message, metadata = {}) => {
  if (!import.meta.env.PROD) {
    console.warn(`[Alert ${level}]`, message, metadata);
    return;
  }

  // Envoyer à Sentry (si disponible)
  try {
    if (typeof window !== 'undefined' && window.Sentry && window.Sentry.captureMessage) {
      window.Sentry.captureMessage(message, {
        level: level === 'critical' ? 'error' : 'warning',
        tags: {
          alert_level: level,
          ...metadata,
        },
      });
    }
  } catch (e) {
    // Ignorer silencieusement si Sentry n'est pas disponible
  }

  // Envoyer à l'API (si disponible)
  try {
    if (typeof window !== 'undefined' && window.fetch) {
      const apiBase = import.meta.env.VITE_API_URL 
        ? `${import.meta.env.VITE_API_URL}/api` 
        : 'http://localhost:8000/api';

      fetch(`${apiBase}/monitoring/alerts/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          level: level,
          message: message,
          metadata: metadata,
          timestamp: new Date().toISOString(),
          url: typeof window !== 'undefined' ? window.location.href : '',
        }),
      }).catch(() => {
        // Ignorer silencieusement les erreurs
      });
    }
  } catch (e) {
    // Ignorer silencieusement les erreurs
  }
};

/**
 * Export pour utilisation dans l'application
 */
export default {
  initMonitoring,
  sendMetric,
  sendError,
  sendAlert,
};

