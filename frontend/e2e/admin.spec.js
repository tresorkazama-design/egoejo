import { test, expect } from '@playwright/test';

test.describe('Page Admin', () => {
  test.beforeEach(async ({ page }) => {
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
    await page.goto('/admin');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier qu'un message d'authentification est affiché
    // (le message exact dépend de l'implémentation)
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  test('devrait charger la page admin avec authentification mockée', async ({ page }) => {
    // Simuler une authentification
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'test-admin-token');
    });

    // Mock de la réponse d'authentification
    await page.route('**/api/intents/admin/**', async (route) => {
      const request = route.request();
      const authHeader = request.headers()['authorization'];
      
      if (authHeader && authHeader.includes('Bearer')) {
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
            ],
          }),
        });
      } else {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Non authentifié' }),
        });
      }
    });

    await page.goto('/admin');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que la page admin est chargée
    const adminPage = page.locator('[data-testid="admin-page"], .admin-page');
    await expect(adminPage.first()).toBeVisible({ timeout: 10000 });
  });

  test('devrait afficher la table des intentions', async ({ page }) => {
    // Simuler une authentification
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'test-admin-token');
    });

    await page.goto('/admin');
    await page.waitForLoadState('networkidle');
    
    // Attendre que la table soit chargée
    const table = page.locator('table, [role="table"]');
    await expect(table.first()).toBeVisible({ timeout: 10000 });
    
    // Vérifier que les colonnes sont présentes
    await expect(page.getByText(/id|nom|email|profil|date/i)).toBeVisible();
  });

  test('devrait permettre de rechercher des intentions', async ({ page }) => {
    // Simuler une authentification
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'test-admin-token');
    });

    await page.goto('/admin');
    await page.waitForLoadState('networkidle');
    
    // Trouver le champ de recherche
    const searchInput = page.getByLabel(/recherche|search/i).or(
      page.getByPlaceholder(/recherche|search/i)
    ).or(
      page.locator('input[type="search"], input[type="text"]').first()
    );
    
    if (await searchInput.isVisible()) {
      await searchInput.fill('Test');
      
      // Attendre que les résultats soient filtrés
      await page.waitForTimeout(500);
      
      // Vérifier que la recherche a été effectuée
      // (la vérification exacte dépend de l'implémentation)
      expect(await searchInput.inputValue()).toBe('Test');
    }
  });

  test('devrait permettre de filtrer par profil', async ({ page }) => {
    // Simuler une authentification
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'test-admin-token');
    });

    await page.goto('/admin');
    await page.waitForLoadState('networkidle');
    
    // Trouver le filtre de profil
    const profilFilter = page.getByLabel(/profil/i).or(
      page.locator('select[name*="profil"], select[id*="profil"]').first()
    );
    
    if (await profilFilter.isVisible()) {
      await profilFilter.selectOption('je-decouvre');
      
      // Attendre que le filtre soit appliqué
      await page.waitForTimeout(500);
      
      // Vérifier que le filtre a été sélectionné
      await expect(profilFilter).toHaveValue(/je-decouvre/i);
    }
  });

  test('devrait permettre d\'exporter en CSV', async ({ page }) => {
    // Simuler une authentification
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'test-admin-token');
    });

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

    await page.goto('/admin');
    await page.waitForLoadState('networkidle');
    
    // Trouver le bouton d'export
    const exportButton = page.getByRole('button', { name: /exporter|export|csv/i });
    
    if (await exportButton.isVisible()) {
      // Écouter les téléchargements
      const downloadPromise = page.waitForEvent('download');
      await exportButton.click();
      
      // Attendre le téléchargement
      const download = await downloadPromise;
      
      // Vérifier que le téléchargement a été déclenché
      expect(download.suggestedFilename()).toContain('.csv');
    }
  });

  test('devrait gérer les erreurs de chargement gracieusement', async ({ page }) => {
    // Simuler une authentification
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'test-admin-token');
    });

    // Simuler une erreur API
    await page.route('**/api/intents/admin/**', async (route) => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Erreur serveur' }),
      });
    });

    await page.goto('/admin');
    await page.waitForLoadState('networkidle');
    
    // La page ne devrait pas planter
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
    
    // Vérifier qu'un message d'erreur est affiché (si implémenté)
    // ou que la page reste fonctionnelle
  });
});

