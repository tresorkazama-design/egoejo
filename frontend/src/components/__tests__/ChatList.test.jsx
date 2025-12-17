import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ChatList from '../ChatList';
import { renderWithProviders } from '../../test/test-utils';
import { fetchAPI } from '../../utils/api';

vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => err.message || 'Erreur'),
}));

describe('ChatList', () => {
  const mockOnSelectThread = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('devrait afficher un loader pendant le chargement', () => {
    fetchAPI.mockImplementation(() => new Promise(() => {})); // Ne résout jamais
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('devrait afficher les threads de chat généralisé (sans projet)', async () => {
    const generalThreads = [
      {
        id: 1,
        title: 'Discussion générale',
        project: null,
        participants: [{ id: 1, username: 'user1' }, { id: 2, username: 'user2' }],
        last_message_at: new Date().toISOString(),
      },
      {
        id: 2,
        title: 'Chat libre',
        project: null,
        participants: [{ id: 1, username: 'user1' }],
        last_message_at: new Date().toISOString(),
      },
    ];

    fetchAPI.mockResolvedValue(generalThreads);
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} />);

    await waitFor(() => {
      expect(screen.getByText('Discussion générale')).toBeInTheDocument();
      expect(screen.getByText('Chat libre')).toBeInTheDocument();
    });
  });

  it('devrait afficher les threads liés aux projets', async () => {
    const projectThreads = [
      {
        id: 3,
        title: 'Discussion Projet A',
        project: { id: 1, titre: 'Projet A' },
        participants: [{ id: 1, username: 'user1' }],
        last_message_at: new Date().toISOString(),
      },
      {
        id: 4,
        title: 'Discussion Projet B',
        project: { id: 2, titre: 'Projet B' },
        participants: [{ id: 1, username: 'user1' }],
        last_message_at: new Date().toISOString(),
      },
    ];

    fetchAPI.mockResolvedValue(projectThreads);
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} />);

    await waitFor(() => {
      expect(screen.getByText('Discussion Projet A')).toBeInTheDocument();
      expect(screen.getByText('Discussion Projet B')).toBeInTheDocument();
    });
  });

  it('devrait afficher les threads de communauté (multi-participants)', async () => {
    const communityThreads = [
      {
        id: 5,
        title: 'Communauté EGOEJO',
        project: null,
        participants: [
          { id: 1, username: 'user1' },
          { id: 2, username: 'user2' },
          { id: 3, username: 'user3' },
          { id: 4, username: 'user4' },
        ],
        last_message_at: new Date().toISOString(),
      },
    ];

    fetchAPI.mockResolvedValue(communityThreads);
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} />);

    await waitFor(() => {
      expect(screen.getByText('Communauté EGOEJO')).toBeInTheDocument();
      // Vérifier que les participants sont affichés
      expect(screen.getByText('user1')).toBeInTheDocument();
      expect(screen.getByText('user2')).toBeInTheDocument();
      expect(screen.getByText('user3')).toBeInTheDocument();
      // Vérifier l'indicateur "+X" pour les participants supplémentaires
      expect(screen.getByText('+1')).toBeInTheDocument();
    });
  });

  it('devrait permettre de sélectionner un thread', async () => {
    const user = userEvent.setup();
    const threads = [
      {
        id: 1,
        title: 'Thread test',
        project: null,
        participants: [{ id: 1, username: 'user1' }],
        last_message_at: new Date().toISOString(),
      },
    ];

    fetchAPI.mockResolvedValue(threads);
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} selectedThreadId={null} />);

    await waitFor(() => {
      expect(screen.getByText('Thread test')).toBeInTheDocument();
    });

    const threadButton = screen.getByText('Thread test');
    await user.click(threadButton);

    expect(mockOnSelectThread).toHaveBeenCalledWith(threads[0]);
  });

  it('devrait mettre en évidence le thread sélectionné', async () => {
    const threads = [
      {
        id: 1,
        title: 'Thread sélectionné',
        project: null,
        participants: [{ id: 1, username: 'user1' }],
        last_message_at: new Date().toISOString(),
      },
      {
        id: 2,
        title: 'Thread non sélectionné',
        project: null,
        participants: [{ id: 1, username: 'user1' }],
        last_message_at: new Date().toISOString(),
      },
    ];

    fetchAPI.mockResolvedValue(threads);
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} selectedThreadId={1} />);

    await waitFor(() => {
      const selectedButton = screen.getByText('Thread sélectionné').closest('button');
      expect(selectedButton).toHaveClass('is-active');
    });
  });

  it('devrait afficher un message si aucun thread n\'existe', async () => {
    fetchAPI.mockResolvedValue([]);
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} />);

    await waitFor(() => {
      expect(screen.getByText(/aucune conversation disponible/i)).toBeInTheDocument();
    });
  });

  it('devrait gérer les erreurs de chargement', async () => {
    fetchAPI.mockRejectedValue(new Error('Erreur réseau'));
    renderWithProviders(<ChatList onSelectThread={mockOnSelectThread} />);

    await waitFor(() => {
      expect(screen.getByText(/erreur/i)).toBeInTheDocument();
    });
  });
});

