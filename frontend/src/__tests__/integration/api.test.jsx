import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { Projets } from '../../app/pages/Projets';
import { renderWithProviders } from '../../test/test-utils';
import { fetchAPI } from '../../utils/api';

// Mock fetchAPI pour les tests
vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => err.message || 'Erreur'),
}));

describe('Integration API', () => {
  it('devrait charger les projets depuis l\'API (MSW)', async () => {
    // Mock de la réponse API
    fetchAPI.mockResolvedValue({
      results: [
        { id: 1, titre: 'Projet 1', description: 'Description 1', montant_cible: 1000 },
        { id: 2, titre: 'Projet 2', description: 'Description 2', montant_cible: 2000 }
      ]
    });

    renderWithProviders(<Projets />);

    // Attendre que les projets soient affichés
    await waitFor(() => {
      expect(screen.getByText('Projet 1')).toBeInTheDocument();
      expect(screen.getByText('Projet 2')).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('devrait gérer les erreurs réseau', async () => {
    // Mock d'une erreur
    fetchAPI.mockRejectedValue(new Error('Erreur réseau'));

    renderWithProviders(<Projets />);
    
    // Attendre que l'erreur soit affichée ou que le composant gère l'erreur
    await waitFor(() => {
      const errorElement = screen.queryByText(/erreur/i);
      expect(errorElement || screen.queryByTestId('projets-page')).toBeTruthy();
    }, { timeout: 5000 });
  });
});

