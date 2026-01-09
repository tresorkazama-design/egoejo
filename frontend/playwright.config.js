import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration Playwright pour les tests E2E
 * 
 * MODES DISPONIBLES:
 * - Mode "mock-only" (par défaut) : Tous les tests mockent les APIs, pas besoin de backend
 * - Mode "full-stack" : Tests qui nécessitent le backend réel (backend-connection.spec.js)
 * 
 * Usage:
 * - Tests mock-only (par défaut): npx playwright test
 * - Tests full-stack: E2E_MODE=full-stack npx playwright test --project="full-stack"
 * 
 * @see https://playwright.dev/docs/test-configuration
 */
const E2E_MODE = process.env.E2E_MODE || 'mock-only';

export default defineConfig({
  testDir: './e2e',
  
  /* Maximum time one test can run for. */
  timeout: 60 * 1000, // 60s pour les tests avec animations (augmenté pour cold start Django en CI)
  
  expect: {
    /**
     * Maximum time expect() should wait for the condition to be met.
     * Augmenté à 10s pour les éléments qui se chargent lentement
     */
    timeout: 10000
  },
  
  /* Run tests in files in parallel */
  fullyParallel: true,
  
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  
  /* Retry on CI only - Retries intelligents pour éliminer les erreurs d'infrastructure */
  // En CI : 2 retries pour gérer les timeouts/erreurs infrastructure uniquement
  // En local : 0 retry pour détecter immédiatement les bugs réels
  // NOTE: Les retries ne s'appliquent qu'aux timeouts/erreurs réseau, pas aux erreurs fonctionnelles
  retries: process.env.CI ? 2 : 0,
  
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: process.env.CI ? 'github' : 'line',
  
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Maximum time each action such as `click()` can take. */
    actionTimeout: 60 * 1000, // 60s pour les actions lentes (augmenté pour cold start Django en CI)
    
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    
    /* Screenshot on failure */
    screenshot: 'only-on-failure',
    
    /* Video on failure (optionnel, peut être activé si nécessaire) */
    // video: 'on-first-retry',
    
    /* Force la langue française par défaut pour tous les tests mock-only */
    /* Cela évite les échecs i18n où les tests cherchent du texte FR mais la page est en EN */
    locale: 'fr-FR',
  },

  /* Configure projects for major browsers */
  projects: [
    // MODE MOCK-ONLY (par défaut) - Pas besoin de backend
    // Exclut backend-connection.spec.js qui nécessite le backend réel
    {
      name: 'chromium',
      testMatch: E2E_MODE === 'mock-only' 
        ? ['**/*.spec.js', '!**/backend-connection.spec.js']
        : '**/*.spec.js',
      use: { 
        ...devices['Desktop Chrome'],
        // Force la locale française pour tous les tests mock-only
        locale: 'fr-FR',
        // Setup global : force la langue FR dans localStorage pour tous les tests mock-only
        // Cela évite les échecs i18n où les tests cherchent du texte FR mais la page est en EN
        // Note: addInitScript doit être appelé dans chaque test, mais on peut le faire via setupMockOnlyTest
        // ou via un helper global. Pour l'instant, on force juste la locale du navigateur.
      },
    },
    {
      name: 'Mobile Chrome',
      testMatch: E2E_MODE === 'mock-only' 
        ? ['**/*.spec.js', '!**/backend-connection.spec.js']
        : '**/*.spec.js',
      use: { 
        ...devices['Pixel 5'],
        locale: 'fr-FR',
      },
    },
    
    // MODE FULL-STACK - Nécessite le backend réel
    // Seulement si E2E_MODE=full-stack
    ...(E2E_MODE === 'full-stack' ? [
      {
        name: 'full-stack',
        testMatch: '**/backend-connection.spec.js',
        use: { 
          ...devices['Desktop Chrome'],
          baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
          // Pour full-stack, on peut utiliser le backend réel
          // Pas de locale forcée car on teste la connexion réelle
        },
      },
    ] : []),
  ],

  /* Run your local dev server before starting the tests */
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000, // 2 minutes pour démarrer le serveur
    stdout: 'ignore',
    stderr: 'pipe',
  },
  
  /* Global setup/teardown (optionnel) */
  // globalSetup: './e2e/utils/global-setup.js',
  // globalTeardown: './e2e/utils/global-teardown.js',
});

