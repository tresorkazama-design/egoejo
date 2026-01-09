import { test, expect } from '@playwright/test';
import { setupMockOnlyTest } from './utils/test-helpers';

test.describe('Page Contenus', () => {
  test.beforeEach(async ({ page }) => {
    // Setup mock-only : langue FR + mocks API par défaut
    await setupMockOnlyTest(page, { language: 'fr' });
  });

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
    await expect(page.getByTestId('contenus-badge')).toBeVisible();
  });

  test('devrait afficher le blockquote highlight', async ({ page }) => {
    await page.goto('/contenus');
    const blockquote = page.locator('blockquote');
    await expect(blockquote.first()).toBeVisible();
    await expect(blockquote.first()).toContainText(/Chaque contenu est une invitation/i);
  });

  test('devrait afficher les stats', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page.getByTestId('contenus-stats-count')).toBeVisible();
    await expect(page.getByTestId('contenus-stats-formats')).toBeVisible();
    await expect(page.getByTestId('contenus-stats-library')).toBeVisible();
  });

  test('devrait afficher la section CTA "Partagez vos contenus"', async ({ page }) => {
    await page.goto('/contenus');
    await expect(page.getByRole('heading', { name: /Partagez vos contenus/i })).toBeVisible();
  });

  test('devrait afficher les liens de navigation dans le CTA', async ({ page }) => {
    await page.goto('/contenus');
    const linkRejoindre = page.getByTestId('contenus-link-rejoindre');
    const linkProposer = page.getByTestId('contenus-link-propose');
    await expect(linkRejoindre).toBeVisible();
    await expect(linkProposer).toBeVisible();
  });

  test('devrait afficher la section références "Types de contenus"', async ({ page }) => {
    await page.goto('/contenus');
    // Attendre que la page soit complètement chargée
    await page.waitForLoadState('networkidle');
    // Vérifier avec un timeout plus long
    await expect(page.getByTestId('contenus-types-section')).toBeVisible({ timeout: 10000 });
  });
});

