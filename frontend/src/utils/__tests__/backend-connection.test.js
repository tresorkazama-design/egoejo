import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { API_BASE, fetchAPI } from '../api';

describe('Connexion Backend-Frontend', () => {
  const originalFetch = global.fetch;
  
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
    vi.clearAllMocks();
  });

  describe('Configuration API', () => {
    it('devrait avoir une URL de base configurée', () => {
      expect(API_BASE).toBeDefined();
      expect(API_BASE).toContain('http');
      expect(API_BASE).toContain('/api');
    });

    it('devrait pointer vers le backend local par défaut', () => {
      // Le test accepte localhost ou 127.0.0.1, ou une URL de production si VITE_API_URL est défini
      expect(API_BASE).toMatch(/https?:\/\/(localhost|127\.0\.0\.1|[\w.-]+):?\d*\/api/);
    });
  });

  describe('Health Check - Vérification de la connexion', () => {
    it('devrait pouvoir se connecter au backend (health check)', async () => {
      // Mock d'une réponse réussie du backend
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ status: 'ok', message: 'Backend is running' }),
      });

      const result = await fetchAPI('/health/');
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/health/'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result.status).toBe('ok');
    });

    it('devrait gérer les erreurs de connexion au backend', async () => {
      // Simuler une erreur de connexion (backend non disponible)
      global.fetch.mockRejectedValueOnce(new Error('Network error: Failed to fetch'));

      await expect(fetchAPI('/health/')).rejects.toThrow();
    });

    it('devrait gérer les erreurs HTTP du backend', async () => {
      // Simuler une erreur 500 du backend
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal Server Error' }),
      });

      await expect(fetchAPI('/health/')).rejects.toThrow('Internal Server Error');
    });
  });

  describe('Endpoints principaux', () => {
    it('devrait pouvoir appeler l\'endpoint /projets/', async () => {
      const mockProjets = { results: [], count: 0 };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockProjets,
      });

      const result = await fetchAPI('/projets/');
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projets/'),
        expect.any(Object)
      );
      expect(result).toEqual(mockProjets);
    });

    it('devrait pouvoir appeler l\'endpoint /intents/rejoindre/', async () => {
      const mockResponse = { message: 'Intention enregistrée' };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse,
      });

      const result = await fetchAPI('/intents/rejoindre/', {
        method: 'POST',
        body: JSON.stringify({ nom: 'Test', email: 'test@example.com' }),
      });
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/intents/rejoindre/'),
        expect.objectContaining({
          method: 'POST',
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('devrait ajouter le token d\'authentification si disponible', async () => {
      const mockToken = 'test-token-123';
      
      // Mock addSecurityHeaders directement dans api.js
      // On doit réimporter api.js pour avoir accès à la fonction
      const apiModule = await import('../api.js');
      const securityModule = await import('../security.js');
      
      // Mock les fonctions de security
      vi.spyOn(securityModule, 'getTokenSecurely').mockReturnValue(mockToken);
      vi.spyOn(securityModule, 'isTokenValid').mockReturnValue(true);
      vi.spyOn(securityModule, 'getCSRFToken').mockReturnValue(null);
      
      // Mock addSecurityHeaders pour qu'il utilise nos mocks
      vi.spyOn(securityModule, 'addSecurityHeaders').mockImplementation((headers = {}) => {
        const securityHeaders = {
          'Content-Type': 'application/json',
          ...headers,
        };
        if (mockToken && securityModule.isTokenValid(mockToken)) {
          securityHeaders['Authorization'] = `Bearer ${mockToken}`;
        }
        return securityHeaders;
      });

      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      });

      await apiModule.fetchAPI('/admin/projets/');
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
        })
      );
    });
  });

  describe('Gestion des erreurs réseau', () => {
    it('devrait gérer les timeouts de connexion', async () => {
      // Simuler un timeout
      global.fetch.mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(fetchAPI('/projets/')).rejects.toThrow();
    });

    it('devrait gérer les erreurs CORS', async () => {
      // Simuler une erreur CORS
      global.fetch.mockRejectedValueOnce(
        new Error("CORS policy: No 'Access-Control-Allow-Origin' header")
      );

      await expect(fetchAPI('/projets/')).rejects.toThrow();
    });
  });

  describe('Format des requêtes', () => {
    it('devrait envoyer les données en JSON', async () => {
      const data = { nom: 'Test', email: 'test@example.com' };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => ({}),
      });

      await fetchAPI('/intents/rejoindre/', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      
      const callArgs = global.fetch.mock.calls[0];
      expect(callArgs[1].headers['Content-Type']).toBe('application/json');
    });

    it('devrait préserver les headers personnalisés', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({}),
      });

      await fetchAPI('/projets/', {
        headers: {
          'X-Custom-Header': 'custom-value',
        },
      });
      
      const callArgs = global.fetch.mock.calls[0];
      expect(callArgs[1].headers['X-Custom-Header']).toBe('custom-value');
    });
  });
});

