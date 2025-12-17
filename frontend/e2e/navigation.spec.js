import { test, expect } from '@playwright/test';

test.describe('Navigation', () => {
  test('devrait naviguer entre toutes les pages principales', async ({ page }) => {
    await page.goto('/');
    
          const pages = [
            { name: 'Univers', url: '/univers' },
            { name: 'Vision', url: '/vision' },
            { name: 'Citations', url: '/citations' },
            { name: 'Alliances', url: '/alliances' },
            { name: 'Projets', url: '/projets' },
            { name: 'Contenus', url: '/contenus' },
            { name: 'Communauté', url: '/communaute' },
            { name: 'Votes', url: '/votes' },
            { name: 'Rejoindre', url: '/rejoindre' },
          ];
    
    for (const pageInfo of pages) {
      // Cliquer sur le lien (utiliser first() pour éviter l'ambiguïté si plusieurs liens existent)
      const link = page.getByRole('link', { name: new RegExp(pageInfo.name, 'i') }).first();
      await link.click();
      
      // Vérifier l'URL
      await expect(page).toHaveURL(new RegExp(pageInfo.url));
      
      // Vérifier que le contenu est chargé
      const mainContent = page.locator('main, [role="main"], h1');
      await expect(mainContent.first()).toBeVisible();
      
      // Retourner à la page d'accueil
      await page.goto('/');
    }
  });

  test('devrait gérer la page 404', async ({ page }) => {
    await page.goto('/page-inexistante');
    
    // Vérifier que la page 404 est affichée (utiliser first() pour éviter l'ambiguïté)
    await expect(page.getByText(/404|not found|page introuvable/i).first()).toBeVisible({ timeout: 10000 });
  });

  test('devrait pouvoir utiliser le bouton retour du navigateur', async ({ page }) => {
    await page.goto('/');
    await page.goto('/univers');
    await page.goto('/vision');
    
    // Utiliser le bouton retour
    await page.goBack();
    await expect(page).toHaveURL(/.*univers/);
    
    await page.goBack();
    await expect(page).toHaveURL('/');
  });
});

