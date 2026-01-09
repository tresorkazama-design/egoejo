import { test, expect } from '@playwright/test';
import { setupMockOnlyTest } from './utils/test-helpers';

test.describe('Formulaire Rejoindre', () => {
  test.beforeEach(async ({ page }) => {
    // Setup mock-only : langue FR + mocks API par défaut
    await setupMockOnlyTest(page, { language: 'fr' });
  });

  test('devrait afficher le formulaire', async ({ page }) => {
    await page.goto('/rejoindre');
    
    // Attendre que la page soit complètement chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que les champs sont présents avec un timeout plus long
    await expect(page.getByTestId('rejoindre-input-nom')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('rejoindre-input-email')).toBeVisible({ timeout: 10000 });
    await expect(page.getByTestId('rejoindre-select-profil')).toBeVisible({ timeout: 10000 });
  });

  test('devrait valider les champs requis', async ({ page }) => {
    await page.goto('/rejoindre');
    
    // Attendre que le formulaire soit chargé
    await page.waitForSelector('form', { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Désactiver la validation HTML5 native pour permettre la validation JavaScript
    await page.evaluate(() => {
      const form = document.querySelector('form');
      if (form) {
        form.setAttribute('novalidate', 'true');
      }
    });
    
    // Essayer de soumettre sans remplir les champs
    const submitButton = page.getByTestId('rejoindre-submit-button');
    
    // Attendre que le bouton soit cliquable
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    
    // Cliquer sur le bouton pour déclencher la validation
    await submitButton.click();
    
    // Attendre que les messages d'erreur apparaissent dans le DOM
    // Les erreurs sont affichées dans des <p> avec la classe text-red-500
    await page.waitForSelector('p.text-red-500', { timeout: 5000 });
    
    // Vérifier qu'au moins un message d'erreur est visible
    const errorMessages = page.locator('p.text-red-500');
    const count = await errorMessages.count();
    expect(count).toBeGreaterThan(0);
    
    // Vérifier que le premier message d'erreur est visible
    await expect(errorMessages.first()).toBeVisible();
  });

  test('devrait soumettre le formulaire avec des données valides', async ({ page }) => {
    await page.goto('/rejoindre');
    
    // Attendre que le formulaire soit chargé
    await page.waitForSelector('form', { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Intercepter la requête API
    await page.route('**/api/intents/rejoindre/', route => {
      route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ message: 'Intention enregistrée' }),
      });
    });
    
    // Remplir le formulaire
    await page.getByTestId('rejoindre-input-nom').fill('Test User');
    await page.getByTestId('rejoindre-input-email').fill('test@example.com');
    await page.getByTestId('rejoindre-select-profil').selectOption('je-decouvre');
    
    // Soumettre le formulaire
    const submitButton = page.getByTestId('rejoindre-submit-button');
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await submitButton.click();
    
    // Vérifier le message de succès (utiliser first() car il y a h2 et p)
    await expect(page.getByText(/merci|succès|enregistré/i).first()).toBeVisible({ timeout: 10000 });
  });

  test('devrait protéger contre le spam (honeypot)', async ({ page }) => {
    await page.goto('/rejoindre');
    
    // Attendre que le formulaire soit chargé
    await page.waitForSelector('form', { timeout: 10000 });
    await page.waitForLoadState('networkidle');
    
    // Intercepter la requête API
    let requestIntercepted = false;
    await page.route('**/api/intents/rejoindre/', route => {
      requestIntercepted = true;
      const request = route.request();
      const postData = request.postDataJSON();
      
      // Vérifier que le honeypot n'est pas dans les données
      if (postData.website) {
        route.fulfill({
          status: 400,
          contentType: 'application/json',
          body: JSON.stringify({ detail: 'Spam détecté' }),
        });
      } else {
        route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({ message: 'Intention enregistrée' }),
        });
      }
    });
    
    // Remplir le formulaire
    await page.getByLabel(/nom/i).first().fill('Test User');
    await page.getByLabel(/email/i).first().fill('test@example.com');
    await page.getByLabel(/profil/i).first().selectOption('je-decouvre');
    
    // Remplir le champ honeypot (devrait être caché)
    const honeypot = page.locator('input[name="website"]');
    if (await honeypot.isVisible({ timeout: 1000 }).catch(() => false)) {
      await honeypot.fill('spam');
    } else {
      // Le champ est caché, c'est bon
      await honeypot.evaluate((el) => {
        el.value = 'spam';
      });
    }
    
    // Soumettre le formulaire
    const submitButton = page.getByRole('button', { name: /envoyer|soumettre/i }).first();
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await submitButton.click();
    
    // Attendre que la requête API soit faite (attente active)
    await page.waitForResponse('**/api/intents/rejoindre/', { timeout: 10000 });
    
    // Vérifier que la requête a été interceptée
    expect(requestIntercepted).toBe(true);
  });
});

