import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour la navigation par sections (ancres #hash)
 * 
 * Ces tests vérifient :
 * - Le scroll vers les sections via les liens d'ancres
 * - Le fonctionnement du skip-link pour l'accessibilité
 * - Que l'URL ne change pas de route lors de la navigation par sections
 * 
 * IMPORTANT : Ces tests sont bloquants en CI et échouent explicitement
 * si le scroll ne se produit pas.
 */

/**
 * Helper function pour attendre qu'un élément soit visible et dans le viewport
 * @param {Page} page - Instance Playwright Page
 * @param {string} selectorOrId - Sélecteur CSS ou ID de l'élément
 * @param {Object} options - Options (timeout, tolerance)
 * @returns {Promise<void>}
 */
async function waitForElementInViewport(page, selectorOrId, options = {}) {
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

test.describe('Navigation par sections (ancres)', () => {
  test.beforeEach(async ({ page }) => {
    // Aller à la page d'accueil avant chaque test
    await page.goto('/');
    // Attendre que la page soit complètement chargée
    await page.waitForLoadState('networkidle');
  });

  test('devrait scroller vers la section #soutenir lors du clic sur "Soutenir"', async ({ page }) => {
    // Enregistrer la position de scroll initiale
    const initialScrollY = await page.evaluate(() => window.scrollY);
    
    // Trouver le bouton "Soutenir"
    const soutenirLink = page.locator('a[href="#soutenir"]').first();
    
    // Vérifier que le lien existe
    await expect(soutenirLink).toBeVisible({ timeout: 5000 });
    
    // Vérifier que la section existe avant le clic
    const sectionExists = await page.evaluate(() => {
      return document.getElementById('soutenir') !== null;
    });
    expect(sectionExists).toBe(true);
    
    // Cliquer sur le lien "Soutenir"
    await soutenirLink.click();
    
    // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL (déterministe)
    await page.waitForFunction(
      () => window.location.hash === '#soutenir',
      { timeout: 5000 }
    );
    
    // ÉTAPE 2 : Attendre que la section soit visible dans le viewport (attente active)
    await waitForElementInViewport(page, '#soutenir', { timeout: 5000 });
    
    // Vérifier que le scroll s'est produit
    const finalScrollY = await page.evaluate(() => window.scrollY);
    expect(finalScrollY).toBeGreaterThan(initialScrollY);
    
    // Vérification finale : la section est bien visible
    const isSectionVisible = await page.evaluate(() => {
      const section = document.getElementById('soutenir');
      if (!section) return false;
      const rect = section.getBoundingClientRect();
      return rect.top >= -1 && rect.top < window.innerHeight + 1;
    });
    expect(isSectionVisible).toBe(true);
    
    // Vérifier que l'URL contient le hash #soutenir
    await expect(page).toHaveURL(/#soutenir/);
    
    // Vérifier que l'URL ne change pas de route (reste sur /)
    const currentPath = new URL(page.url()).pathname;
    expect(currentPath).toBe('/');
  });

  test('devrait activer le skip-link et transférer le focus sur #main-content', async ({ page }) => {
    // Trouver le skip-link
    const skipLink = page.locator('a[href="#main-content"]').first();
    
    // Vérifier que le skip-link existe
    await expect(skipLink).toBeVisible({ timeout: 5000 });
    
    // Vérifier que le skip-link est initialement masqué (hors écran)
    const isInitiallyHidden = await skipLink.evaluate((el) => {
      const style = window.getComputedStyle(el);
      return style.position === 'absolute' && (style.left === '-9999px' || parseFloat(style.left) < -1000);
    });
    expect(isInitiallyHidden).toBe(true);
    
    // Focus sur le skip-link (simuler Tab depuis le début de la page)
    await skipLink.focus();
    
    // Attendre que le skip-link devienne visible au focus (attente active)
    await page.waitForFunction(
      () => {
        const link = document.querySelector('a[href="#main-content"]');
        if (!link) return false;
        const style = window.getComputedStyle(link);
        const left = parseFloat(style.left);
        return left >= 0 && left < 100;
      },
      { timeout: 2000 }
    );
    
    // Vérifier que le skip-link est visible au focus
    const isVisibleOnFocus = await skipLink.evaluate((el) => {
      const style = window.getComputedStyle(el);
      const left = parseFloat(style.left);
      return left >= 0 && left < 100;
    });
    expect(isVisibleOnFocus).toBe(true);
    
    // Activer le skip-link (Enter)
    await skipLink.press('Enter');
    
    // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL
    await page.waitForFunction(
      () => window.location.hash === '#main-content',
      { timeout: 5000 }
    );
    
    // ÉTAPE 2 : Attendre que main-content soit visible dans le viewport
    await waitForElementInViewport(page, '#main-content', { timeout: 5000 });
    
    // ÉTAPE 3 : Attendre que main-content soit focus (assertion d'accessibilité)
    await page.waitForFunction(
      () => {
        const main = document.getElementById('main-content');
        if (!main) return false;
        // Le focus peut être sur main directement ou sur un élément enfant
        return document.activeElement === main || main.contains(document.activeElement);
      },
      { timeout: 3000 }
    );
    
    // Vérifier que l'URL contient le hash #main-content
    await expect(page).toHaveURL(/#main-content/);
    
    // Vérifier que l'URL ne change pas de route (reste sur /)
    const currentPath = new URL(page.url()).pathname;
    expect(currentPath).toBe('/');
    
    // Vérification finale : #main-content est focus
    const isMainFocused = await page.evaluate(() => {
      const main = document.getElementById('main-content');
      if (!main) return false;
      return document.activeElement === main || main.contains(document.activeElement);
    });
    expect(isMainFocused).toBe(true);
    
    // Vérification finale : #main-content est visible
    const isMainVisible = await page.evaluate(() => {
      const main = document.getElementById('main-content');
      if (!main) return false;
      const rect = main.getBoundingClientRect();
      return rect.top < window.innerHeight && rect.bottom > 0;
    });
    expect(isMainVisible).toBe(true);
  });

  test('devrait conserver la route lors de la navigation par sections', async ({ page }) => {
    // Aller sur une page spécifique
    await page.goto('/projets');
    await page.waitForLoadState('networkidle');
    
    // Vérifier qu'on est bien sur /projets
    await expect(page).toHaveURL(/.*projets/);
    const initialPath = new URL(page.url()).pathname;
    
    // Retourner à la page d'accueil
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Cliquer sur "Soutenir"
    const soutenirLink = page.locator('a[href="#soutenir"]').first();
    await expect(soutenirLink).toBeVisible({ timeout: 5000 });
    await soutenirLink.click();
    
    // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL
    await page.waitForFunction(
      () => window.location.hash === '#soutenir',
      { timeout: 5000 }
    );
    
    // ÉTAPE 2 : Attendre que la section soit visible
    await waitForElementInViewport(page, '#soutenir', { timeout: 5000 });
    
    // Vérifier que l'URL contient le hash
    await expect(page).toHaveURL(/#soutenir/);
    
    // VÉRIFICATION CRITIQUE : La route ne doit PAS changer
    const finalPath = new URL(page.url()).pathname;
    expect(finalPath).toBe('/');
    
    // Vérifier que seul le hash a changé, pas le pathname
    const url = new URL(page.url());
    expect(url.pathname).toBe('/');
    expect(url.hash).toBe('#soutenir');
  });

  test('devrait gérer le scroll même si on est déjà sur la page', async ({ page }) => {
    // Aller à la page d'accueil
    await page.goto('/');
    await page.waitForLoadState('networkidle');
    
    // Scroller un peu vers le bas
    await page.evaluate(() => window.scrollTo(0, 500));
    
    // Attendre que le scroll soit terminé (attente active)
    await page.waitForFunction(
      () => {
        // Le scroll est terminé quand window.scrollY est stable
        return Math.abs(window.scrollY - 500) < 5;
      },
      { timeout: 2000 }
    );
    
    // Enregistrer la position avant le clic
    const scrollBefore = await page.evaluate(() => window.scrollY);
    
    // Cliquer sur "Soutenir"
    const soutenirLink = page.locator('a[href="#soutenir"]').first();
    await expect(soutenirLink).toBeVisible({ timeout: 5000 });
    await soutenirLink.click();
    
    // ÉTAPE 1 : Attendre que le hash soit présent dans l'URL
    await page.waitForFunction(
      () => window.location.hash === '#soutenir',
      { timeout: 5000 }
    );
    
    // ÉTAPE 2 : Attendre que le scroll se produise ET que la section soit visible
    await page.waitForFunction(
      (scrollBefore) => {
        const section = document.getElementById('soutenir');
        if (!section) return false;
        const rect = section.getBoundingClientRect();
        const viewportHeight = window.innerHeight;
        const scrollAfter = window.scrollY;
        const isVisible = rect.top >= -1 && rect.top < viewportHeight + 1;
        // Le scroll doit avoir changé ET la section doit être visible
        return scrollAfter !== scrollBefore && isVisible;
      },
      scrollBefore,
      { timeout: 5000 }
    );
    
    // Vérifier que le scroll s'est produit (position différente)
    const scrollAfter = await page.evaluate(() => window.scrollY);
    expect(scrollAfter).not.toBe(scrollBefore);
    
    // Vérification finale : la section est visible
    const isSectionVisible = await page.evaluate(() => {
      const section = document.getElementById('soutenir');
      if (!section) return false;
      const rect = section.getBoundingClientRect();
      return rect.top >= -1 && rect.top < window.innerHeight + 1;
    });
    expect(isSectionVisible).toBe(true);
  });
});
