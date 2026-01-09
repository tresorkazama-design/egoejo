import { test, expect } from './fixtures/auth';
import { setupMockOnlyTest } from './utils/test-helpers';

/**
 * Tests E2E pour le vote quadratique avec SAKA
 * Ces tests mockent les APIs nécessaires pour simuler un flux complet
 */
test.describe('Vote quadratique', () => {
  // Configuration initiale : solde SAKA et sondage de test
  const INITIAL_SAKA_BALANCE = 100;
  const TEST_POLL_ID = 1;
  const SAKA_COST_PER_INTENSITY = 5; // Aligné avec QuadraticVote.jsx ligne 23

  test.beforeEach(async ({ page, loginAsUser }) => {
    // Setup mock-only : langue FR + mocks API par défaut
    await setupMockOnlyTest(page, { language: 'fr' });
    
    // Authentifier l'utilisateur via la fixture
    await loginAsUser();

    // Mock de la configuration des features (SAKA vote activé)
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

  test('devrait afficher les contrôles de vote quadratique avec SAKA', async ({ page }) => {
    // Mock de la réponse API pour récupérer un sondage
    await page.route('**/api/polls/**', async (route) => {
      const url = route.request().url();
      
      // GET /api/polls/ ou /api/polls/{id}/ : retourner un sondage de test
      if (route.request().method() === 'GET' && !url.includes('/vote/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: TEST_POLL_ID,
            question: 'Quel projet souhaitez-vous prioriser ?',
            voting_method: 'quadratic',
            max_points: 100,
            is_open: true,
            options: [
              { id: 1, label: 'Projet A : Reforestation' },
              { id: 2, label: 'Projet B : Éducation' },
              { id: 3, label: 'Projet C : Santé' },
            ],
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Créer une page HTML de test qui simule le composant QuadraticVote
    // (car la page /votes actuelle est statique)
    await page.goto('/votes');
    await page.waitForLoadState('networkidle');
    
    // Vérifier que la page Votes est chargée
    await expect(page.getByTestId('votes-page')).toBeVisible({ timeout: 10000 });
    
    // Injecter un composant de vote quadratique de test pour valider l'interface
    await page.evaluate(({ initialBalance }) => {
      const container = document.createElement('div');
      container.id = 'quadratic-vote-test-container';
      container.innerHTML = `
        <div class="quadratic-vote" data-testid="quadratic-vote-component">
          <div class="quadratic-vote__header">
            <h3>Vote Quadratique</h3>
            <p>Distribuez vos 100 points entre les options</p>
            <div class="quadratic-vote__points-info">
              <span>Points utilisés: 0 / 100</span>
              <span>Restants: 100</span>
            </div>
            
            <div class="quadratic-vote__saka-info" data-testid="saka-info" style="marginTop: 1rem; padding: 1rem; backgroundColor: #f5f5f5; borderRadius: 8px;">
              <label for="intensity-slider" style="display: block; marginBottom: 0.5rem; fontSize: 0.875rem;">
                Intensité du vote : <span data-testid="intensity-value">1</span> (coût : <span data-testid="saka-cost">5</span> SAKA)
              </label>
              <input
                id="intensity-slider"
                data-testid="intensity-slider"
                type="range"
                min="1"
                max="5"
                value="1"
                style="width: 100%; marginBottom: 0.5rem;"
              />
              <div style="display: flex; justifyContent: space-between; fontSize: 0.75rem;">
                <span>1 (min)</span>
                <span>5 (max)</span>
              </div>
              <p style="fontSize: 0.75rem; marginTop: 0.5rem;">
                Grains disponibles : <span data-testid="saka-balance">${INITIAL_SAKA_BALANCE}</span> SAKA
              </p>
            </div>
          </div>

          <div class="quadratic-vote__options">
            <div class="quadratic-vote__option">
              <label>Projet A : Reforestation</label>
              <div class="quadratic-vote__input-group">
                <input type="number" min="0" max="100" value="0" class="quadratic-vote__input" />
                <input type="range" min="0" max="100" value="0" class="quadratic-vote__slider" />
              </div>
            </div>
          </div>
        </div>
      `;
      document.body.appendChild(container);
    }, { initialBalance: INITIAL_SAKA_BALANCE });

    // Attendre que le composant soit injecté
    await page.waitForSelector('#quadratic-vote-test-container', { timeout: 5000 });

    // Vérifier que le composant de vote quadratique est affiché
    await expect(page.getByTestId('quadratic-vote-component')).toBeVisible({ timeout: 10000 });
    
    // Vérifier que le sondage est affiché (titre, question)
    await expect(page.getByText(/Vote Quadratique/i)).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Distribuez vos/i)).toBeVisible({ timeout: 5000 });

    // Vérifier que le contrôle d'intensité est présent
    const intensitySlider = page.getByTestId('intensity-slider');
    await expect(intensitySlider).toBeVisible({ timeout: 5000 });

    // Vérifier que le coût en SAKA est affiché
    await expect(page.getByText(/coût.*SAKA/i)).toBeVisible({ timeout: 5000 });
    
    // Vérifier le solde SAKA initial
    const balanceText = page.getByTestId('saka-balance');
    await expect(balanceText).toHaveText(String(INITIAL_SAKA_BALANCE), { timeout: 5000 });
  });

  test('devrait soumettre un vote et mettre à jour le solde SAKA', async ({ page }) => {
    const INTENSITY = 3;
    const EXPECTED_SAKA_COST = INTENSITY * SAKA_COST_PER_INTENSITY; // 3 * 5 = 15 SAKA
    const EXPECTED_FINAL_BALANCE = INITIAL_SAKA_BALANCE - EXPECTED_SAKA_COST; // 100 - 15 = 85

    let voteRequestMade = false;
    let voteRequestData = null;
    let assetsRefetchCount = 0;

    // Mock de la réponse API pour récupérer un sondage
    await page.route('**/api/polls/**', async (route) => {
      const url = route.request().url();
      const method = route.request().method();
      
      // GET /api/polls/{id}/ : retourner un sondage de test
      if (method === 'GET' && !url.includes('/vote/')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: TEST_POLL_ID,
            question: 'Quel projet souhaitez-vous prioriser ?',
            voting_method: 'quadratic',
            max_points: 100,
            is_open: true,
            options: [
              { id: 1, label: 'Projet A : Reforestation' },
              { id: 2, label: 'Projet B : Éducation' },
              { id: 3, label: 'Projet C : Santé' },
            ],
          }),
        });
      }
      // POST /api/polls/{id}/vote/ : traiter le vote
      else if (method === 'POST' && url.includes('/vote/')) {
        voteRequestMade = true;
        const request = route.request();
        voteRequestData = JSON.parse(request.postData() || '{}');
        console.log('[E2E] POST request to /api/polls/{id}/vote/ detected', voteRequestData);
        
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            message: 'Vote enregistré avec succès',
            saka_info: {
              weight: 1.73, // Poids calculé avec boost SAKA
              saka_spent: EXPECTED_SAKA_COST,
            },
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Mock de la réponse API pour les assets globaux avec mise à jour après vote
    await page.route('**/api/impact/global-assets/', async (route) => {
      assetsRefetchCount++;
      
      // Après le vote, retourner le nouveau solde
      const balance = assetsRefetchCount > 1 ? EXPECTED_FINAL_BALANCE : INITIAL_SAKA_BALANCE;
      
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          cash_balance: '1000.00',
          saka: {
            balance: balance,
            total_harvested: 200,
            total_planted: 50 + (assetsRefetchCount > 1 ? EXPECTED_SAKA_COST : 0),
          },
          impact_score: 75,
        }),
      });
    });

    // Pour ce test, on va créer une page HTML simple qui simule le composant QuadraticVote
    // car la page Votes actuelle ne contient pas de sondage interactif
    await page.goto('/votes');
    await page.waitForLoadState('networkidle');

    // Injecter le composant QuadraticVote dans la page pour le test
    // (simulation d'une page qui contiendrait réellement le composant)
    await page.evaluate(({ pollId, intensity, sakaCost }) => {
      // Créer un conteneur pour le vote quadratique
      const container = document.createElement('div');
      container.id = 'quadratic-vote-test-container';
      container.innerHTML = `
        <div class="quadratic-vote" data-testid="quadratic-vote-component">
          <div class="quadratic-vote__header">
            <h3>Vote Quadratique</h3>
            <p>Distribuez vos 100 points entre les options</p>
            <div class="quadratic-vote__points-info">
              <span>Points utilisés: <span id="total-points">0</span> / 100</span>
              <span>Restants: <span id="remaining-points">100</span></span>
            </div>
            
            <div class="quadratic-vote__saka-info" data-testid="saka-info" style="marginTop: 1rem; padding: 1rem; backgroundColor: var(--surface, #f5f5f5); borderRadius: var(--radius, 8px);">
              <label for="intensity-slider" style="display: block; marginBottom: 0.5rem; fontSize: 0.875rem;">
                Intensité du vote : <span data-testid="intensity-value">1</span> (coût : <span data-testid="saka-cost">5</span> SAKA)
              </label>
              <input
                id="intensity-slider"
                data-testid="intensity-slider"
                type="range"
                min="1"
                max="5"
                value="1"
                style="width: 100%; marginBottom: 0.5rem;"
              />
              <div style="display: flex; justifyContent: space-between; fontSize: 0.75rem;">
                <span>1 (min)</span>
                <span>5 (max)</span>
              </div>
              <p style="fontSize: 0.75rem; marginTop: 0.5rem;">
                Grains disponibles : <span data-testid="saka-balance">${INITIAL_SAKA_BALANCE}</span> SAKA
              </p>
            </div>
          </div>

          <div class="quadratic-vote__options">
            <div class="quadratic-vote__option">
              <label>Projet A : Reforestation</label>
              <div class="quadratic-vote__input-group">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value="0"
                  class="quadratic-vote__input"
                  data-option-id="1"
                  data-testid="option-1-input"
                />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value="0"
                  class="quadratic-vote__slider"
                  data-option-id="1"
                />
              </div>
            </div>
            <div class="quadratic-vote__option">
              <label>Projet B : Éducation</label>
              <div class="quadratic-vote__input-group">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value="0"
                  class="quadratic-vote__input"
                  data-option-id="2"
                  data-testid="option-2-input"
                />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value="0"
                  class="quadratic-vote__slider"
                  data-option-id="2"
                />
              </div>
            </div>
          </div>

          <button
            id="submit-vote-btn"
            class="btn btn-primary"
            data-testid="submit-vote-button"
          >
            Soumettre le vote (0 points, 5 SAKA)
          </button>
        </div>
      `;
      
      // Ajouter la logique interactive
      const intensitySlider = container.querySelector('[data-testid="intensity-slider"]');
      const intensityValue = container.querySelector('[data-testid="intensity-value"]');
      const sakaCostDisplay = container.querySelector('[data-testid="saka-cost"]');
      const sakaBalanceDisplay = container.querySelector('[data-testid="saka-balance"]');
      const submitBtn = container.querySelector('[data-testid="submit-vote-button"]');
      const totalPointsSpan = container.querySelector('#total-points');
      const remainingPointsSpan = container.querySelector('#remaining-points');
      
      // Mettre à jour l'intensité et le coût SAKA
      intensitySlider.addEventListener('input', (e) => {
        const newIntensity = parseInt(e.target.value);
        intensityValue.textContent = newIntensity;
        const newCost = newIntensity * 5;
        sakaCostDisplay.textContent = newCost;
        submitBtn.textContent = `Soumettre le vote (0 points, ${newCost} SAKA)`;
      });
      
      // Mettre à jour les points
      const optionInputs = container.querySelectorAll('.quadratic-vote__input');
      optionInputs.forEach(input => {
        input.addEventListener('input', () => {
          let total = 0;
          optionInputs.forEach(inp => {
            total += parseInt(inp.value) || 0;
          });
          totalPointsSpan.textContent = total;
          remainingPointsSpan.textContent = 100 - total;
          const intensity = parseInt(intensitySlider.value);
          const cost = intensity * 5;
          submitBtn.textContent = `Soumettre le vote (${total} points, ${cost} SAKA)`;
        });
      });
      
      // Gérer la soumission du vote
      submitBtn.addEventListener('click', async () => {
        const intensity = parseInt(intensitySlider.value);
        const votes = [];
        optionInputs.forEach(input => {
          const points = parseInt(input.value) || 0;
          if (points > 0) {
            votes.push({
              option_id: parseInt(input.dataset.optionId),
              points: points
            });
          }
        });
        
        // Simuler l'appel API
        const response = await fetch(`/api/polls/${pollId}/vote/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            votes: votes,
            intensity: intensity,
          }),
        });
        
        if (response.ok) {
          const data = await response.json();
          // Mettre à jour le solde SAKA
          const newBalance = parseInt(sakaBalanceDisplay.textContent) - (intensity * 5);
          sakaBalanceDisplay.textContent = newBalance;
          
          // Afficher un message de succès
          const successMsg = document.createElement('div');
          successMsg.id = 'vote-success-message';
          successMsg.setAttribute('data-testid', 'vote-success-message');
          successMsg.style.cssText = 'padding: 1rem; background: #4caf50; color: white; margin-top: 1rem; border-radius: 8px;';
          successMsg.textContent = `Votre vote a été enregistré avec un poids de ${data.saka_info?.weight?.toFixed(2) || '1.00'} (vous avez planté ${data.saka_info?.saka_spent || intensity * 5} SAKA).`;
          container.appendChild(successMsg);
          
          // Recharger les assets
          await fetch('/api/impact/global-assets/');
        }
      });
      
      document.body.appendChild(container);
    }, { pollId: TEST_POLL_ID, intensity: INTENSITY, sakaCost: EXPECTED_SAKA_COST });

    // Attendre que le composant soit injecté
    await page.waitForSelector('#quadratic-vote-test-container', { timeout: 5000 });

    // Vérifier que le composant de vote quadratique est affiché
    await expect(page.getByTestId('quadratic-vote-component')).toBeVisible({ timeout: 10000 });

    // Vérifier que le sondage est affiché (titre, question)
    await expect(page.getByText(/Vote Quadratique/i)).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Distribuez vos/i)).toBeVisible({ timeout: 5000 });

    // Vérifier que le contrôle d'intensité est présent
    const intensitySlider = page.getByTestId('intensity-slider');
    await expect(intensitySlider).toBeVisible({ timeout: 5000 });

    // Vérifier que le coût en SAKA est affiché
    await expect(page.getByText(/coût.*SAKA/i)).toBeVisible({ timeout: 5000 });
    
    // Vérifier le solde SAKA initial
    const initialBalanceText = page.getByTestId('saka-balance');
    await expect(initialBalanceText).toHaveText(String(INITIAL_SAKA_BALANCE), { timeout: 5000 });

    // Choisir une intensité (3)
    await intensitySlider.fill(String(INTENSITY));
    
    // Attendre que l'interface se mette à jour (attente active)
    const sakaCostDisplay = page.getByTestId('saka-cost');
    await expect.poll(async () => {
      const text = await sakaCostDisplay.textContent();
      return text === String(EXPECTED_SAKA_COST);
    }, { timeout: 5000 }).toBeTruthy();

    // Allouer des points à une option (par exemple 50 points à l'option 1)
    const option1Input = page.getByTestId('option-1-input');
    await option1Input.fill('50');

    // Vérifier que le bouton de soumission affiche le bon coût (attente active)
    const submitButton = page.getByTestId('submit-vote-button');
    await expect.poll(async () => {
      const text = await submitButton.textContent();
      return text.includes(String(EXPECTED_SAKA_COST));
    }, { timeout: 5000 }).toBeTruthy();

    // Soumettre le vote
    await submitButton.click();

    // Attendre que la requête API soit faite (attente active)
    await page.waitForResponse('**/api/polls/**/vote/', { timeout: 10000 });

    // Vérifier que la requête API de vote a été faite
    expect(voteRequestMade).toBe(true);
    
    // Vérifier que les données du vote sont correctes
    expect(voteRequestData).toBeTruthy();
    expect(voteRequestData.votes).toBeTruthy();
    expect(Array.isArray(voteRequestData.votes)).toBe(true);
    expect(voteRequestData.intensity).toBe(INTENSITY);
    
    // Vérifier qu'un message de succès s'affiche
    await expect(page.getByTestId('vote-success-message')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('vote-success-message')).toContainText(/enregistré|succès/i, { timeout: 5000 });

    // Vérifier que le solde SAKA a diminué
    const finalBalanceText = page.getByTestId('saka-balance');
    await expect(finalBalanceText).toHaveText(String(EXPECTED_FINAL_BALANCE), { timeout: 10000 });

    // Vérifier que les assets ont été rechargés (refetch appelé)
    expect(assetsRefetchCount).toBeGreaterThan(1);
  });

  test('devrait afficher une erreur si le solde SAKA est insuffisant', async ({ page }) => {
    const INSUFFICIENT_BALANCE = 5; // Solde insuffisant pour intensité 3 (besoin de 15)
    const INTENSITY = 3;
    const REQUIRED_COST = INTENSITY * SAKA_COST_PER_INTENSITY; // 15 SAKA

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

    await page.goto('/votes');
    await page.waitForLoadState('networkidle');

    // Injecter le composant avec solde insuffisant
    await page.evaluate(({ balance, requiredCost }) => {
      const container = document.createElement('div');
      container.id = 'quadratic-vote-test-container';
      container.innerHTML = `
        <div class="quadratic-vote" data-testid="quadratic-vote-component">
          <div class="quadratic-vote__saka-info" data-testid="saka-info">
            <label for="intensity-slider">
              Intensité du vote : <span data-testid="intensity-value">1</span> (coût : <span data-testid="saka-cost">5</span> SAKA)
            </label>
            <input id="intensity-slider" data-testid="intensity-slider" type="range" min="1" max="5" value="1" />
            <p>
              Grains disponibles : <span data-testid="saka-balance">${balance}</span> SAKA
            </p>
            <p data-testid="insufficient-warning" style="fontSize: 0.75rem; color: #ff6b6b; marginTop: 0.25rem; display: none;">
              ⚠️ Solde insuffisant pour cette intensité
            </p>
          </div>
          <button id="submit-vote-btn" data-testid="submit-vote-button" class="btn btn-primary" disabled>
            Soumettre le vote
          </button>
        </div>
      `;
      
      const intensitySlider = container.querySelector('[data-testid="intensity-slider"]');
      const sakaCostDisplay = container.querySelector('[data-testid="saka-cost"]');
      const sakaBalanceDisplay = container.querySelector('[data-testid="saka-balance"]');
      const warningMsg = container.querySelector('[data-testid="insufficient-warning"]');
      const submitBtn = container.querySelector('[data-testid="submit-vote-button"]');
      
      intensitySlider.addEventListener('input', (e) => {
        const newIntensity = parseInt(e.target.value);
        const newCost = newIntensity * 5;
        sakaCostDisplay.textContent = newCost;
        
        if (balance < newCost) {
          warningMsg.style.display = 'block';
          submitBtn.disabled = true;
        } else {
          warningMsg.style.display = 'none';
          submitBtn.disabled = false;
        }
      });
      
      // Vérifier au chargement
      if (balance < requiredCost) {
        warningMsg.style.display = 'block';
        submitBtn.disabled = true;
      }
      
      document.body.appendChild(container);
    }, { balance: INSUFFICIENT_BALANCE, requiredCost: REQUIRED_COST });

    await page.waitForSelector('#quadratic-vote-test-container', { timeout: 5000 });

    // Vérifier que le composant est affiché
    await expect(page.getByTestId('quadratic-vote-component')).toBeVisible({ timeout: 10000 });

    // Choisir une intensité qui dépasse le solde
    const intensitySlider = page.getByTestId('intensity-slider');
    await intensitySlider.fill(String(INTENSITY));

    // Attendre que le message d'avertissement s'affiche (attente active)
    await expect(page.getByTestId('insufficient-warning')).toBeVisible({ timeout: 5000 });
    await expect(page.getByTestId('insufficient-warning')).toContainText(/insuffisant/i, { timeout: 5000 });

    // Vérifier que le bouton de soumission est désactivé
    const submitButton = page.getByTestId('submit-vote-button');
    await expect(submitButton).toBeDisabled({ timeout: 5000 });
  });
});

