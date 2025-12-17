import { test, expect } from '@playwright/test';

test.describe('Page d\'accueil', () => {
  test('devrait charger la page d\'accueil', async ({ page }) => {
    await page.goto('/');
    
    // Vérifier que la page est chargée
    await expect(page).toHaveTitle(/EGOEJO/i);
    
    // Vérifier que le contenu principal est présent
    const mainContent = page.locator('main, [role="main"], .home-page');
    await expect(mainContent.first()).toBeVisible();
  });

  test('devrait pouvoir naviguer vers la page Univers', async ({ page }) => {
    await page.goto('/');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Cliquer sur le lien Univers (utiliser first() pour éviter l'ambiguïté)
    const universLink = page.getByRole('link', { name: /univers/i }).first();
    await universLink.waitFor({ state: 'visible', timeout: 10000 });
    await universLink.click();
    
    // Vérifier que nous sommes sur la page Univers
    await expect(page).toHaveURL(/.*univers/, { timeout: 10000 });
  });

  test('devrait pouvoir naviguer vers la page Rejoindre', async ({ page }) => {
    await page.goto('/');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Cliquer sur le lien Rejoindre (utiliser first() pour éviter l'ambiguïté)
    const rejoindreLink = page.getByRole('link', { name: /rejoindre/i }).first();
    await rejoindreLink.waitFor({ state: 'visible', timeout: 10000 });
    await rejoindreLink.click();
    
    // Vérifier que nous sommes sur la page Rejoindre
    await expect(page).toHaveURL(/.*rejoindre/, { timeout: 10000 });
    
    // Vérifier que le formulaire est présent
    const form = page.locator('form, [role="form"]');
    await expect(form.first()).toBeVisible({ timeout: 10000 });
  });
});

