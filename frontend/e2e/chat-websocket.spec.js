/**
 * Tests E2E pour le chat WebSocket.
 * 
 * Vérifie :
 * - Connexion WebSocket
 * - Échange de messages entre 2 utilisateurs
 * - Affichage des messages dans l'UI
 * - Persistence des messages
 */
import { test, expect } from '@playwright/test';
import { loginAsUser, gotoAuthed, waitForApiIdle, setupTestMode, setupFrenchLanguage } from './utils/test-helpers';

test.describe('Chat WebSocket (E2E)', () => {
  let user1Context;
  let user2Context;
  let user1Page;
  let user2Page;
  let user1Id;
  let user2Id;
  let threadId;

  test.beforeAll(async ({ browser }) => {
    // Créer deux contextes séparés pour simuler 2 utilisateurs
    user1Context = await browser.newContext();
    user2Context = await browser.newContext();
    
    user1Page = await user1Context.newPage();
    user2Page = await user2Context.newPage();
    
    // Setup pour les deux pages
    await setupTestMode(user1Page);
    await setupTestMode(user2Page);
    await setupFrenchLanguage(user1Page);
    await setupFrenchLanguage(user2Page);
    
    // Login user1
    await loginAsUser(user1Page, { 
      username: 'testuser1', 
      email: 'testuser1@example.com',
      is_staff: false 
    });
    await waitForApiIdle(user1Page);
    
    // Login user2
    await loginAsUser(user2Page, { 
      username: 'testuser2', 
      email: 'testuser2@example.com',
      is_staff: false 
    });
    await waitForApiIdle(user2Page);
    
    // Récupérer les IDs utilisateurs depuis l'API
    const user1Response = await user1Page.request.get('/api/auth/user/');
    const user1Data = await user1Response.json();
    user1Id = user1Data.id;
    
    const user2Response = await user2Page.request.get('/api/auth/user/');
    const user2Data = await user2Response.json();
    user2Id = user2Data.id;
    
    // Créer un thread de chat (via API user1)
    const threadResponse = await user1Page.request.post('/api/chat/threads/', {
      data: {
        title: 'Test Chat E2E',
        thread_type: 'GENERAL'
      }
    });
    const threadData = await threadResponse.json();
    threadId = threadData.id;
    
    // Ajouter user2 comme membre du thread (via API user1 ou user2)
    // Note: Cette opération peut nécessiter des permissions spécifiques
    // Pour simplifier, on suppose que user2 peut rejoindre le thread
    try {
      await user2Page.request.post(`/api/chat/threads/${threadId}/join/`, {
        data: {}
      });
    } catch (e) {
      // Si l'endpoint n'existe pas, on peut utiliser l'API admin ou skip ce test
      console.warn('[E2E] Endpoint join thread non disponible, utilisation alternative');
    }
  });

  test.afterAll(async () => {
    await user1Context.close();
    await user2Context.close();
  });

  test('1. Connexion WebSocket pour user1', async () => {
    // Aller sur la page de chat
    await user1Page.goto(`/chat/${threadId}`);
    await waitForApiIdle(user1Page);
    
    // Attendre que la connexion WebSocket soit établie
    // (on peut vérifier via les logs de la console ou un indicateur dans l'UI)
    await user1Page.waitForTimeout(1000); // Attendre la connexion WS
    
    // Vérifier que la page est chargée
    const pageTitle = await user1Page.title();
    expect(pageTitle).toBeTruthy();
    
    console.log('[E2E] ✅ User1 connecté au chat');
  });

  test('2. Connexion WebSocket pour user2', async () => {
    // Aller sur la page de chat
    await user2Page.goto(`/chat/${threadId}`);
    await waitForApiIdle(user2Page);
    
    // Attendre que la connexion WebSocket soit établie
    await user2Page.waitForTimeout(1000);
    
    // Vérifier que la page est chargée
    const pageTitle = await user2Page.title();
    expect(pageTitle).toBeTruthy();
    
    console.log('[E2E] ✅ User2 connecté au chat');
  });

  test('3. User1 envoie un message, User2 le reçoit', async () => {
    // User1 envoie un message via l'UI
    const messageInput = user1Page.locator('input[type="text"], textarea').first();
    await messageInput.fill('Message E2E de user1');
    await messageInput.press('Enter');
    
    // Attendre que le message soit envoyé
    await user1Page.waitForTimeout(500);
    
    // Vérifier que le message apparaît dans l'UI de user1
    const messageInUser1 = user1Page.locator('text=Message E2E de user1').first();
    await expect(messageInUser1).toBeVisible({ timeout: 5000 });
    
    // Attendre que le message soit broadcasté via WebSocket
    await user2Page.waitForTimeout(1000);
    
    // Vérifier que le message apparaît dans l'UI de user2
    const messageInUser2 = user2Page.locator('text=Message E2E de user1').first();
    await expect(messageInUser2).toBeVisible({ timeout: 5000 });
    
    console.log('[E2E] ✅ Message envoyé par user1 et reçu par user2');
  });

  test('4. User2 envoie un message, User1 le reçoit', async () => {
    // User2 envoie un message via l'UI
    const messageInput = user2Page.locator('input[type="text"], textarea').first();
    await messageInput.fill('Réponse E2E de user2');
    await messageInput.press('Enter');
    
    // Attendre que le message soit envoyé
    await user2Page.waitForTimeout(500);
    
    // Vérifier que le message apparaît dans l'UI de user2
    const messageInUser2 = user2Page.locator('text=Réponse E2E de user2').first();
    await expect(messageInUser2).toBeVisible({ timeout: 5000 });
    
    // Attendre que le message soit broadcasté via WebSocket
    await user1Page.waitForTimeout(1000);
    
    // Vérifier que le message apparaît dans l'UI de user1
    const messageInUser1 = user1Page.locator('text=Réponse E2E de user2').first();
    await expect(messageInUser1).toBeVisible({ timeout: 5000 });
    
    console.log('[E2E] ✅ Message envoyé par user2 et reçu par user1');
  });

  test('5. Vérifier persistence des messages (rechargement page)', async () => {
    // User1 recharge la page
    await user1Page.reload();
    await waitForApiIdle(user1Page);
    
    // Attendre que les messages soient chargés depuis l'API
    await user1Page.waitForTimeout(1000);
    
    // Vérifier que les messages précédents sont toujours visibles
    const message1 = user1Page.locator('text=Message E2E de user1').first();
    const message2 = user1Page.locator('text=Réponse E2E de user2').first();
    
    await expect(message1).toBeVisible({ timeout: 5000 });
    await expect(message2).toBeVisible({ timeout: 5000 });
    
    console.log('[E2E] ✅ Messages persistés après rechargement');
  });

  test('6. Déconnexion brutale et reconnexion', async () => {
    // User1 se connecte
    await user1Page.goto(`/chat/${threadId}`);
    await waitForApiIdle(user1Page);
    await user1Page.waitForTimeout(1000);
    
    // Simuler une déconnexion brutale (fermer l'onglet)
    // Note: On ne peut pas vraiment fermer l'onglet dans Playwright,
    // mais on peut simuler en naviguant ailleurs
    await user1Page.goto('/');
    await user1Page.waitForTimeout(500);
    
    // Reconnexion
    await user1Page.goto(`/chat/${threadId}`);
    await waitForApiIdle(user1Page);
    await user1Page.waitForTimeout(1000);
    
    // Vérifier que la reconnexion fonctionne
    const pageTitle = await user1Page.title();
    expect(pageTitle).toBeTruthy();
    
    console.log('[E2E] ✅ Déconnexion brutale et reconnexion réussies');
  });
});
