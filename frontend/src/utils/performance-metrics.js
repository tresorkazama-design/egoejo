/**
 * Utilitaires pour mesurer et tracker les métriques de performance
 * Core Web Vitals et métriques personnalisées
 */

/**
 * Mesure les Core Web Vitals
 */
export const measureWebVitals = () => {
  if (typeof window === 'undefined' || !window.performance) {
    return;
  }

  // Largest Contentful Paint (LCP)
  if ('PerformanceObserver' in window) {
    try {
      const lcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        const lcp = lastEntry.renderTime || lastEntry.loadTime;
        
        if (lcp) {
          trackMetric('LCP', lcp);
          // LCP devrait être < 2.5s
          if (lcp > 2500) {
            console.warn(`LCP is slow: ${lcp}ms`);
          }
        }
      });
      lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
    } catch (e) {
      // PerformanceObserver peut ne pas être supporté
    }

    // First Input Delay (FID)
    try {
      const fidObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          const fid = entry.processingStart - entry.startTime;
          trackMetric('FID', fid);
          // FID devrait être < 100ms
          if (fid > 100) {
            console.warn(`FID is slow: ${fid}ms`);
          }
        });
      });
      fidObserver.observe({ entryTypes: ['first-input'] });
    } catch (e) {
      // PerformanceObserver peut ne pas être supporté
    }

    // Cumulative Layout Shift (CLS)
    try {
      let clsValue = 0;
      let sessionValue = 0;
      let sessionEntries = [];

      const clsObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          // Only count if the layout shift had no recent user input
          if (!entry.hadRecentInput) {
            const firstSessionEntry = sessionEntries[0];
            const lastSessionEntry = sessionEntries[sessionEntries.length - 1];

            // If the entry occurred less than 1 second after the previous entry
            // and less than 5 seconds after the first entry in the session,
            // include the entry in the current session. Otherwise, start a new session.
            if (
              sessionValue &&
              entry.startTime - lastSessionEntry.startTime < 1000 &&
              entry.startTime - firstSessionEntry.startTime < 5000
            ) {
              sessionValue += entry.value;
              sessionEntries.push(entry);
            } else {
              sessionValue = entry.value;
              sessionEntries = [entry];
            }

            // If the current session value is larger than the current CLS value,
            // update CLS and the entries contributing to it.
            if (sessionValue > clsValue) {
              clsValue = sessionValue;
              // Note: clsEntries was stored but never used, removed for linting
            }
          }
        }

        if (clsValue) {
          trackMetric('CLS', clsValue);
          // CLS devrait être < 0.1
          if (clsValue > 0.1) {
            console.warn(`CLS is poor: ${clsValue}`);
          }
        }
      });
      clsObserver.observe({ entryTypes: ['layout-shift'] });
    } catch (e) {
      // PerformanceObserver peut ne pas être supporté
    }
  }

  // Time to First Byte (TTFB)
  if (window.performance.timing) {
    const timing = window.performance.timing;
    const ttfb = timing.responseStart - timing.navigationStart;
    trackMetric('TTFB', ttfb);
  }

  // First Contentful Paint (FCP)
  if ('PerformanceObserver' in window) {
    try {
      const fcpObserver = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          if (entry.name === 'first-contentful-paint') {
            trackMetric('FCP', entry.startTime);
          }
        });
      });
      fcpObserver.observe({ entryTypes: ['paint'] });
    } catch (e) {
      // PerformanceObserver peut ne pas être supporté
    }
  }
};

/**
 * Track une métrique de performance
 */
const trackMetric = (name, value) => {
  if (import.meta.env.PROD) {
    // Envoyer à votre service d'analytics
    if (typeof window !== 'undefined' && window.gtag) {
      window.gtag('event', name, {
        event_category: 'Web Vitals',
        value: Math.round(name === 'CLS' ? value * 1000 : value),
        event_label: name,
        non_interaction: true,
      });
    }

    // Envoyer aussi à votre endpoint
    const apiBase = import.meta.env.VITE_API_URL 
      ? `${import.meta.env.VITE_API_URL}/api` 
      : 'http://localhost:8000/api';
    
    fetch(`${apiBase}/analytics/metrics/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        metric: name,
        value: value,
        timestamp: new Date().toISOString(),
        url: window.location.href,
      }),
    }).catch(() => {
      // Ignorer les erreurs silencieusement
    });
  } else {
    console.log(`[Performance Metric] ${name}: ${value}`);
  }
};

/**
 * Mesure le temps de chargement d'une page
 */
export const measurePageLoad = () => {
  if (typeof window === 'undefined' || !window.performance) {
    return;
  }

  window.addEventListener('load', () => {
    const timing = window.performance.timing;
    const loadTime = timing.loadEventEnd - timing.navigationStart;
    trackMetric('PageLoad', loadTime);
  });
};

/**
 * Mesure le temps de rendu d'un composant
 */
export const measureComponentRender = (componentName, renderFn) => {
  if (import.meta.env.DEV && typeof window !== 'undefined' && window.performance) {
    const start = performance.now();
    const result = renderFn();
    const end = performance.now();
    const duration = end - start;
    
    if (duration > 16) { // Plus d'une frame (60fps)
      console.warn(`[Performance] ${componentName} took ${duration.toFixed(2)}ms to render`);
    }
    
    return result;
  }
  return renderFn();
};

/**
 * Initialise le tracking des métriques de performance
 */
export const initPerformanceTracking = () => {
  if (typeof window === 'undefined') {
    return;
  }

  measureWebVitals();
  measurePageLoad();
};

