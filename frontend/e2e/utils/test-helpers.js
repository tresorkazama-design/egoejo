/**
 * Helpers globaux pour les tests E2E Playwright
 */

/**
 * Configure le mode test global pour rendre les tests déterministes
 * - Définit prefers-reduced-motion: reduce
 * - Désactive scroll-behavior: smooth
 * - Définit VITE_E2E=1 pour désactiver les animations lourdes (GSAP/Three)
 * @param {import('@playwright/test').Page} page
 */
export async function setupTestMode(page) {
  await page.addInitScript(() => {
    // 1. Forcer prefers-reduced-motion: reduce
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: (query) => {
        if (query === '(prefers-reduced-motion: reduce)') {
          return {
            matches: true,
            media: query,
            onchange: null,
            addListener: () => {},
            removeListener: () => {},
            addEventListener: () => {},
            removeEventListener: () => {},
            dispatchEvent: () => true,
          };
        }
        return mediaQuery;
      },
    });

    // 2. Désactiver scroll-behavior: smooth
    const style = document.createElement('style');
    style.textContent = `
      * {
        scroll-behavior: auto !important;
      }
    `;
    document.head.appendChild(style);

    // 3. Définir VITE_E2E=1 pour désactiver les animations lourdes
    window.VITE_E2E = true;
    // Stocker dans localStorage pour que React puisse y accéder
    window.localStorage.setItem('VITE_E2E', '1');
  });
}

/**
 * Configure la langue française pour les tests
 * @param {import('@playwright/test').Page} page
 */
export async function setupFrenchLanguage(page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('egoejo_lang', 'fr');
    // Forcer aussi la langue du navigateur pour les tests
    Object.defineProperty(navigator, 'language', {
      writable: true,
      value: 'fr-FR'
    });
  });
}

/**
 * Mock par défaut de l'API de configuration des features
 * @param {import('@playwright/test').Page} page
 */
export async function mockFeaturesConfig(page) {
  await page.route('**/api/config/features/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        saka_enabled: true,
        saka_vote_enabled: true,
        saka_project_boost_enabled: true,
      }),
    });
  });
}

/**
 * Mock par défaut de l'API d'authentification (non authentifié)
 * @param {import('@playwright/test').Page} page
 */
export async function mockUnauthenticated(page) {
  await page.route('**/api/auth/me/', async (route) => {
    await route.fulfill({
      status: 401,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'Authentication credentials were not provided.' }),
    });
  });
}

/**
 * Mock par défaut de l'API d'authentification (authentifié)
 * @param {import('@playwright/test').Page} page
 * @param {Object} user - Données utilisateur (optionnel)
 */
export async function mockAuthenticated(page, user = {}) {
  const defaultUser = {
    id: 1,
    username: 'testuser',
    email: 'test@example.com',
    is_staff: false,
    is_superuser: false,
    ...user,
  };

  await page.addInitScript(() => {
    window.localStorage.setItem('token', 'mock-access-token');
    window.localStorage.setItem('refresh_token', 'mock-refresh-token'); // Note: refresh_token (pas refreshToken)
  });

  await page.route('**/api/auth/me/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(defaultUser),
    });
  });
}

/**
 * Login as user - Helper pour authentifier un utilisateur dans les tests
 * @param {import('@playwright/test').Page} page
 * @param {Object} options - Options (user, token, refreshToken)
 * @returns {Promise<void>}
 */
export async function loginAsUser(page, options = {}) {
  const {
    user = {
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      is_staff: false,
      is_superuser: false,
    },
    token = 'mock-access-token',
    refreshToken = 'mock-refresh-token',
  } = options;

  // Définir le token dans localStorage AVANT le chargement de la page
  // Utiliser addInitScript pour que ce soit fait avant que React ne charge
  await page.addInitScript(({ token, refreshToken }) => {
    window.localStorage.setItem('token', token);
    window.localStorage.setItem('refresh_token', refreshToken); // Note: refresh_token (pas refreshToken)
  }, { token, refreshToken });

  // Mock l'endpoint /api/auth/me/ qui est appelé au chargement par AuthContext
  await page.route('**/api/auth/me/', async (route) => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(user),
    });
  });

  // Mock /api/config/features/ si pas déjà fait
  await mockFeaturesConfig(page);
}

/**
 * Helper pour naviguer vers une route et attendre que l'app soit chargée
 * Aucun waitForTimeout - utilise des attentes actives
 * @param {import('@playwright/test').Page} page
 * @param {string} route - Route à visiter (ex: '/admin', '/dashboard')
 * @param {Object} options - Options (waitForSelector, timeout, dataTestId)
 * @returns {Promise<void>}
 */
