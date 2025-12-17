import { test, expect } from '@playwright/test';

/**
 * Tests E2E pour l'authentification (inscription et connexion)
 */
test.describe('Authentification', () => {
  test('devrait permettre l\'inscription d\'un nouvel utilisateur', async ({ page }) => {
    // Intercepter la requête API d'inscription
    let apiRequestMade = false;
    let requestData = null;

    await page.route('**/api/auth/register/', async (route) => {
      if (route.request().method() === 'POST') {
        apiRequestMade = true;
        const request = route.request();
        requestData = request.postDataJSON();
        console.log('[E2E] POST request to /api/auth/register/ detected');
        await route.fulfill({
          status: 201,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            username: 'testuser',
            email: 'test@example.com',
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Aller sur la page d'inscription
    await page.goto('/register');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que le formulaire est présent
    await expect(page.getByLabel(/nom d'utilisateur|username/i).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByLabel(/email/i).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByLabel(/mot de passe|password/i).first()).toBeVisible({ timeout: 10000 });
    
    // Remplir le formulaire
    await page.getByLabel(/nom d'utilisateur|username/i).first().fill('testuser');
    await page.getByLabel(/email/i).first().fill('test@example.com');
    await page.getByLabel(/mot de passe|password/i).first().fill('testpassword123');
    
    // Si le champ de confirmation de mot de passe existe
    const passwordConfirm = page.getByLabel(/confirmer|confirm/i).first();
    if (await passwordConfirm.isVisible({ timeout: 2000 }).catch(() => false)) {
      await passwordConfirm.fill('testpassword123');
    }
    
    // Soumettre le formulaire
    const submitButton = page.getByRole('button', { name: /inscrire|s'inscrire|register|créer/i }).first();
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await submitButton.click();
    
    // Attendre que la requête soit faite
    await page.waitForTimeout(2000);
    
    // Vérifier que la requête API a été faite
    expect(apiRequestMade).toBe(true);
    
    // Vérifier que les données ont été envoyées
    if (requestData) {
      expect(requestData.username).toBe('testuser');
      expect(requestData.email).toBe('test@example.com');
    }
    
    // Vérifier qu'on est redirigé vers la page de connexion ou qu'un message de succès s'affiche
    await expect(
      page.getByText(/succès|merci|bienvenue|redirection|login|connexion/i).first()
    ).toBeVisible({ timeout: 10000 });
  });

  test('devrait permettre la connexion d\'un utilisateur existant', async ({ page }) => {
    // Intercepter la requête API de connexion
    let apiRequestMade = false;
    let requestData = null;

    await page.route('**/api/auth/login/', async (route) => {
      if (route.request().method() === 'POST') {
        apiRequestMade = true;
        const request = route.request();
        requestData = request.postDataJSON();
        console.log('[E2E] POST request to /api/auth/login/ detected');
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            access: 'mock-access-token',
            refresh: 'mock-refresh-token',
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Aller sur la page de connexion
    await page.goto('/login');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Vérifier que le formulaire est présent
    await expect(page.getByLabel(/nom d'utilisateur|username|email/i).first()).toBeVisible({ timeout: 10000 });
    await expect(page.getByLabel(/mot de passe|password/i).first()).toBeVisible({ timeout: 10000 });
    
    // Remplir le formulaire
    await page.getByLabel(/nom d'utilisateur|username|email/i).first().fill('testuser');
    await page.getByLabel(/mot de passe|password/i).first().fill('testpassword123');
    
    // Soumettre le formulaire
    const submitButton = page.getByRole('button', { name: /connexion|se connecter|login|connecter/i }).first();
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await submitButton.click();
    
    // Attendre que la requête soit faite
    await page.waitForTimeout(2000);
    
    // Vérifier que la requête API a été faite
    expect(apiRequestMade).toBe(true);
    
    // Vérifier que les données ont été envoyées
    if (requestData) {
      expect(requestData.username || requestData.email).toBeTruthy();
      expect(requestData.password).toBeTruthy();
    }
    
    // Vérifier qu'un message de succès s'affiche ou qu'on est redirigé
    await expect(
      page.getByText(/succès|bienvenue|redirection|accueil/i).first()
    ).toBeVisible({ timeout: 10000 });
  });

  test('devrait afficher une erreur si les identifiants sont incorrects', async ({ page }) => {
    // Intercepter la requête API de connexion avec une erreur
    await page.route('**/api/auth/login/', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 401,
          contentType: 'application/json',
          body: JSON.stringify({
            detail: 'Identifiants incorrects',
          }),
        });
      } else {
        await route.continue();
      }
    });

    // Aller sur la page de connexion
    await page.goto('/login');
    
    // Attendre que la page soit chargée
    await page.waitForLoadState('networkidle');
    
    // Remplir le formulaire avec des identifiants incorrects
    await page.getByLabel(/nom d'utilisateur|username|email/i).first().fill('wronguser');
    await page.getByLabel(/mot de passe|password/i).first().fill('wrongpassword');
    
    // Soumettre le formulaire
    const submitButton = page.getByRole('button', { name: /connexion|se connecter|login/i }).first();
    await submitButton.waitFor({ state: 'visible', timeout: 10000 });
    await submitButton.click();
    
    // Attendre que l'erreur s'affiche
    await page.waitForTimeout(2000);
    
    // Vérifier qu'un message d'erreur est affiché
    await expect(
      page.getByText(/erreur|incorrect|échec|invalid/i).first()
    ).toBeVisible({ timeout: 10000 });
  });
});

