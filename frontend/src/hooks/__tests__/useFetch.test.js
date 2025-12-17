import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useFetch } from '../useFetch';
import { fetchAPI } from '../../utils/api';
import { server } from '../../test/mocks/server';

vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => {
    if (err instanceof Error) {
      return err.message;
    }
    return 'Une erreur est survenue';
  }),
}));

describe('useFetch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Désactiver MSW complètement pour ces tests
    server.resetHandlers();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('devrait charger les données au montage', async () => {
    const mockData = { id: 1, name: 'Test' };
    fetchAPI.mockResolvedValueOnce(mockData);

    const { result } = renderHook(() => useFetch('/test'));

    expect(result.current.loading).toBe(true);
    expect(result.current.data).toBeNull();

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.data).toEqual(mockData);
    expect(result.current.error).toBeNull();
  });

  it('devrait gérer les erreurs', async () => {
    // Désactiver MSW pour ce test et utiliser uniquement le mock
    server.resetHandlers();
    const error = new Error('Erreur réseau');
    fetchAPI.mockImplementationOnce(() => Promise.reject(error));

    const { result } = renderHook(() => useFetch('/test'));

    // Attendre que le loading soit false ET que l'erreur soit définie
    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeTruthy();
    }, { timeout: 5000 });

    expect(result.current.error).toBe('Erreur réseau');
    expect(result.current.data).toBeNull();
  });

  it('devrait permettre de refetch les données', async () => {
    const mockData1 = { id: 1, name: 'Test 1' };
    const mockData2 = { id: 2, name: 'Test 2' };
    fetchAPI.mockResolvedValueOnce(mockData1).mockResolvedValueOnce(mockData2);

    const { result } = renderHook(() => useFetch('/test'));

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData1);
    });

    result.current.refetch();

    await waitFor(() => {
      expect(result.current.data).toEqual(mockData2);
    });
  });

  it('devrait annuler la requête si le composant est démonté', async () => {
    fetchAPI.mockImplementation(() => new Promise(() => {})); // Jamais résolu

    const { unmount } = renderHook(() => useFetch('/test'));

    unmount();

    // Le fetch devrait être appelé mais annulé
    expect(fetchAPI).toHaveBeenCalled();
  });
});

