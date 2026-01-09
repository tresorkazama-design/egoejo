/**
 * Tests E2E BLOQUANTS - Violations SAKA/EUR
 * 
 * Ces tests échouent si :
 * 1. Un symbole monétaire "€" apparaît dans un écran SAKA (hors zones explicitement EUR)
 * 2. Un texte suggère conversion / échange SAKA↔EUR
 * 3. Un composant affiche SAKA et EUR sans disclaimer/badge "non monétaire"
 * 
 * TAG : @critical - Tests BLOQUANTS pour la Constitution EGOEJO
 * TAG : @egoejo_compliance - Tests de compliance Constitution EGOEJO
 * 
 * Ces tests doivent être exécutés avec le backend réel pour vérifier l'UI complète.
 */

import { test, expect } from '@playwright/test';
import { waitForApiIdle } from './utils/test-helpers';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';
const API_BASE = `${BACKEND_URL}/api`;

/**
 * Helper pour créer un utilisateur et obtenir un token
 */
async function createAndLoginUser(page, username, email, password) {
  // Créer l'utilisateur
  const registerResponse = await page.request.post(`${API_BASE}/auth/register/`, {
    data: { username, email, password, first_name: 'Test', last_name: 'User' },
  });
  
  if (registerResponse.status() !== 201) {
    const errorText = await registerResponse.text();
    throw new Error(`Échec création utilisateur: ${registerResponse.status()} - ${errorText}`);
  }
  
  // Login
  const loginResponse = await page.request.post(`${API_BASE}/auth/login/`, {
    data: { username, password },
  });
  
  if (loginResponse.status() !== 200) {
    const errorText = await loginResponse.text();
    throw new Error(`Échec login: ${loginResponse.status()} - ${errorText}`);
  }
  
  const tokenData = await loginResponse.json();
  return tokenData.access;
}

/**
 * Helper pour créditer du SAKA (si endpoint test-only disponible)
 */
async function grantSaka(page, token, amount) {
  try {
    const response = await page.request.post(`${API_BASE}/saka/grant/`, {
      headers: { 'Authorization': `Bearer ${token}` },
      data: { amount, reason: 'e2e_test' },
    });
    
    if (response.status() === 200 || response.status() === 201) {
      return await response.json();
    }
  } catch (error) {
    // Endpoint non disponible, on continue sans crédit SAKA
  }
  return { ok: false };
}

