/**
 * Utilitaires pour optimiser les performances
 */
import { logger } from './logger';

/**
 * Debounce une fonction
 * @param {Function} func - Fonction à debouncer
 * @param {number} wait - Délai en millisecondes
 * @returns {Function} Fonction debouncée
 */
export const debounce = (func, wait = 300) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

/**
 * Throttle une fonction
 * @param {Function} func - Fonction à throttler
 * @param {number} limit - Limite en millisecondes
 * @returns {Function} Fonction throttlée
 */
export const throttle = (func, limit = 300) => {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
};

/**
 * Vérifie si la page est visible
 * @returns {boolean}
 */
export const isPageVisible = () => {
  return !document.hidden;
};

/**
 * Utilise requestIdleCallback si disponible, sinon setTimeout
 * @param {Function} callback - Fonction à exécuter
 * @param {Object} options - Options
 */
export const requestIdleCallbackPolyfill = (callback, options = {}) => {
  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, options);
  }
  // Fallback pour les navigateurs qui ne supportent pas requestIdleCallback
  return setTimeout(() => {
    callback({
      didTimeout: false,
      timeRemaining: () => 5, // Estimation
    });
  }, 1);
};

/**
 * Annule un requestIdleCallback
 * @param {number} id - ID retourné par requestIdleCallback
 */
export const cancelIdleCallbackPolyfill = (id) => {
  if ('cancelIdleCallback' in window) {
    return window.cancelIdleCallback(id);
  }
  return clearTimeout(id);
};

/**
 * Mesure les performances d'une fonction
 * @param {Function} func - Fonction à mesurer
 * @param {string} label - Label pour les dev tools
 * @returns {Promise<number>} Durée d'exécution en millisecondes
 */
export const measurePerformance = async (func, label = 'Function') => {
  if (import.meta.env.DEV && 'performance' in window) {
    const start = performance.now();
    await func();
    const end = performance.now();
    const duration = end - start;
    logger.debug(`${label}: ${duration.toFixed(2)}ms`);
    return duration;
  }
  const start = performance.now();
  await func();
  const end = performance.now();
  return end - start;
};

/**
 * Lazy load une ressource
 * @param {string} src - URL de la ressource
 * @param {string} type - Type de ressource ('script', 'style', 'image')
 * @returns {Promise}
 */
export const lazyLoadResource = (src, type = 'script') => {
  return new Promise((resolve, reject) => {
    if (type === 'script') {
      const script = document.createElement('script');
      script.src = src;
      script.async = true;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    } else if (type === 'style') {
      const link = document.createElement('link');
      link.rel = 'stylesheet';
      link.href = src;
      link.onload = resolve;
      link.onerror = reject;
      document.head.appendChild(link);
    } else if (type === 'image') {
      const img = new Image();
      img.src = src;
      img.onload = resolve;
      img.onerror = reject;
    }
  });
};

/**
 * Prefetch une ressource
 * @param {string} url - URL à prefetch
 * @param {string} as - Type de ressource
 */
export const prefetchResource = (url, as = 'fetch') => {
  const link = document.createElement('link');
  link.rel = 'prefetch';
  link.href = url;
  link.as = as;
  document.head.appendChild(link);
};

/**
 * Preload une ressource critique
 * @param {string} url - URL à preload
 * @param {string} as - Type de ressource
 * @param {string} type - MIME type
 */
export const preloadResource = (url, as = 'script', type = null) => {
  const link = document.createElement('link');
  link.rel = 'preload';
  link.href = url;
  link.as = as;
  if (type) link.type = type;
  if (as === 'font') link.crossOrigin = 'anonymous';
  document.head.appendChild(link);
};

/**
 * Vérifie si le navigateur supporte les fonctionnalités modernes
 * @returns {Object} Support des fonctionnalités
 */
export const checkBrowserSupport = () => {
  return {
    webgl: !!window.WebGLRenderingContext,
    webgl2: !!window.WebGL2RenderingContext,
    serviceWorker: 'serviceWorker' in navigator,
    intersectionObserver: 'IntersectionObserver' in window,
    requestIdleCallback: 'requestIdleCallback' in window,
    fetch: 'fetch' in window,
    promises: typeof Promise !== 'undefined',
  };
};

/**
 * Crée un cache LRU (Least Recently Used)
 * @param {number} maxSize - Taille maximale du cache
 * @returns {Object} Objet cache avec méthodes get, set, has, clear
 */
export const createCache = (maxSize = 50) => {
  const cache = new Map();
  
  return {
    get(key) {
      if (cache.has(key)) {
        // Déplacer la clé à la fin (LRU)
        const value = cache.get(key);
        cache.delete(key);
        cache.set(key, value);
        return value;
      }
      return undefined;
    },
    
    set(key, value) {
      if (cache.has(key)) {
        // Mettre à jour et déplacer à la fin
        cache.delete(key);
      } else if (cache.size >= maxSize) {
        // Supprimer le premier élément (le moins récemment utilisé)
        const firstKey = cache.keys().next().value;
        cache.delete(firstKey);
      }
      cache.set(key, value);
    },
    
    has(key) {
      return cache.has(key);
    },
    
    clear() {
      cache.clear();
    },
    
    size() {
      return cache.size;
    }
  };
};
