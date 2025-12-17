import { test, expect } from '@playwright/test';

test.describe('Page Contenus', () => {
  test('devrait charger la page contenus', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page).toHaveTitle(/EGOEJO/i);
    const mainContent = page.locator('main, [role="main"], .page--citations');
    await expect(mainContent.first()).toBeVisible();
  });

  test('devrait afficher le titre "Contenus"', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page.getByRole('heading', { level: 1, name: /Contenus/i })).toBeVisible();
  });

  test('devrait afficher le badge "Ressources éducatives"', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page.getByText('Ressources éducatives')).toBeVisible();
  });

  test('devrait afficher le blockquote highlight', async ({ page }) => {
    await page.goto('/contenus');
    const blockquote = page.locator('blockquote');
    await expect(blockquote.first()).toBeVisible();
    await expect(blockquote.first()).toContainText(/Chaque contenu est une invitation/i);
  });

  test('devrait afficher les stats', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page.getByText(/contenu/i)).toBeVisible();
    await expect(page.getByText(/format/i)).toBeVisible();
    await expect(page.getByText(/bibliothèque/i)).toBeVisible();
  });

  test('devrait afficher la section CTA "Partagez vos contenus"', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page.getByRole('heading', { name: /Partagez vos contenus/i })).toBeVisible();
  });

  test('devrait afficher les liens de navigation dans le CTA', async ({ page }) => {
    await page.goto('/contenus');
    const linkRejoindre = page.getByRole('link', { name: /Rejoindre l'Alliance/i });
    const linkProposer = page.getByRole('link', { name: /Proposer un contenu/i });
    await expect(linkRejoindre).toBeVisible();
    await expect(linkProposer).toBeVisible();
  });

  test('devrait afficher la section références "Types de contenus"', async ({ page }) => {
    await page.goto('/contenus');
    // Attendre que la page soit complètement chargée
    await page.waitForLoadState('networkidle');
    // Vérifier avec un timeout plus long et first() pour éviter l'ambiguïté
    await expect(page.getByRole('heading', { name: /Types de contenus/i }).first()).toBeVisible({ timeout: 10000 });
  });
});

