import { test, expect } from './fixtures/auth';
import { setupMockOnlyTest } from './utils/test-helpers';

/**
 * Tests E2E pour le boost SAKA d'un projet
 * Parcours : va sur /projets, sélectionne un projet, clique sur "Booster / Semer du SAKA",
 * confirme, voit le score SAKA du projet augmenter.
 */
test.describe('Boost SAKA d\'un projet', () => {
  const INITIAL_SAKA_BALANCE = 100;
  const SAKA_BOOST_COST = 10;
  const EXPECTED_FINAL_BALANCE = INITIAL_SAKA_BALANCE - SAKA_BOOST_COST;
  const TEST_PROJECT_ID = 1;
  const INITIAL_SAKA_SCORE = 50;
  const EXPECTED_NEW_SAKA_SCORE = INITIAL_SAKA_SCORE + SAKA_BOOST_COST;

  test.beforeEach(async ({ page, loginAsUser }) => {
    // Setup mock-only : langue FR + mocks API par défaut
    await setupMockOnlyTest(page, { language: 'fr' });
    
    // Authentifier l'utilisateur via la fixture
    await loginAsUser();

    // Mock de la configuration des features (SAKA boost activé)
    await page.route('**/api/config/features/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          saka_enabled: true,
          saka_vote_enabled: true,
          saka_project_boost_enabled: true,
        }),
      });
    });

    // Mock de la réponse API pour les assets globaux (solde SAKA initial)
    await page.route('**/api/impact/global-assets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: INITIAL_SAKA_BALANCE,
            total_harvested: 200,
            total_planted: 50,
          },
          impact_score: 75,
        }),
      });
    });
  });

  test('devrait afficher la liste des projets avec les boutons de boost SAKA', async ({ page }) => {
    // Mock de la réponse API pour les projets
    await page.route('**/api/projets/', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: TEST_PROJECT_ID,
                titre: 'Projet Test - Reforestation',
                description: 'Un projet de reforestation pour restaurer la biodiversité',
                contenu: 'Description détaillée du projet...',
                saka_score: INITIAL_SAKA_SCORE,
                saka_supporters_count: 5,
                impact_4p: {
                  p1_financier: 1000,
                  p2_saka: INITIAL_SAKA_SCORE,
                  p3_social: 75,
                  p4_sens: 80,
                },
              },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.goto('/projets');
    await page.waitForLoadState('networkidle');

    // Vérifier que la page Projets est chargée
    await expect(page.getByTestId('projets-page')).toBeVisible({ timeout: 10000 });

    // Vérifier que le projet est affiché
    await expect(page.getByText('Projet Test - Reforestation')).toBeVisible({ timeout: 10000 });

    // Vérifier que le score SAKA est affiché
    await expect(page.getByText(new RegExp(`Soutien SAKA.*${INITIAL_SAKA_SCORE}.*grains`, 'i'))).toBeVisible({ timeout: 5000 });

    // Vérifier que le bouton de boost est présent et activé
    const boostButton = page.getByRole('button', { name: new RegExp(`Nourrir.*${SAKA_BOOST_COST}.*SAKA`, 'i') });
    await expect(boostButton).toBeVisible({ timeout: 5000 });
    await expect(boostButton).toBeEnabled();
  });

  test('devrait booster un projet avec SAKA et voir le score augmenter', async ({ page }) => {
    let boostRequestMade = false;
    let boostRequestData = null;
    let assetsRefetchCount = 0;

    // Mock de la réponse API pour les projets
    await page.route('**/api/projets/', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: TEST_PROJECT_ID,
                titre: 'Projet Test - Reforestation',
                description: 'Un projet de reforestation',
                contenu: 'Description détaillée...',
                saka_score: INITIAL_SAKA_SCORE,
                saka_supporters_count: 5,
                impact_4p: {
                  p1_financier: 1000,
                  p2_saka: INITIAL_SAKA_SCORE,
                  p3_social: 75,
                  p4_sens: 80,
                },
              },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock de la réponse API pour le boost SAKA
    await page.route(`**/api/projets/${TEST_PROJECT_ID}/boost/`, async (route) => {
      if (route.request().method() === 'POST') {
        boostRequestMade = true;
        const request = route.request();
        boostRequestData = request.postDataJSON();
        console.log('[E2E] POST request to /api/projets/{id}/boost/ detected');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Projet boosté avec succès',
            new_saka_score: EXPECTED_NEW_SAKA_SCORE,
            new_saka_supporters_count: 6,
            saka_spent: SAKA_BOOST_COST,
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock de la réponse API pour les assets globaux avec mise à jour après boost
    await page.route('**/api/impact/global-assets/', async (route) => {
      assetsRefetchCount++;
      
      // Après le boost, retourner le nouveau solde
      const balance = assetsRefetchCount > 1 ? EXPECTED_FINAL_BALANCE : INITIAL_SAKA_BALANCE;
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: balance,
            total_harvested: 200,
            total_planted: 50 + (assetsRefetchCount > 1 ? SAKA_BOOST_COST : 0),
          },
          impact_score: 75,
        }),
      });
    });

    await page.goto('/projets');
    await page.waitForLoadState('networkidle');

    // Vérifier que la page est chargée
    await expect(page.getByTestId('projets-page')).toBeVisible({ timeout: 10000 });

    // Vérifier le score SAKA initial
    const initialScoreText = page.getByText(new RegExp(`Soutien SAKA.*${INITIAL_SAKA_SCORE}.*grains`, 'i'));
    await expect(initialScoreText).toBeVisible({ timeout: 5000 });

    // Cliquer sur le bouton "Nourrir ce projet"
    const boostButton = page.getByRole('button', { name: new RegExp(`Nourrir.*${SAKA_BOOST_COST}.*SAKA`, 'i') });
    await expect(boostButton).toBeVisible({ timeout: 5000 });
    await boostButton.click();

    // Attendre que la requête API soit faite (attente active)
    await page.waitForResponse('**/api/projets/**/boost/', { timeout: 10000 });

    // Vérifier que la requête API a été faite avec les bons paramètres
    expect(boostRequestMade).toBe(true);
    if (boostRequestData) {
      expect(boostRequestData.amount).toBe(SAKA_BOOST_COST);
    }

    // Vérifier que le score SAKA a été mis à jour dans l'affichage
    // (le composant devrait mettre à jour le score après la réponse API)
    const newScoreText = page.getByText(new RegExp(`Soutien SAKA.*${EXPECTED_NEW_SAKA_SCORE}.*grains`, 'i'));
    await expect(newScoreText).toBeVisible({ timeout: 10000 });

    // Vérifier qu'une notification de succès est affichée
    const successNotification = page.getByText(/merci.*saka.*nourrissent|projet.*boosté/i);
    await expect(successNotification).toBeVisible({ timeout: 5000 });

    // Vérifier que le nombre de supporters a augmenté (si affiché)
    const supportersText = page.getByText(new RegExp(`Soutenu par.*6.*membre`, 'i'));
    if (await supportersText.isVisible({ timeout: 2000 }).catch(() => false)) {
      await expect(supportersText).toBeVisible();
    }
  });

  test('devrait désactiver le bouton de boost si le solde SAKA est insuffisant', async ({ page }) => {
    const INSUFFICIENT_BALANCE = 5; // Moins que le coût de 10 SAKA

    // Mock de la réponse API pour les assets globaux avec solde insuffisant
    await page.route('**/api/impact/global-assets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: INSUFFICIENT_BALANCE,
            total_harvested: 200,
            total_planted: 50,
          },
          impact_score: 75,
        }),
      });
    });

    // Mock de la réponse API pour les projets
    await page.route('**/api/projets/', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: TEST_PROJECT_ID,
                titre: 'Projet Test - Reforestation',
                description: 'Un projet de reforestation',
                contenu: 'Description détaillée...',
                saka_score: INITIAL_SAKA_SCORE,
                saka_supporters_count: 5,
                impact_4p: {
                  p1_financier: 1000,
                  p2_saka: INITIAL_SAKA_SCORE,
                  p3_social: 75,
                  p4_sens: 80,
                },
              },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.goto('/projets');
    await page.waitForLoadState('networkidle');

    // Vérifier que la page est chargée
    await expect(page.getByTestId('projets-page')).toBeVisible({ timeout: 10000 });

    // Vérifier que le bouton de boost est désactivé
    const boostButton = page.getByRole('button', { name: new RegExp(`Nourrir.*${SAKA_BOOST_COST}.*SAKA`, 'i') });
    await expect(boostButton).toBeVisible({ timeout: 5000 });
    await expect(boostButton).toBeDisabled();
  });

  test('devrait afficher une erreur si le boost échoue (ex: solde insuffisant côté serveur)', async ({ page }) => {
    // Mock de la réponse API pour les projets
    await page.route('**/api/projets/', async (route) => {
      if (route.request().method() === 'GET') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            results: [
              {
                id: TEST_PROJECT_ID,
                titre: 'Projet Test - Reforestation',
                description: 'Un projet de reforestation',
                contenu: 'Description détaillée...',
                saka_score: INITIAL_SAKA_SCORE,
                saka_supporters_count: 5,
                impact_4p: {
                  p1_financier: 1000,
                  p2_saka: INITIAL_SAKA_SCORE,
                  p3_social: 75,
                  p4_sens: 80,
                },
              },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock de la réponse API pour le boost SAKA avec erreur
    await page.route(`**/api/projets/${TEST_PROJECT_ID}/boost/`, async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({
            error: 'Solde SAKA insuffisant',
            detail: 'Vous avez 100 SAKA, mais il en faut 10 pour booster ce projet.',
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.goto('/projets');
    await page.waitForLoadState('networkidle');

    // Vérifier que la page est chargée
    await expect(page.getByTestId('projets-page')).toBeVisible({ timeout: 10000 });

    // Cliquer sur le bouton "Nourrir ce projet"
    const boostButton = page.getByRole('button', { name: new RegExp(`Nourrir.*${SAKA_BOOST_COST}.*SAKA`, 'i') });
    await expect(boostButton).toBeVisible({ timeout: 5000 });
    await boostButton.click();

    // Attendre que l'erreur soit affichée (attente active)
    await expect(page.getByText(/solde.*insuffisant|erreur.*boost|insufficient|error/i)).toBeVisible({ timeout: 5000 });
    const errorMessage = page.getByText(/solde.*insuffisant|erreur.*boost/i);
    await expect(errorMessage).toBeVisible({ timeout: 5000 });

    // Vérifier que le score SAKA n'a pas changé
    const scoreText = page.getByText(new RegExp(`Soutien SAKA.*${INITIAL_SAKA_SCORE}.*grains`, 'i'));
    await expect(scoreText).toBeVisible({ timeout: 5000 });
  });
});

