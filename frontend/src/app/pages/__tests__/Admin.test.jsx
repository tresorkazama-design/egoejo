import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, fireEvent, render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Admin } from '../Admin';
import { fetchAPI } from '../../../utils/api';
import { useAuth } from '../../../contexts/AuthContext';
import { LanguageProvider } from '../../../contexts/LanguageContext';
import { NotificationProvider } from '../../../contexts/NotificationContext';

vi.mock('../../../utils/api');
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }) => children, // Ne pas bloquer le rendu
}));

import { renderWithProviders } from '../../../test/test-utils';

describe('Admin', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // S'assurer que useAuth retourne toujours les bonnes valeurs par défaut
    useAuth.mockReturnValue({ 
      token: 'test-token', 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    global.fetch = vi.fn();
    window.confirm = vi.fn(() => true);
    // Mock fetch pour éviter les appels API réels
    global.fetch.mockResolvedValue({
      ok: true,
      json: async () => ({}),
      blob: async () => new Blob(['test'], { type: 'text/csv' })
    });
  });

  it('devrait afficher la page admin', async () => {
    useAuth.mockReturnValue({ 
      token: 'test-token', 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    fetchAPI.mockResolvedValue({ results: [], total_pages: 1 });
    renderWithProviders(<Admin />, { language: 'fr' });
    // Attendre que le composant se charge (le useEffect se déclenche)
    await waitFor(() => {
      expect(screen.getByTestId('admin-page')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('devrait demander l\'authentification si pas de token', async () => {
    useAuth.mockReturnValue({ 
      token: null, 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    renderWithProviders(<Admin />, { language: 'fr' });
    // Le texte peut être "Vous devez être connecté pour accéder à cette page."
    await waitFor(() => {
      expect(screen.getByText(/vous devez être connecté/i)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('devrait afficher la liste des intentions', async () => {
    useAuth.mockReturnValue({ 
      token: 'test-token', 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    const mockIntents = [
      { id: 1, nom: 'Test', email: 'test@example.com', profil: 'je-decouvre', date_creation: '2025-01-27' },
    ];
    fetchAPI.mockResolvedValue({ results: mockIntents, total_pages: 1 });

    renderWithProviders(<Admin />, { language: 'fr' });

    // Attendre que le loader disparaisse et que les données soient chargées
    await waitFor(() => {
      expect(screen.getByTestId('admin-page')).toBeInTheDocument();
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(screen.getByTestId('intent-1')).toBeInTheDocument();
      expect(screen.getByText('Test')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('devrait permettre de filtrer par recherche', { timeout: 15000 }, async () => {
    useAuth.mockReturnValue({ 
      token: 'test-token', 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    fetchAPI.mockResolvedValue({ results: [], total_pages: 1 });

    renderWithProviders(<Admin />, { language: 'fr' });

    // Attendre que le loader disparaisse et que la page soit chargée
    await waitFor(() => {
      expect(screen.getByTestId('admin-page')).toBeInTheDocument();
    }, { timeout: 5000 });

    // Attendre que le champ de recherche soit disponible (peut être "Recherche" ou "Search")
    await waitFor(() => {
      const searchInput = screen.queryByLabelText(/recherche|search/i);
      expect(searchInput).toBeInTheDocument();
    }, { timeout: 3000 });

    const searchInput = screen.getByLabelText(/recherche|search/i);
    // Simuler un changement complet du filtre avec fireEvent
    fireEvent.change(searchInput, { target: { value: 'test' } });

    // Attendre que le useEffect se déclenche avec le filtre complet
    // Le composant utilise useEffect avec filters comme dépendance
    await waitFor(() => {
      // Vérifier qu'au moins un appel contient "search=test"
      const calls = fetchAPI.mock.calls;
      const hasTestSearch = calls.some(call => {
        const url = call[0];
        if (!url || typeof url !== 'string') return false;
        // L'URL peut être "/intents/admin/?search=test" ou "/intents/admin/?page=1&search=test"
        return url.includes('search=test');
      });
      expect(hasTestSearch).toBe(true);
    }, { timeout: 5000 });
  }, { timeout: 15000 });

  it('devrait permettre de supprimer une intention', async () => {
    useAuth.mockReturnValue({ 
      token: 'test-token', 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    const user = userEvent.setup();
    const mockIntents = [
      { id: 1, nom: 'Test', email: 'test@example.com', profil: 'je-decouvre', date_creation: '2025-01-27' },
    ];
    // Premier appel pour charger les intents, puis pour recharger après suppression
    fetchAPI.mockResolvedValueOnce({ results: mockIntents, total_pages: 1 });
    // Le composant utilise fetchAPI pour la suppression
    fetchAPI.mockResolvedValueOnce({ ok: true });
    // Rechargement après suppression
    fetchAPI.mockResolvedValueOnce({ results: [], total_pages: 1 });

    renderWithProviders(<Admin />, { language: 'fr' });

    await waitFor(() => {
      expect(screen.getByTestId('admin-page')).toBeInTheDocument();
    }, { timeout: 3000 });

    await waitFor(() => {
      expect(screen.getByTestId('intent-1')).toBeInTheDocument();
    }, { timeout: 5000 });

    const deleteButton = screen.getByRole('button', { name: /supprimer|delete/i });
    await user.click(deleteButton);

    await waitFor(() => {
      // Le composant utilise fetchAPI pour la suppression
      expect(fetchAPI).toHaveBeenCalledWith(
        expect.stringContaining('/intents/1/delete/'),
        expect.any(Object)
      );
    }, { timeout: 5000 });
  });

  it('devrait permettre d\'exporter en CSV', async () => {
    useAuth.mockReturnValue({ 
      token: 'test-token', 
      user: null, 
      loading: false,
      login: vi.fn(),
      logout: vi.fn()
    });
    const user = userEvent.setup();
    fetchAPI.mockResolvedValue({ results: [], total_pages: 1 });
    global.fetch.mockResolvedValue({
      ok: true,
      blob: async () => new Blob(['test'], { type: 'text/csv' })
    });

    renderWithProviders(<Admin />, { language: 'fr' });

    await waitFor(() => {
      expect(screen.getByTestId('admin-page')).toBeInTheDocument();
    }, { timeout: 5000 });

    // Attendre que le bouton d'export soit disponible (il peut être dans une section search)
    await waitFor(() => {
      const exportButton = screen.getByRole('button', { name: /exporter|export/i });
      expect(exportButton).toBeInTheDocument();
    }, { timeout: 5000 });

    const exportButton = screen.getByRole('button', { name: /exporter|export/i });
    await user.click(exportButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalled();
    }, { timeout: 5000 });
  });
});