export async function gotoAuthed(page, route, options = {}) {
  const {
    waitForSelector = '#root',
    dataTestId = null, // Ex: 'admin-page', 'projets-page'
    timeout = 10000,
  } = options;

  // Aller sur la route
  await page.goto(route);

  // Attendre que le DOM soit chargé
  await page.waitForLoadState('domcontentloaded');

  // Attendre que l'élément root soit présent (l'app React est montée)
  await page.waitForSelector(waitForSelector, { state: 'attached', timeout });

  // Attendre que l'app React soit prête (AuthContext a fini de charger)
  // On vérifie que l'élément root contient du contenu
  await page.waitForFunction(
    (selector) => {
      const element = document.querySelector(selector);
      return element && element.children.length > 0;
    },
    waitForSelector,
    { timeout }
  );

  // Si un data-testid est fourni, attendre qu'il soit visible
  // Sinon, essayer de détecter automatiquement le data-testid de la page
  const testIdToWait = dataTestId || route.split('/').filter(Boolean)[0] + '-page';
  if (testIdToWait) {
    try {
      await page.waitForFunction(
        (testId) => {
          const element = document.querySelector(`[data-testid="${testId}"]`);
          return element && element.offsetParent !== null; // Vérifier que l'élément est visible
        },
        testIdToWait,
        { timeout: 5000 }
      );
    } catch {
      // Si le data-testid n'existe pas, on continue quand même
      // Certaines pages peuvent ne pas avoir de data-testid
    }
  }

  // Utiliser waitForAppIdle pour attendre que l'app soit complètement prête
  await waitForAppIdle(page, { timeout: 10000 });
}

/**
 * Helper pour attendre que l'app soit idle (plus de requêtes fetch actives)
 * Utilise une instrumentation simple pour tracker les requêtes fetch
 * @param {import('@playwright/test').Page} page
 * @param {Object} options - Options (timeout, pollInterval)
 * @returns {Promise<void>}
 */
export async function waitForAppIdle(page, options = {}) {
  const { timeout = 10000, pollInterval = 100 } = options;

  // Instrumenter fetch pour tracker les requêtes actives
  await page.addInitScript(() => {
    if (!window.__e2eFetchCount) {
      window.__e2eFetchCount = 0;
      window.__e2eActiveFetches = new Set();

      const originalFetch = window.fetch;
      window.fetch = function(...args) {
        const fetchId = Symbol('fetch');
        window.__e2eFetchCount++;
        window.__e2eActiveFetches.add(fetchId);

        const promise = originalFetch.apply(this, args);
        promise
          .finally(() => {
            window.__e2eActiveFetches.delete(fetchId);
          });

        return promise;
      };
    }
  });

  // Attendre que toutes les requêtes soient terminées
  await page.waitForFunction(
    () => {
      return window.__e2eActiveFetches && window.__e2eActiveFetches.size === 0;
    },
    { timeout, polling: pollInterval }
  );

  // Attendre aussi que l'élément "app-ready" soit présent (si défini)
  // ou que le DOM soit stable
  try {
    await page.waitForFunction(
      () => {
        // Vérifier si un élément app-ready existe
        const appReady = document.querySelector('[data-testid="app-ready"]');
        if (appReady) return true;

        // Sinon, vérifier que le root contient du contenu et qu'il n'y a pas de spinner
        const root = document.querySelector('#root');
        if (!root || root.children.length === 0) return false;

        const loadingSpinner = document.querySelector('[data-testid="loading"], .loading, [aria-busy="true"]');
        if (loadingSpinner && loadingSpinner.offsetParent !== null) return false;

        return true;
      },
      { timeout: 5000 }
    );
  } catch {
    // Si app-ready n'existe pas, on continue quand même
  }
}

/**
 * Setup par défaut pour les tests mock-only (pas besoin de backend)
 * @param {import('@playwright/test').Page} page
 * @param {Object} options - Options (language, auth)
 */
export async function setupMockOnlyTest(page, options = {}) {
  const { language = 'fr', auth = false, user = {} } = options;

  // Toujours activer le mode test pour désactiver les animations
  await setupTestMode(page);

  if (language === 'fr') {
    await setupFrenchLanguage(page);
  }

  await mockFeaturesConfig(page);

  if (auth) {
    await mockAuthenticated(page, user);
  } else {
    await mockUnauthenticated(page);
  }
}

/**
 * Helper pour attendre qu'un élément soit dans le viewport
 * Utilise polling avec getBoundingClientRect() pour vérifier la visibilité
 * @param {import('@playwright/test').Page} page
 * @param {string} selectorOrId - Sélecteur CSS ou ID (avec ou sans #)
 * @param {Object} options - Options (timeout, tolerance)
 * @returns {Promise<void>}
 */
export async function waitForElementInViewport(page, selectorOrId, options = {}) {
  const { timeout = 5000, tolerance = 1 } = options;
  const selector = selectorOrId.startsWith('#') 
    ? `#${selectorOrId.replace('#', '')}` 
    : selectorOrId;
  
  await page.waitForFunction(
    ({ selector, tolerance }) => {
      const element = selector.startsWith('#')
        ? document.getElementById(selector.replace('#', ''))
        : document.querySelector(selector);
      
      if (!element) return false;
      
      const rect = element.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      
      // L'élément est dans le viewport si :
      // - rect.top est entre -tolerance et viewportHeight
      // - rect.bottom est > 0 (au moins une partie visible)
      const isInViewport = rect.top >= -tolerance && 
                          rect.top < viewportHeight + tolerance &&
                          rect.bottom > 0;
      
      return isInViewport;
    },
    { selector, tolerance },
    { timeout }
  );
}

/**
 * Helper pour attendre que toutes les requêtes API soient terminées
 * Utilise waitForAppIdle qui track les requêtes fetch
 * @param {import('@playwright/test').Page} page
 * @param {Object} options - Options (timeout, pollInterval)
 * @returns {Promise<void>}
 */
export async function waitForApiIdle(page, options = {}) {
  await waitForAppIdle(page, options);
}

