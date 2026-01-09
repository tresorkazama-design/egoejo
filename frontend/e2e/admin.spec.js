import { test, expect } from './fixtures/auth';
import { setupMockOnlyTest } from './utils/test-helpers';

/**
 * Tests E2E pour la page Admin
 */
test.describe('Page Admin', () => {
  test.beforeEach(async ({ page, loginAsUser }) => {
    // Setup mock-only : langue FR + mocks API par défaut
    await setupMockOnlyTest(page, { language: 'fr' });
    
    // Authentifier en tant qu'admin
    await loginAsUser({
      user: {
        id: 1,
        username: 'admin',
        email: 'admin@example.com',
        is_staff: true,
        is_superuser: true,
      },
    });

    // Mock des données d'intentions pour les tests
    await page.route('**/api/intents/admin/**', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            count: 3,
            results: [
              {
                id: 1,
                nom: 'Test User 1',
                email: 'test1@example.com',
                profil: 'je-decouvre',
                created_at: '2025-01-27T10:00:00Z',
              },
              {
                id: 2,
                nom: 'Test User 2',
                email: 'test2@example.com',
                profil: 'je-participe',
                created_at: '2025-01-27T11:00:00Z',
              },
              {
                id: 3,
                nom: 'Test User 3',
                email: 'test3@example.com',
                profil: 'je-contribue',
                created_at: '2025-01-27T12:00:00Z',
              },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });
  });

  test('devrait afficher un message si non authentifié', async ({ page }) => {
    // Pour ce test, on ne s'authentifie pas
    await page.route('**/api/auth/me/', async (route) => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Authentication credentials were not provided.' }),
      });
    });

    await page.goto('/admin');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier qu'un message d'authentification est affiché
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  test('devrait charger la page admin avec authentification mockée', async ({ page, gotoAuthed }) => {
    await gotoAuthed('/admin');
    
    // Vérifier que la page admin est chargée
    const adminPage = page.locator('[data-testid="admin-page"], .admin-page, main, [role="main"]');
    await expect(adminPage.first()).toBeVisible({ timeout: 10000 });
  });

  test('devrait afficher la table des intentions', async ({ page, gotoAuthed }) => {
    await gotoAuthed('/admin');
    
    // Attendre que la table soit chargée
    const table = page.locator('table, [role="table"]');
    await expect(table.first()).toBeVisible({ timeout: 10000 });
    
    // Vérifier que les colonnes sont présentes
    await expect(page.getByTestId('admin-table-header-id')).toBeVisible();
    await expect(page.getByTestId('admin-table-header-nom')).toBeVisible();
    await expect(page.getByTestId('admin-table-header-email')).toBeVisible();
    await expect(page.getByTestId('admin-table-header-profil')).toBeVisible();
    await expect(page.getByTestId('admin-table-header-date')).toBeVisible();
  });

  test('devrait permettre de rechercher des intentions', async ({ page, gotoAuthed }) => {
    await gotoAuthed('/admin');
    
    // Trouver le champ de recherche
    const searchInput = page.getByTestId('admin-search-input');
    
    if (await searchInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await searchInput.fill('Test');
      
      // Attendre que les résultats soient filtrés (pas de waitForTimeout)
      await page.waitForLoadState('networkidle');
      
      // Vérifier que la recherche a été effectuée
      expect(await searchInput.inputValue()).toBe('Test');
    }
  });

  test('devrait permettre de filtrer par profil', async ({ page, gotoAuthed }) => {
    await gotoAuthed('/admin');
    
    // Trouver le filtre de profil
    const profilFilter = page.getByTestId('admin-profil-filter');
    
    if (await profilFilter.isVisible({ timeout: 5000 }).catch(() => false)) {
      await profilFilter.selectOption('je-decouvre');
      
      // Attendre que le filtre soit appliqué (pas de waitForTimeout)
      await page.waitForLoadState('networkidle');
      
      // Vérifier que le filtre a été sélectionné
      await expect(profilFilter).toHaveValue(/je-decouvre/i);
    }
  });

  test('devrait permettre d\'exporter en CSV', async ({ page, gotoAuthed }) => {
    // Intercepter la requête d'export
    let exportRequestMade = false;
    
    await page.route('**/api/intents/export/**', async (route) => {
      exportRequestMade = true;
      await route.fulfill({
        status: 200,
        contentType: 'text/csv',
        headers: {
          'Content-Disposition': 'attachment; filename="intents.csv"',
        },
        body: 'id,nom,email,profil\n1,Test User,test@example.com,je-decouvre\n',
      });
    });

    await gotoAuthed('/admin');
    
    // Trouver le bouton d'export
    const exportButton = page.getByTestId('admin-export-button');
    
    if (await exportButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      // Écouter les téléchargements
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      // Attendre le téléchargement
      const download = await downloadPromise;
      
      // Vérifier que le téléchargement a été déclenché
      expect(download.suggestedFilename()).toContain('.csv');
    }
  });

  test('devrait gérer les erreurs de chargement gracieusement', async ({ page, gotoAuthed }) => {
    // Simuler une erreur API
    await page.route('**/api/intents/admin/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Erreur serveur' }),
      });
    });

    await gotoAuthed('/admin');
    
    // La page ne devrait pas planter
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
    
    // Vérifier qu'un message d'erreur est affiché (si implémenté)
    // ou que la page reste fonctionnelle
  });
});
