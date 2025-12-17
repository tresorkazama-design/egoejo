import { describe, it, expect, vi, beforeEach } from 'vitest';

// Utilitaires API
export const API_BASE = 'http://127.0.0.1:8000/api';

export const fetchAPI = async (endpoint, options = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  // Ajouter le token si disponible
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
    throw new Error(error.detail || `Erreur ${response.status}`);
  }

  return response.json();
};

export const handleAPIError = (error) => {
  if (error instanceof Error) {
    return error.message;
  }
  if (typeof error === 'string') {
    return error;
  }
  return 'Une erreur est survenue';
};

describe('API Utilities', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
    localStorage.clear();
    localStorage.getItem.mockClear();
    localStorage.setItem.mockClear();
  });

  describe('fetchAPI', () => {
    it('devrait faire une requête GET simple', async () => {
      const mockData = { id: 1, name: 'Test' };
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockData,
      });

      const result = await fetchAPI('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        `${API_BASE}/test`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
      expect(result).toEqual(mockData);
    });

    it('devrait ajouter le token d\'authentification si disponible', async () => {
      localStorage.setItem('token', 'test-token');
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await fetchAPI('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('devrait accepter des options personnalisées', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({}),
      });

      await fetchAPI('/test', {
        method: 'POST',
        body: JSON.stringify({ name: 'Test' }),
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ name: 'Test' }),
        })
      );
    });

    it('devrait lancer une erreur si la réponse n\'est pas ok', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Not found' }),
      });

      await expect(fetchAPI('/test')).rejects.toThrow('Not found');
    });

    it('devrait gérer les erreurs sans détail', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => {
          throw new Error('Parse error');
        },
      });

      await expect(fetchAPI('/test')).rejects.toThrow('Erreur inconnue');
    });
  });

  describe('handleAPIError', () => {
    it('devrait retourner le message d\'une Error', () => {
      const error = new Error('Erreur de test');
      expect(handleAPIError(error)).toBe('Erreur de test');
    });

    it('devrait retourner une chaîne directement', () => {
      expect(handleAPIError('Erreur simple')).toBe('Erreur simple');
    });

    it('devrait retourner un message par défaut pour les autres types', () => {
      expect(handleAPIError(null)).toBe('Une erreur est survenue');
      expect(handleAPIError({})).toBe('Une erreur est survenue');
      expect(handleAPIError(123)).toBe('Une erreur est survenue');
    });
  });
});

