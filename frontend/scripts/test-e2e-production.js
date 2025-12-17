#!/usr/bin/env node

/**
 * Script pour exécuter les tests E2E en production
 * Usage: npm run test:e2e:production
 */

import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const projectRoot = join(__dirname, '..');

console.log('🚀 Exécution des tests E2E en production...\n');

// Vérifier que l'URL de production est définie
const productionUrl = process.env.PLAYWRIGHT_BASE_URL || process.env.VITE_APP_URL || 'https://egoejo.org';
console.log(`📍 URL de production: ${productionUrl}\n`);

try {
  // Exécuter les tests avec la configuration de production
  execSync(
    `npx playwright test --config=playwright.production.config.js`,
    {
      cwd: projectRoot,
      stdio: 'inherit',
      env: {
        ...process.env,
        PLAYWRIGHT_BASE_URL: productionUrl,
      },
    }
  );
  console.log('\n✅ Tous les tests E2E en production ont réussi!');
} catch (error) {
  console.error('\n❌ Certains tests E2E en production ont échoué');
  process.exit(1);
}

