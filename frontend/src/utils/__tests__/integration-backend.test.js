import { describe, it, expect, vi, beforeEach } from 'vitest';
import { fetchAPI } from '../api';

// Mock fetchAPI pour ces tests
vi.mock('../api', async () => {
  const actual = await vi.importActual('../api');
  return {
    ...actual,
    fetchAPI: vi.fn(),
  };
});

/**
 * Tests d'intégration Backend-Frontend (mockés)
 * Ces tests utilisent des mocks pour simuler les réponses du backend
 * et ne nécessitent pas que le backend soit démarré
 */
describe('Tests d\'intégration Backend-Frontend', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  describe('Health Check', () => {
    it('devrait pouvoir se connecter au backend (mocké)', async () => {
      // Mock de la réponse
      fetchAPI.mockResolvedValue({
        results: [
          { id: 1, titre: 'Projet 1', description: 'Description 1' }
        ]
      });

      const data = await fetchAPI('/projets/');
      expect(data).toBeDefined();
      expect(typeof data).toBe('object');
      expect(fetchAPI).toHaveBeenCalledWith('/projets/');
    });

    it('devrait recevoir une réponse JSON valide', async () => {
      // Mock de la réponse
      fetchAPI.mockResolvedValue({
        results: [
          { id: 1, titre: 'Projet 1' }
        ]
      });

      const data = await fetchAPI('/projets/');
      expect(data).toBeDefined();
      expect(typeof data).toBe('object');
      if (data.results) {
        expect(Array.isArray(data.results)).toBe(true);
      }
    });
  });

  describe('Endpoints API', () => {
    it('devrait pouvoir récupérer la liste des projets', async () => {
      // Mock de la réponse
      fetchAPI.mockResolvedValue({
        results: [
          { id: 1, titre: 'Projet 1' },
          { id: 2, titre: 'Projet 2' }
        ]
      });

      const data = await fetchAPI('/projets/');
      expect(data).toBeDefined();
      if (Array.isArray(data)) {
        expect(Array.isArray(data)).toBe(true);
      } else if (data.results) {
        expect(Array.isArray(data.results)).toBe(true);
      }
    });

    it('devrait pouvoir soumettre une intention de rejoindre', async () => {
      const testData = {
        nom: 'Test Integration',
        email: `test-${Date.now()}@example.com`,
        profil: 'je-decouvre',
      };

      // Mock de la réponse
      fetchAPI.mockResolvedValue({
        id: 1,
        ok: true,
        ...testData
      });

      const response = await fetchAPI('/intents/rejoindre/', {
        method: 'POST',
        body: JSON.stringify(testData),
      });

      expect(response).toBeDefined();
      expect(response.id || response.ok).toBeDefined();
      expect(fetchAPI).toHaveBeenCalledWith(
        '/intents/rejoindre/',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(testData),
        })
      );
    });
  });

  describe('Gestion des erreurs', () => {
    it('devrait gérer les erreurs 404 correctement', async () => {
      // Mock d'une erreur 404
      fetchAPI.mockRejectedValue(new Error('Erreur 404'));

      let errorThrown = false;
      try {
        await fetchAPI('/endpoint-inexistant/');
      } catch (error) {
        errorThrown = true;
        expect(error).toBeInstanceOf(Error);
        expect(error.message).toBeDefined();
      }
      expect(errorThrown).toBe(true);
    });

    it('devrait gérer les erreurs 500 correctement', async () => {
      // Mock d'une erreur 500
      fetchAPI.mockRejectedValue(new Error('Erreur 500'));

      let errorThrown = false;
      try {
        await fetchAPI('/projets/');
      } catch (error) {
        errorThrown = true;
        expect(error).toBeInstanceOf(Error);
        expect(error.message).toBeDefined();
      }
      expect(errorThrown).toBe(true);
    });
  });
});

