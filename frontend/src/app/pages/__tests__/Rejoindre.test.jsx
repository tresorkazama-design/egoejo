import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Rejoindre } from '../Rejoindre';
import { fetchAPI } from '../../../utils/api';
import { server } from '../../../test/mocks/server';

vi.mock('../../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => {
    if (err instanceof Error) {
      return err.message;
    }
    return 'Une erreur est survenue';
  }),
}));

import { renderWithProviders } from '../../../test/test-utils';

describe('Rejoindre', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    global.fetch = vi.fn();
    // Désactiver MSW complètement pour ces tests
    server.resetHandlers();
  });

  afterEach(() => {
    server.resetHandlers();
  });

  it('devrait afficher le formulaire de rejoindre', () => {
    renderWithProviders(<Rejoindre />);
    expect(screen.getByTestId('rejoindre-page')).toBeInTheDocument();
    expect(screen.getByTestId('rejoindre-form')).toBeInTheDocument();
  });

  it('devrait afficher tous les champs du formulaire', () => {
    renderWithProviders(<Rejoindre />);
    expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/profil/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
  });

  it('devrait valider les champs requis', async () => {
    renderWithProviders(<Rejoindre />);

    const form = screen.getByTestId('rejoindre-form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/le nom est requis/i)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait valider le format de l\'email', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Rejoindre />);

    // Remplir les champs requis d'abord
    await user.type(screen.getByLabelText(/nom/i), 'Test User');
    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'invalid-email');
    await user.selectOptions(screen.getByLabelText(/profil/i), 'je-decouvre');

    const form = screen.getByTestId('rejoindre-form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/email invalide/i)).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait soumettre le formulaire avec succès', async () => {
    const user = userEvent.setup();
    fetchAPI.mockResolvedValueOnce({ id: 1, ok: true });

    renderWithProviders(<Rejoindre />);

    await user.type(screen.getByLabelText(/nom/i), 'Test User');
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.selectOptions(screen.getByLabelText(/profil/i), 'je-decouvre');

    const submitButton = screen.getByRole('button', { name: /envoyer/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/merci/i)).toBeInTheDocument();
    });
  });

  it('devrait gérer les erreurs de soumission', { timeout: 10000 }, async () => {
    const user = userEvent.setup();
    // Désactiver MSW pour ce test et utiliser uniquement le mock
    server.resetHandlers();
    const error = new Error('Erreur serveur');
    fetchAPI.mockImplementationOnce(() => Promise.reject(error));

    renderWithProviders(<Rejoindre />);

    await user.type(screen.getByLabelText(/nom/i), 'Test User');
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.selectOptions(screen.getByLabelText(/profil/i), 'je-decouvre');

    const form = screen.getByTestId('rejoindre-form');
    fireEvent.submit(form);

    // Attendre que l'erreur soit affichée (pas le message de succès)
    await waitFor(() => {
      // L'erreur devrait être affichée dans errorMessage
      // Ne pas afficher le message de succès
      expect(screen.queryByText(/merci/i)).not.toBeInTheDocument();
      const errorElement = screen.queryByText(/erreur/i);
      expect(errorElement).toBeInTheDocument();
    }, { timeout: 5000 });
  });

  it('devrait protéger contre le spam (honeypot)', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Rejoindre />);

    // Remplir le champ honeypot (caché)
    const websiteInput = document.querySelector('input[name="website"]');
    expect(websiteInput).toBeInTheDocument();
    await user.type(websiteInput, 'spam');

    // Remplir les autres champs requis pour que la validation passe
    await user.type(screen.getByLabelText(/nom/i), 'Test User');
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.selectOptions(screen.getByLabelText(/profil/i), 'je-decouvre');

    const form = screen.getByTestId('rejoindre-form');
    fireEvent.submit(form);

    await waitFor(() => {
      expect(screen.getByText(/spam détecté/i)).toBeInTheDocument();
    }, { timeout: 3000 });
  });
});