test.describe('Violations SAKA/EUR - Tests BLOQUANTS', () => {
  test.describe.configure({ mode: 'serial' });
  
  let userToken;
  let testUsername;
  
  test.beforeAll(async ({ browser }) => {
    // Vérifier que le backend est accessible
    const page = await browser.newPage();
    try {
      const healthCheck = await page.request.get(`${BACKEND_URL}/api/health/`).catch(() => 
        page.request.get(`${BACKEND_URL}/`)
      );
      
      if (healthCheck.status() >= 400) {
        throw new Error(`Backend répond avec status ${healthCheck.status()}`);
      }
    } catch (error) {
      throw new Error(
        `Backend non accessible à ${BACKEND_URL}. ` +
        `Assurez-vous que le backend Django est démarré.`
      );
    }
    await page.close();
  });
  
  test.beforeEach(async ({ page }) => {
    // Créer un utilisateur unique pour chaque test
    const timestamp = Date.now();
    testUsername = `test_violation_${timestamp}`;
    const testEmail = `test_violation_${timestamp}@e2e.test`;
    const testPassword = 'testpass123';
    
    userToken = await createAndLoginUser(page, testUsername, testEmail, testPassword);
    
    // Créditer du SAKA pour les tests
    await grantSaka(page, userToken, 100);
    
    // Configurer l'authentification dans le navigateur
    await page.addInitScript(({ token }) => {
      window.localStorage.setItem('token', token);
      window.localStorage.setItem('refresh_token', 'mock-refresh-token');
    }, { token: userToken });
  });
  
  test('VIOLATION 1: Aucun symbole "€" dans un écran SAKA (hors zones explicitement EUR)', async ({ page }) => {
    /**
     * Test BLOQUANT : Vérifie qu'aucun symbole "€" n'apparaît dans les écrans SAKA
     * (sauf dans les zones explicitement EUR comme le dashboard financier)
     * 
     * Constitution EGOEJO: SAKA et EUR doivent être strictement séparés visuellement.
     */
    
    // Pages SAKA à vérifier (sans zones EUR)
    const sakaPages = [
      { path: '/votes', description: 'Page Votes (vote quadratique SAKA)' },
      { path: '/impact', description: 'Page Impact (affichage SAKA)' },
    ];
    
    for (const { path, description } of sakaPages) {
      console.log(`[E2E] 🔍 Vérification ${description} (${path})`);
      
      await page.goto(path);
      await waitForApiIdle(page, { timeout: 30000 });
      
      // Attendre que la page soit chargée
      await page.waitForLoadState('networkidle');
      
      // Récupérer tout le contenu texte de la page
      const pageContent = await page.textContent('body');
      const pageHTML = await page.content();
      
      // Identifier les zones explicitement EUR (si présentes)
      // Ces zones peuvent contenir "€" sans violation
      const eurZones = page.locator('[data-testid*="eur"], [data-testid*="euro"], [data-testid*="wallet"], [data-testid*="finance"]');
      const eurZonesCount = await eurZones.count();
      
      // Extraire le texte des zones EUR (si présentes)
      let eurZonesText = '';
      if (eurZonesCount > 0) {
        for (let i = 0; i < eurZonesCount; i++) {
          const zoneText = await eurZones.nth(i).textContent().catch(() => '');
          eurZonesText += zoneText + ' ';
        }
      }
      
      // Chercher "€" dans le contenu de la page
      const euroSymbolMatches = (pageContent.match(/€/g) || []).length;
      
      // Si des zones EUR existent, soustraire les "€" de ces zones
      const eurZonesEuroMatches = (eurZonesText.match(/€/g) || []).length;
      const sakaZonesEuroMatches = euroSymbolMatches - eurZonesEuroMatches;
      
      if (sakaZonesEuroMatches > 0) {
        // Trouver les contextes où "€" apparaît (pour diagnostic)
        const euroContexts = [];
        const regex = /[^€]*€[^€]*/g;
        let match;
        while ((match = regex.exec(pageContent)) !== null) {
          const context = match[0].trim().substring(0, 100);
          // Vérifier si ce contexte est dans une zone EUR
          if (!eurZonesText.includes(context)) {
            euroContexts.push(context);
          }
        }
        
        throw new Error(
          `BLOQUANT : Symbole "€" détecté dans un écran SAKA (${description}).\n` +
          `Nombre de violations: ${sakaZonesEuroMatches}\n` +
          `Contexte(s) de violation:\n${euroContexts.slice(0, 5).join('\n')}\n\n` +
          `Constitution EGOEJO: SAKA et EUR doivent être strictement séparés visuellement.\n` +
          `Les écrans SAKA ne doivent pas afficher de symbole "€" (sauf dans les zones explicitement EUR).`
        );
      }
      
      console.log(`[E2E] ✅ Aucun symbole "€" détecté dans ${description}`);
    }
  });
  
  test('VIOLATION 2: Aucun texte suggérant conversion/échange SAKA↔EUR', async ({ page }) => {
    /**
     * Test BLOQUANT : Vérifie qu'aucun texte ne suggère de conversion ou échange SAKA↔EUR
     * 
     * Constitution EGOEJO: Aucune conversion SAKA ↔ EUR n'est autorisée.
     */
    
    // Pages à vérifier
    const pagesToCheck = [
      { path: '/votes', description: 'Page Votes' },
      { path: '/impact', description: 'Page Impact' },
      { path: '/projets', description: 'Page Projets' },
      { path: '/', description: 'Page Accueil' },
    ];
    
    const forbiddenPatterns = [
      /convertir.*saka.*eur|convertir.*eur.*saka/i,
      /saka.*to.*eur|eur.*to.*saka/i,
      /saka.*en.*eur|eur.*en.*saka/i,
      /échanger.*saka.*eur|échanger.*eur.*saka/i,
      /exchange.*saka.*eur|exchange.*eur.*saka/i,
      /taux.*saka.*eur|taux.*eur.*saka|rate.*saka.*eur|rate.*eur.*saka/i,
      /équivalent.*saka.*eur|équivalent.*eur.*saka|equivalent.*saka.*eur|equivalent.*eur.*saka/i,
      /1.*saka.*=.*\d+.*eur|\d+.*eur.*=.*1.*saka/i,
      /saka.*vaut.*eur|eur.*vaut.*saka|saka.*worth.*eur|eur.*worth.*saka/i,
      /prix.*saka|price.*saka|valeur.*saka.*eur|value.*saka.*eur/i,
    ];
    
    for (const { path, description } of pagesToCheck) {
      console.log(`[E2E] 🔍 Vérification ${description} (${path})`);
      
      await page.goto(path);
      await waitForApiIdle(page, { timeout: 30000 });
      await page.waitForLoadState('networkidle');
      
      // Récupérer tout le contenu texte de la page
      const pageContent = await page.textContent('body');
      const pageHTML = await page.content();
      
      // Vérifier chaque pattern interdit
      for (const pattern of forbiddenPatterns) {
        const matches = pageContent.match(pattern);
        if (matches && matches.length > 0) {
          // Trouver le contexte de la violation
          const matchIndex = pageContent.search(pattern);
          const contextStart = Math.max(0, matchIndex - 50);
          const contextEnd = Math.min(pageContent.length, matchIndex + 100);
          const context = pageContent.substring(contextStart, contextEnd).trim();
          
          throw new Error(
            `BLOQUANT : Texte suggérant conversion/échange SAKA↔EUR détecté (${description}).\n` +
            `Pattern interdit: ${pattern.source}\n` +
            `Contexte de violation: "${context}"\n\n` +
            `Constitution EGOEJO: Aucune conversion SAKA ↔ EUR n'est autorisée.\n` +
            `Aucun texte ne doit suggérer de conversion ou d'échange entre SAKA et EUR.`
          );
        }
      }
      
      console.log(`[E2E] ✅ Aucun texte de conversion détecté dans ${description}`);
    }
  });
  
  test('VIOLATION 3: Composant SAKA/EUR doit avoir disclaimer/badge "non monétaire"', async ({ page }) => {
    /**
     * Test BLOQUANT : Vérifie que tout composant affichant SAKA et EUR ensemble
     * doit avoir un disclaimer/badge "non monétaire"
     * 
     * Constitution EGOEJO: SAKA doit être clairement identifié comme non monétaire.
     */
    
    // Pages où SAKA et EUR peuvent être affichés ensemble
    const pagesToCheck = [
      { path: '/impact', description: 'Page Impact (affichage SAKA + patrimoine EUR)' },
      { path: '/dashboard', description: 'Page Dashboard (affichage SAKA + liquidités EUR)' },
    ];
    
    for (const { path, description } of pagesToCheck) {
      console.log(`[E2E] 🔍 Vérification ${description} (${path})`);
      
      await page.goto(path);
      await waitForApiIdle(page, { timeout: 30000 });
      await page.waitForLoadState('networkidle');
      
      // Vérifier si SAKA et EUR sont présents sur la page
      const pageContent = await page.textContent('body');
      const hasSaka = /SAKA|saka/i.test(pageContent);
      const hasEur = /€|EUR|euro/i.test(pageContent);
      
      if (hasSaka && hasEur) {
        // SAKA et EUR sont présents ensemble - vérifier le disclaimer/badge
        const disclaimerPatterns = [
          /non.*monétaire|non-monétaire|non monétaire/i,
          /non.*monetary|non-monetary/i,
          /relationnel|relational/i,
          /instrumental/i,
        ];
        
        // Chercher le disclaimer/badge
        const hasDisclaimer = disclaimerPatterns.some(pattern => pattern.test(pageContent));
        
        // Chercher aussi dans les attributs data-testid ou aria-label
        const disclaimerElements = page.locator(
          '[data-testid*="non-monetaire"], [data-testid*="non-monetary"], ' +
          '[aria-label*="non monétaire"], [aria-label*="non monetary"], ' +
          '[title*="non monétaire"], [title*="non monetary"]'
        );
        const disclaimerCount = await disclaimerElements.count();
        
        if (!hasDisclaimer && disclaimerCount === 0) {
          throw new Error(
            `BLOQUANT : Composant affichant SAKA et EUR sans disclaimer/badge "non monétaire" (${description}).\n` +
            `La page contient à la fois SAKA et EUR mais aucun disclaimer/badge "non monétaire" n'est présent.\n\n` +
            `Constitution EGOEJO: SAKA doit être clairement identifié comme non monétaire.\n` +
            `Tout composant affichant SAKA et EUR ensemble doit avoir un disclaimer/badge "non monétaire".`
          );
        }
        
        console.log(`[E2E] ✅ Disclaimer/badge "non monétaire" présent dans ${description}`);
      } else {
        console.log(`[E2E] ℹ️ SAKA et EUR ne sont pas présents ensemble dans ${description} (pas de vérification nécessaire)`);
      }
    }
  });
});

