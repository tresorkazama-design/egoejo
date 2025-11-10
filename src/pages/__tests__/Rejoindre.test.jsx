import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Rejoindre from '../Rejoindre';

// Mock de l'API
vi.mock('../../config/api.js', () => ({
  api: {
    rejoindre: () => '/api/intents/rejoindre/',
  },
}));

describe('Rejoindre', () => {
  beforeEach(() => {
    // Reset fetch mock before each test
    global.fetch = vi.fn();
  });

  it('renders the form correctly', () => {
    render(<Rejoindre />);
    expect(screen.getByText('Rejoindre EGOEJO')).toBeInTheDocument();
    expect(screen.getByLabelText(/nom/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/profil/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument();
  });

  it('shows error when required fields are missing', async () => {
    const user = userEvent.setup();
    render(<Rejoindre />);
    
    const submitButton = screen.getByRole('button', { name: /envoyer/i });
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/le nom est requis/i)).toBeInTheDocument();
    });
  });

  it('shows error when email is invalid', async () => {
    const user = userEvent.setup();
    render(<Rejoindre />);
    
    const nomInput = screen.getByLabelText(/nom/i);
    const emailInput = screen.getByLabelText(/email/i);
    const submitButton = screen.getByRole('button', { name: /envoyer/i });
    
    await user.type(nomInput, 'Test User');
    await user.type(emailInput, 'invalid-email');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/l'email n'est pas valide/i)).toBeInTheDocument();
    });
  });

  it('submits form successfully', async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ ok: true, id: 1, created_at: '2025-01-27T10:00:00Z' }),
    });
    
    render(<Rejoindre />);
    
    const nomInput = screen.getByLabelText(/nom/i);
    const emailInput = screen.getByLabelText(/email/i);
    const profilSelect = screen.getByLabelText(/profil/i);
    const submitButton = screen.getByRole('button', { name: /envoyer/i });
    
    await user.type(nomInput, 'Test User');
    await user.type(emailInput, 'test@example.com');
    await user.selectOptions(profilSelect, 'je-decouvre');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/merci/i)).toBeInTheDocument();
    });
    
    expect(global.fetch).toHaveBeenCalledWith(
      '/api/intents/rejoindre/',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
    );
  });

  it('shows error when submission fails', async () => {
    const user = userEvent.setup();
    global.fetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ ok: false, error: 'Erreur serveur' }),
    });
    
    render(<Rejoindre />);
    
    const nomInput = screen.getByLabelText(/nom/i);
    const emailInput = screen.getByLabelText(/email/i);
    const profilSelect = screen.getByLabelText(/profil/i);
    const submitButton = screen.getByRole('button', { name: /envoyer/i });
    
    await user.type(nomInput, 'Test User');
    await user.type(emailInput, 'test@example.com');
    await user.selectOptions(profilSelect, 'je-decouvre');
    await user.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/erreur serveur/i)).toBeInTheDocument();
    });
  });
});

