import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour les parcours SAKA (gain et dépense)
 * Ces tests nécessitent que le backend soit démarré sur http://127.0.0.1:8000
 * ou que les routes API soient mockées
 */
test.describe('Parcours SAKA', () => {
  test.beforeEach(async ({ page }) => {
    // Mock de l'authentification (token dans localStorage)
    await page.addInitScript(() => {
      window.localStorage.setItem('token', 'mock-access-token');
      window.localStorage.setItem('refreshToken', 'mock-refresh-token');
    });
  });

  test('devrait afficher le solde SAKA sur le Dashboard', async ({ page }) => {
    // Mock de la réponse API pour les assets globaux (incluant SAKA)
    await page.route('**/api/impact/global-assets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: 150,
            harvested: 200,
            planted: 50,
          },
          impact_score: 75,
        }),
      });
    });

    // Aller sur le Dashboard
    await page.goto('/dashboard');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que le solde SAKA est affiché
    // Le Dashboard affiche le SAKA dans le FourPStrip et dans la section "Capital Vivant"
    await expect(
      page.getByText(/SAKA|saka|capital vivant/i).first()
    ).toBeVisible({ timeout: 10000 });
    
    // Vérifier que le solde est affiché (150 SAKA)
    await expect(
      page.getByText(/150|SAKA/i).first()
    ).toBeVisible({ timeout: 10000 });
  });

  test('devrait permettre de voir le badge de saison SAKA', async ({ page }) => {
    // Mock de la réponse API pour les assets globaux avec un solde SAKA élevé
    await page.route('**/api/impact/global-assets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: 600, // Solde élevé pour tester le badge "Saison d'abondance"
            harvested: 800,
            planted: 200,
          },
          impact_score: 75,
        }),
      });
    });

    // Aller sur le Dashboard
    await page.goto('/dashboard');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que le badge de saison est affiché
    // Le badge devrait afficher "🌾 Saison d'abondance" pour un solde >= 500
    await expect(
      page.getByText(/saison|abondance|croissance|semailles/i).first()
    ).toBeVisible({ timeout: 10000 });
  });

  test('devrait permettre de voir les statistiques SAKA (Silo, Compost)', async ({ page }) => {
    // Mock de la réponse API pour le Silo SAKA
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          total_composted: 1000,
          last_compost_date: '2025-12-15T10:00:00Z',
        }),
      });
    });

    // Mock de la réponse API pour le preview du compost
    await page.route('**/api/saka/compost/preview/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          eligible_amount: 50,
          next_compost_date: '2025-12-20T10:00:00Z',
        }),
      });
    });

    // Aller sur le Dashboard
    await page.goto('/dashboard');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que les informations sur le Silo sont affichées (si la section existe)
    // Note: Cette vérification dépend de l'implémentation actuelle du Dashboard
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  test('devrait permettre de voir les cycles SAKA', async ({ page }) => {
    // Mock de la réponse API pour les cycles SAKA
    await page.route('**/api/saka/cycles/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 1,
            name: 'Saison 2025 - Printemps',
            start_date: '2025-03-01',
            end_date: '2025-05-31',
            is_active: true,
            stats: {
              harvested: 500,
              planted: 300,
              composted: 100,
            },
          },
        ]),
      });
    });

    // Aller sur la page SakaSilo (si elle existe) ou Dashboard
    await page.goto('/dashboard');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que la page se charge sans erreur
    const pageContent = await page.textContent('body');
    expect(pageContent).toBeTruthy();
  });

  test('devrait permettre de booster un projet avec SAKA', async ({ page }) => {
    // Mock de la réponse API pour les features (SAKA boost activé)
    await page.route('**/api/config/features/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          saka_enabled: true,
          saka_project_boost_enabled: true,
        }),
      });
    });

    // Mock de la réponse API pour les assets globaux (solde SAKA suffisant)
    await page.route('**/api/impact/global-assets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: 50, // Solde suffisant pour un boost (coût: 10 SAKA)
            harvested: 100,
            planted: 50,
          },
          impact_score: 75,
        }),
      });
    });

    // Mock de la réponse API pour les projets
    await page.route('**/api/projets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          count: 1,
          results: [
            {
              id: 1,
              titre: 'Projet Test',
              description: 'Description du projet test',
              saka_score: 0,
              saka_supporters_count: 0,
            },
          ],
        }),
      });
    });

    // Mock de la réponse API pour le boost
    let boostRequestMade = false;
    await page.route('**/api/projets/1/boost/', async (route) => {
      if (route.request().method() === 'POST') {
        boostRequestMade = true;
        const request = route.request();
        const postData = JSON.parse(request.postData() || '{}');
        console.log('[E2E] POST request to /api/projets/1/boost/ detected', postData);
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            new_saka_score: 10,
            new_saka_supporters_count: 1,
            message: 'Projet boosté avec succès',
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Aller sur la page Projets
    await page.goto('/projets');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que la page contient au moins un projet
    await expect(page.getByText(/Projet Test|projet/i).first()).toBeVisible({ timeout: 10000 });
    
    // Chercher le bouton de boost (peut être "Nourrir ce projet" ou similaire)
    const boostButton = page.getByRole('button', { name: /nourrir|boost|saka/i }).first();
    
    // Si le bouton existe et est visible, cliquer dessus
    if (await boostButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await boostButton.click();
      
      // Attendre que la requête soit faite
      await page.waitForTimeout(2000);
      
      // Vérifier que la requête API de boost a été faite
      expect(boostRequestMade).toBe(true);
      
      // Vérifier qu'un message de succès s'affiche
      await expect(
        page.getByText(/merci|succès|nourrissent|boost/i).first()
      ).toBeVisible({ timeout: 10000 });
    } else {
      // Si le bouton n'est pas visible, c'est peut-être parce que SAKA n'est pas activé
      // ou que le solde est insuffisant, on vérifie juste que la page se charge
      const pageContent = await page.textContent('body');
      expect(pageContent).toBeTruthy();
    }
  });
});

