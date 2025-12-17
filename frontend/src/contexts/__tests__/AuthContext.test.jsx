import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import React from 'react';
import { AuthProvider, useAuth } from '../AuthContext';

describe('AuthContext', () => {
  beforeEach(() => {
    // Réinitialiser les mocks avant chaque test
    vi.clearAllMocks();
    localStorage.clear();
    localStorage.getItem.mockClear();
    localStorage.setItem.mockClear();
    localStorage.removeItem.mockClear();
    global.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Initialisation', () => {
    it('devrait initialiser sans token', () => {
      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      expect(result.current.user).toBeNull();
      expect(result.current.token).toBeNull();
      expect(result.current.loading).toBe(false);
    });

    it('devrait initialiser avec token depuis localStorage', async () => {
      const mockToken = 'test-token-123';
      localStorage.setItem('token', mockToken);

      // Mock de la réponse API pour /auth/me/
      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          username: 'testuser',
          email: 'test@example.com',
        }),
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.token).toBe(mockToken);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/me/'),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: `Bearer ${mockToken}`,
          }),
        })
      );
    });
  });

  describe('Login', () => {
    it('devrait connecter un utilisateur avec succès', async () => {
      const mockToken = 'access-token-123';
      const mockRefreshToken = 'refresh-token-123';
      const mockUser = {
        id: 1,
        username: 'testuser',
        email: 'test@example.com',
      };

      // Mock de la réponse login
      fetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            access: mockToken,
            refresh: mockRefreshToken,
          }),
        })
        // Mock de la réponse /auth/me/ après login
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUser,
        });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await result.current.login('testuser', 'password123');
      });

      await waitFor(() => {
        expect(result.current.token).toBe(mockToken);
        expect(result.current.user).toEqual(mockUser);
      });

      expect(localStorage.setItem).toHaveBeenCalledWith('token', mockToken);
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', mockRefreshToken);
    });

    it('devrait échouer avec des identifiants invalides', async () => {
      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          detail: 'Identifiants invalides',
        }),
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await expect(
          result.current.login('wronguser', 'wrongpass')
        ).rejects.toThrow('Identifiants invalides');
      });

      expect(result.current.token).toBeNull();
      expect(result.current.user).toBeNull();
    });
  });

  describe('Register', () => {
    it('devrait enregistrer un nouvel utilisateur avec succès', async () => {
      const userData = {
        username: 'newuser',
        email: 'newuser@example.com',
        password: 'password123',
      };

      fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        const success = await result.current.register(userData);
        expect(success).toBe(true);
      });

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/register/'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
          body: JSON.stringify(userData),
        })
      );
    });

    it('devrait gérer les erreurs d\'inscription', async () => {
      const userData = {
        username: 'existinguser',
        email: 'existing@example.com',
        password: 'password123',
      };

      fetch.mockResolvedValueOnce({
        ok: false,
        json: async () => ({
          username: ['Un utilisateur avec ce nom existe déjà.'],
        }),
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await expect(
          result.current.register(userData)
        ).rejects.toThrow();
      });
    });
  });

  describe('Logout', () => {
    it('devrait déconnecter l\'utilisateur', async () => {
      const mockToken = 'test-token';
      localStorage.setItem('token', mockToken);

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      // Attendre que le contexte soit chargé
      await waitFor(() => {
        expect(result.current).not.toBeNull();
      });

      // Simuler un utilisateur connecté puis déconnexion
      await act(async () => {
        if (result.current) {
          result.current.logout();
        }
      });

      await waitFor(() => {
        expect(result.current.token).toBeNull();
        expect(result.current.user).toBeNull();
      });

      expect(localStorage.removeItem).toHaveBeenCalledWith('token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('Gestion des erreurs', () => {
    it('devrait gérer les erreurs réseau', async () => {
      fetch.mockRejectedValueOnce(new Error('Network error'));

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await act(async () => {
        await expect(
          result.current.login('testuser', 'password123')
        ).rejects.toThrow();
      });
    });

    it('devrait déconnecter si le token est invalide', async () => {
      const invalidToken = 'invalid-token';
      localStorage.setItem('token', invalidToken);

      fetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
      });

      const { result } = renderHook(() => useAuth(), {
        wrapper: AuthProvider,
      });

      await waitFor(() => {
        expect(result.current.loading).toBe(false);
      });

      expect(result.current.token).toBeNull();
      expect(result.current.user).toBeNull();
    });
  });
});

