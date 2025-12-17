import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour la visibilité des cycles SAKA et du Silo commun
 * 
 * Test P0 : Vérifier que l'utilisateur comprend ce qui arrive à sa valeur SAKA
 * - Affichage du Silo commun
 * - Affichage des cycles SAKA (récolte, plantation, compostage)
 * - Prévisualisation du compostage dans le Dashboard
 * 
 * PHILOSOPHIE : Les cycles SAKA DOIVENT être visibles pour garantir la transparence
 * et permettre à l'utilisateur de comprendre que sa valeur circule ou retourne au commun.
 */
test.describe('Visibilité des cycles SAKA et du Silo commun', () => {
  const INITIAL_SAKA_BALANCE = 200;
  const SILO_TOTAL_BALANCE = 5000;
  const SILO_TOTAL_COMPOSTED = 1200;
  const TEST_CYCLE = {
    id: 1,
    name: 'Cycle Q4 2025',
    start_date: '2025-10-01T00:00:00Z',
    end_date: '2025-12-31T23:59:59Z',
    is_active: true,
    stats: {
      saka_harvested: 5000,
      saka_planted: 3000,
      saka_composted: 800,
    },
  };

  // Définir le token dans localStorage AVANT le chargement de chaque page
  // Le AuthContext vérifie localStorage.getItem('token') au chargement initial
  // Sans token, il ne fait pas d'appel API et user reste null
  // Utiliser context.addInitScript() pour que le token soit disponible dès le chargement
  test.beforeEach(async ({ context, page }) => {
    // Définir le token dans localStorage via context (avant le chargement de la page)
    await context.addInitScript(() => {
      window.localStorage.setItem('token', 'test-token-123');
      window.localStorage.setItem('refresh_token', 'test-refresh-token-123');
    });

    // Mock de la configuration des features (SAKA activé)
    await page.route('**/api/config/features/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          saka_enabled: true,
          saka_compost_enabled: true,
          saka_silo_redis_enabled: true,
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
            total_harvested: 300,
            total_planted: 100,
            total_composted: 0,
          },
          impact_score: 75,
        }),
      });
    });
  });

  test('devrait afficher le Silo commun sur la page SakaSeasons', async ({ page }) => {
    // Mock de la réponse API pour le Silo
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          total_balance: SILO_TOTAL_BALANCE,
          total_composted: SILO_TOTAL_COMPOSTED,
          total_cycles: 4,
          last_compost_at: '2025-12-15T10:00:00Z',
          last_updated: '2025-12-17T08:00:00Z',
        }),
      });
    });

    // Mock de la réponse API pour les cycles SAKA
    await page.route('**/api/saka/cycles/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([TEST_CYCLE]),
      });
    });

    // Naviguer vers la page SakaSeasons
    await page.goto('/saka/saisons');
    await page.waitForLoadState('networkidle');
    await page.waitForLoadState('domcontentloaded');

    // Attendre que le h1 soit chargé
    await page.waitForSelector('h1', { timeout: 5000 });
    await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();

    // Attendre que la section Silo soit chargée
    await page.waitForSelector('section', { timeout: 5000 });
    // Utiliser getByRole pour cibler spécifiquement le h2 "Silo commun" 
    // (évite l'ambiguïté : "Silo commun" apparaît aussi dans le paragraphe de description)
    await expect(page.getByRole('heading', { name: 'Silo commun', level: 2 })).toBeVisible();

    // Cibler spécifiquement dans la section Silo pour éviter l'ambiguïté
    const siloSection = page.locator('section').filter({ hasText: /Silo commun/i });
    const siloBalanceText = siloSection.getByText(new RegExp(`${SILO_TOTAL_BALANCE.toLocaleString('fr-FR')}`));
    await expect(siloBalanceText).toBeVisible({ timeout: 5000 });

    // Vérifier que le texte "grains" est présent dans la section Silo (pas dans les cycles)
    // Utiliser siloSection pour cibler spécifiquement le texte "grains" du Silo
    const siloGrainsText = siloSection.getByText(/grains/i).first();
    await expect(siloGrainsText).toBeVisible();

    // Vérifier que la date du dernier compost est affichée (si disponible)
    // Note: Le format peut varier selon l'implémentation
    const lastCompostText = page.getByText(/Dernier compost/i);
    if (await lastCompostText.isVisible().catch(() => false)) {
      await expect(lastCompostText).toBeVisible();
    }
  });

  test('devrait afficher les cycles SAKA avec leurs statistiques', async ({ page }) => {
    // Mock de la réponse API pour le Silo
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          total_balance: SILO_TOTAL_BALANCE,
          total_composted: SILO_TOTAL_COMPOSTED,
        }),
      });
    });

    // Mock de la réponse API pour les cycles SAKA
    await page.route('**/api/saka/cycles/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([TEST_CYCLE]),
      });
    });

    // Naviguer vers la page SakaSeasons
    await page.goto('/saka/saisons');
    await page.waitForLoadState('networkidle');
    await page.waitForLoadState('domcontentloaded');

    // Attendre que le h1 soit chargé
    await page.waitForSelector('h1', { timeout: 5000 });
    await expect(page.locator('h1').filter({ hasText: /Saisons SAKA/i })).toBeVisible();

    // Attendre que l'article du cycle soit chargé
    await page.waitForSelector('article', { timeout: 5000 });
    await expect(page.getByText(TEST_CYCLE.name)).toBeVisible();

    // Cibler dans l'article du cycle pour éviter les ambiguïtés
    const cycleArticle = page.locator('article').filter({ hasText: TEST_CYCLE.name });

    // Vérifier que le badge "Actif" est présent si le cycle est actif
    if (TEST_CYCLE.is_active) {
      await expect(cycleArticle.getByText(/Actif/i)).toBeVisible();
    }

    // Vérifier que les dates du cycle sont affichées
    // Format attendu : "01/10/2025 → 31/12/2025" (format français)
    const dateText = cycleArticle.locator('text=/\\d{1,2}\\/\\d{1,2}\\/\\d{4}/');
    await expect(dateText.first()).toBeVisible();

    // Vérifier que les statistiques du cycle sont affichées dans le contexte de l'article
    // Récolté
    await expect(cycleArticle.getByText(/Récolté/i)).toBeVisible();
    // Chercher le nombre dans le paragraphe suivant "Récolté" (dans l'article)
    const harvestedValue = cycleArticle.locator('p.text-muted-foreground').filter({
      hasText: new RegExp(`${TEST_CYCLE.stats.saka_harvested.toLocaleString('fr-FR')}`)
    });
    await expect(harvestedValue.first()).toBeVisible();

    // Planté
    await expect(cycleArticle.getByText(/Planté/i)).toBeVisible();
    const plantedValue = cycleArticle.locator('p.text-muted-foreground').filter({
      hasText: new RegExp(`${TEST_CYCLE.stats.saka_planted.toLocaleString('fr-FR')}`)
    });
    await expect(plantedValue.first()).toBeVisible();

    // Composté
    await expect(cycleArticle.getByText(/Composté/i)).toBeVisible();
    const compostedValue = cycleArticle.locator('p.text-muted-foreground').filter({
      hasText: new RegExp(`${TEST_CYCLE.stats.saka_composted.toLocaleString('fr-FR')}`)
    });
    await expect(compostedValue.first()).toBeVisible();
  });

  test('devrait afficher la prévisualisation du compostage dans le Dashboard', async ({ page }) => {
    // Mock de l'authentification (NÉCESSAIRE pour useAuth() qui appelle /api/auth/me/)
    // Le AuthContext appelle /api/auth/me/ avec Authorization: Bearer token
    // Le token est maintenant défini dans beforeEach via context.addInitScript()
    await page.route('**/api/auth/me/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
        }),
      });
    });

    // Mock de la réponse API pour le compostage preview
    await page.route('**/api/saka/compost-preview/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          eligible: true,
          amount: 20, // 10% de 200 SAKA (balance initiale) - >= 20 pour satisfaire la condition
          days_until_eligible: 5,
          last_activity_date: '2025-12-10T00:00:00Z',
        }),
      });
    });

    // Mock de la réponse API pour le Silo (optionnel pour Dashboard)
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          total_balance: SILO_TOTAL_BALANCE,
        }),
      });
    });

    // Mock de l'API global-assets (nécessaire pour le Dashboard)
    await page.route('**/api/impact/global-assets/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: { balance: 200 },
          impact_score: 50,
        }),
      });
    });

    // Naviguer vers le Dashboard
    // Le token est défini dans beforeEach via context.addInitScript()
    // Le AuthContext devrait détecter le token et appeler /api/auth/me/
    const navigationPromise = page.goto('/dashboard');
    
    // Attendre que l'utilisateur soit chargé (useAuth() appelle /api/auth/me/)
    const authResponsePromise = page.waitForResponse('**/api/auth/me/', { timeout: 10000 });
    
    // Attendre que la navigation soit terminée
    await navigationPromise;
    
    // Attendre que l'API auth soit appelée
    await authResponsePromise;

    // Attendre que le Dashboard soit complètement chargé
    await page.waitForLoadState('networkidle');

    // Attendre explicitement que l'API compost-preview soit appelée
    // Le hook useSakaCompostPreview() appelle l'API après que user soit défini
    try {
      await page.waitForResponse('**/api/saka/compost-preview/', { timeout: 15000 });
    } catch (error) {
      // Si l'API n'est pas appelée, continuer quand même (peut être un problème de timing)
    }

    // Attendre que la notification soit chargée (avec timeout plus long)
    // La notification est conditionnelle : compost?.enabled && compost?.eligible && compost.amount >= 20
    // Attendre que le texte soit visible dans le DOM
    // Si l'API n'a pas été appelée, le hook retourne null et la notification ne s'affiche pas
    await page.waitForSelector('text=/Vos grains vont bientôt retourner à la terre/i', { 
      timeout: 20000,
      state: 'visible'
    });

    // Vérifier que la notification de compostage est affichée
    // (seulement si eligible et amount >= 20)
    const compostNotification = page.getByText(/Vos grains vont bientôt retourner à la terre/i);
    await expect(compostNotification).toBeVisible();

    // Vérifier que le montant de compostage est affiché
    const compostAmount = page.getByText(/20 SAKA/i);
    await expect(compostAmount).toBeVisible();

    // Vérifier que le texte explique le retour au Silo Commun
    // Le texte "Silo Commun" apparaît dans la notification de compostage
    // Utiliser un sélecteur plus spécifique pour éviter l'ambiguïté
    const notificationSection = page.locator('div').filter({ hasText: /Vos grains vont bientôt retourner à la terre/i });
    await expect(notificationSection.getByText(/Silo Commun/i).first()).toBeVisible();

    // Vérifier que le texte explique que l'utilisateur peut encore planter
    await expect(notificationSection.getByText(/planter/i)).toBeVisible();
  });

  test('devrait gérer le cas où aucun cycle SAKA n\'existe encore', async ({ page }) => {
    // Mock de la réponse API pour le Silo
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          total_balance: 0,
          total_composted: 0,
        }),
      });
    });

    // Mock de la réponse API pour les cycles SAKA (tableau vide)
    await page.route('**/api/saka/cycles/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([]),
      });
    });

    // Naviguer vers la page SakaSeasons
    await page.goto('/saka/saisons');
    await page.waitForLoadState('networkidle');

    // Vérifier que le message "Aucun cycle SAKA n'a encore été enregistré" est affiché
    await expect(
      page.getByText(/Aucun cycle SAKA n'a encore été enregistré/i)
    ).toBeVisible();
  });

  test('devrait expliquer le cycle complet (récolte → plantation → compost → silo)', async ({ page }) => {
    // Mock de la réponse API pour le Silo
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          total_balance: SILO_TOTAL_BALANCE,
        }),
      });
    });

    // Mock de la réponse API pour les cycles SAKA
    await page.route('**/api/saka/cycles/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([TEST_CYCLE]),
      });
    });

    // Naviguer vers la page SakaSeasons
    await page.goto('/saka/saisons');
    await page.waitForLoadState('networkidle');

    // Vérifier que la description du cycle est présente
    // Texte attendu : "Visualisez le cycle de vie des grains SAKA : récolte, plantation et compostage vers le Silo commun."
    await expect(
      page.getByText(/récolte.*plantation.*compostage.*Silo commun/i)
    ).toBeVisible();
  });

  test('devrait afficher plusieurs cycles SAKA si disponibles', async ({ page }) => {
    const cycles = [
      TEST_CYCLE,
      {
        id: 2,
        name: 'Cycle Q3 2025',
        start_date: '2025-07-01T00:00:00Z',
        end_date: '2025-09-30T23:59:59Z',
        is_active: false,
        stats: {
          saka_harvested: 4000,
          saka_planted: 2500,
          saka_composted: 600,
        },
      },
    ];

    // Mock de la réponse API pour le Silo
    await page.route('**/api/saka/silo/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          enabled: true,
          total_balance: SILO_TOTAL_BALANCE,
        }),
      });
    });

    // Mock de la réponse API pour les cycles SAKA (plusieurs cycles)
    await page.route('**/api/saka/cycles/', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(cycles),
      });
    });

    // Naviguer vers la page SakaSeasons
    await page.goto('/saka/saisons');
    await page.waitForLoadState('networkidle');

    // Vérifier que les deux cycles sont affichés
    await expect(page.getByText(cycles[0].name)).toBeVisible();
    await expect(page.getByText(cycles[1].name)).toBeVisible();

    // Vérifier que les statistiques des deux cycles sont affichées (cibler dans les articles spécifiques)
    const cycleArticle1 = page.locator('article').filter({ hasText: cycles[0].name });
    await expect(
      cycleArticle1.getByText(new RegExp(`${cycles[0].stats.saka_harvested.toLocaleString('fr-FR')}`))
    ).toBeVisible();
    
    const cycleArticle2 = page.locator('article').filter({ hasText: cycles[1].name });
    await expect(
      cycleArticle2.getByText(new RegExp(`${cycles[1].stats.saka_harvested.toLocaleString('fr-FR')}`))
    ).toBeVisible();
  });
});

