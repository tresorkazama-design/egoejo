import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration Playwright pour les tests E2E en production
 * Utilise l'URL de production au lieu du serveur local
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 60 * 1000, // Timeout plus long pour la production
  expect: {
    timeout: 10000, // Timeout plus long pour les assertions
  },
  fullyParallel: false, // Exécuter séquentiellement en production pour éviter la surcharge
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Un seul worker en production
  reporter: 'html',
  use: {
    actionTimeout: 10000, // Timeout plus long pour les actions
    baseURL: process.env.PLAYWRIGHT_BASE_URL || process.env.VITE_APP_URL || 'https://egoejo.org',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure', // Garder les vidéos en cas d'échec
  },

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Seulement Chromium en production pour des tests plus rapides
  ],

  // Pas de serveur web local en production
  // webServer: undefined,
});

