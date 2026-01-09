/**
 * Tests E2E pour le comportement offline de la section Contenu
 */

import { test, expect } from '@playwright/test';

test.describe('Contenus - Comportement Offline', () => {
  test.beforeEach(async ({ page, context }) => {
    // Aller à la page des contenus
    await page.goto('/contenus');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    await page.waitForSelector('[data-testid="contenus-page"]', { timeout: 10000 });
  });

  test('devrait charger les contenus en ligne', async ({ page }) => {
    // Vérifier que la page des contenus est chargée
    await expect(page.locator('[data-testid="contenus-page"]')).toBeVisible();
    
    // Vérifier qu'il y a au moins un contenu ou un message approprié
    const hasContent = await page.locator('[role="listitem"]').count() > 0;
    const hasEmptyMessage = await page.locator('text=/aucun contenu/i').isVisible().catch(() => false);
    
    expect(hasContent || hasEmptyMessage).toBe(true);
  });

  test('devrait afficher les contenus depuis le cache en mode offline', async ({ page, context }) => {
    // Vérifier qu'il y a des contenus chargés
    const contentCount = await page.locator('[role="listitem"]').count();
    
    if (contentCount === 0) {
      // Si aucun contenu, on ne peut pas tester le cache offline
      test.skip();
      return;
    }

    // Simuler le mode offline
    await context.setOffline(true);
    
    // Recharger la page
    await page.reload();
    
    // Attendre que la page se charge (peut prendre un peu de temps avec le cache)
    await page.waitForTimeout(3000);
    
    // Vérifier que l'indicateur offline est visible (dans Layout ou dans la page)
    const offlineIndicator = page.locator('text=/hors-ligne|offline|Mode hors-ligne/i').first();
    await expect(offlineIndicator).toBeVisible({ timeout: 10000 });
    
    // Vérifier que les contenus sont toujours visibles (depuis le cache)
    const cachedContentCount = await page.locator('[role="listitem"]').count();
    expect(cachedContentCount).toBeGreaterThan(0);
  });

  test('devrait afficher un message approprié si aucun contenu en cache', async ({ page, context }) => {
    // Aller directement en mode offline sans charger de contenu
    await context.setOffline(true);
    
    // Recharger la page
    await page.reload();
    
    // Attendre que la page se charge
    await page.waitForTimeout(2000);
    
    // Vérifier qu'un message offline est affiché
    const offlineMessage = page.locator('text=/hors-ligne|offline|aucun contenu en cache/i').first();
    await expect(offlineMessage).toBeVisible({ timeout: 5000 });
  });

  test('devrait permettre la navigation entre pages en mode offline si en cache', async ({ page, context }) => {
    // Attendre que les contenus soient chargés
    await page.waitForLoadState('networkidle');
    
    // Vérifier s'il y a une pagination
    const hasPagination = await page.locator('[data-testid="pagination-next"]').isVisible().catch(() => false);
    
    if (!hasPagination) {
      // Pas de pagination, on ne peut pas tester
      test.skip();
      return;
    }

    // Aller à la page suivante pour charger plus de contenus en cache
    await page.click('[data-testid="pagination-next"]');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);

    // Simuler le mode offline
    await context.setOffline(true);
    
    // Recharger la page
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Vérifier que les contenus sont toujours accessibles
    const contentCount = await page.locator('[role="listitem"]').count();
    expect(contentCount).toBeGreaterThan(0);
  });

  test('devrait restaurer la connexion et recharger les contenus', async ({ page, context }) => {
    // Charger les contenus en ligne
    await page.waitForLoadState('networkidle');
    const initialContentCount = await page.locator('[role="listitem"]').count();
    
    // Passer en mode offline
    await context.setOffline(true);
    await page.reload();
    await page.waitForTimeout(2000);
    
    // Vérifier que l'indicateur offline est visible
    await expect(page.locator('text=/hors-ligne|offline/i').first()).toBeVisible({ timeout: 5000 });
    
    // Restaurer la connexion
    await context.setOffline(false);
    
    // Attendre que la connexion soit rétablie
    await page.waitForTimeout(1000);
    
    // Recharger la page
    await page.reload();
    await page.waitForLoadState('networkidle');
    
    // Vérifier que les contenus sont rechargés
    const restoredContentCount = await page.locator('[role="listitem"]').count();
    expect(restoredContentCount).toBeGreaterThanOrEqual(initialContentCount);
  });
});

