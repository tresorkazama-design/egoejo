import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { screen, waitFor, render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import Chat from '../Chat';
import { renderWithProviders } from '../../../test/test-utils';
import { fetchAPI } from '../../../utils/api';
import { useAuth } from '../../../contexts/AuthContext';

// Mock de AuthContext
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: vi.fn(),
  AuthProvider: ({ children }) => children,
}));

// Mock des composants enfants
vi.mock('../../../components/ChatList', () => ({
  default: ({ onSelectThread, selectedThreadId }) => (
    <div data-testid="chat-list">
      <button
        data-testid="select-thread-1"
        onClick={() => onSelectThread({ id: 1, title: 'Thread généralisé', project: null })}
      >
        Thread généralisé
      </button>
      <button
        data-testid="select-thread-2"
        onClick={() => onSelectThread({ id: 2, title: 'Thread projet', project: { id: 1, titre: 'Projet Test' } })}
      >
        Thread projet
      </button>
      <button
        data-testid="select-thread-3"
        onClick={() => onSelectThread({ id: 3, title: 'Thread communauté', project: null, participants: [{ id: 1 }, { id: 2 }, { id: 3 }] })}
      >
        Thread communauté
      </button>
    </div>
  ),
}));

vi.mock('../../../components/ChatWindow', () => ({
  default: ({ thread }) => (
    <div data-testid="chat-window">
      {thread ? (
        <>
          <h3 data-testid="thread-title">{thread.title}</h3>
          {thread.project && (
            <div data-testid="thread-project">Projet: {thread.project.titre}</div>
          )}
          {thread.participants && thread.participants.length > 2 && (
            <div data-testid="thread-community">Communauté: {thread.participants.length} participants</div>
          )}
        </>
      ) : (
        <p data-testid="no-thread">Aucun thread sélectionné</p>
      )}
    </div>
  ),
}));

// Mock de l'API
vi.mock('../../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => err.message || 'Erreur'),
}));

// Mock du hook useWebSocket
vi.mock('../../../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    isConnected: true,
    sendMessage: vi.fn(),
    disconnect: vi.fn(),
  })),
}));

describe('Chat', () => {
  const mockUser = { id: 1, username: 'testuser', email: 'test@example.com' };

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('devrait afficher un loader pendant le chargement de l\'authentification', () => {
    useAuth.mockReturnValue({ loading: true, token: null, user: null, onLogout: vi.fn() });
    renderWithProviders(<Chat />);
    // Vérifier qu'il y a au moins un élément avec "chargement"
    const loadingElements = screen.getAllByText(/chargement/i);
    expect(loadingElements.length).toBeGreaterThan(0);
  });

  it('devrait demander l\'authentification si l\'utilisateur n\'est pas connecté', () => {
    useAuth.mockReturnValue({ loading: false, token: null, user: null, onLogout: vi.fn() });
    renderWithProviders(<Chat />);
    expect(screen.getByText(/vous devez être connecté/i)).toBeInTheDocument();
  });

  it('devrait afficher le chat si l\'utilisateur est connecté', () => {
    useAuth.mockReturnValue({
      loading: false,
      token: 'test-token',
      user: mockUser,
      onLogout: vi.fn(),
    });
    renderWithProviders(<Chat />);
    expect(screen.getByTestId('chat-list')).toBeInTheDocument();
    expect(screen.getByTestId('chat-window')).toBeInTheDocument();
  });

  it('devrait permettre de sélectionner un thread de chat généralisé', async () => {
    const user = userEvent.setup();
    useAuth.mockReturnValue({
      loading: false,
      token: 'test-token',
      user: mockUser,
      onLogout: vi.fn(),
    });
    renderWithProviders(<Chat />);

    const generalThreadButton = screen.getByTestId('select-thread-1');
    await user.click(generalThreadButton);

    await waitFor(() => {
      expect(screen.getByTestId('thread-title')).toHaveTextContent('Thread généralisé');
      expect(screen.queryByTestId('thread-project')).not.toBeInTheDocument();
    });
  });

  it('devrait permettre de sélectionner un thread lié à un projet', async () => {
    const user = userEvent.setup();
    useAuth.mockReturnValue({
      loading: false,
      token: 'test-token',
      user: mockUser,
      onLogout: vi.fn(),
    });
    renderWithProviders(<Chat />);

    const projectThreadButton = screen.getByTestId('select-thread-2');
    await user.click(projectThreadButton);

    await waitFor(() => {
      expect(screen.getByTestId('thread-title')).toHaveTextContent('Thread projet');
      expect(screen.getByTestId('thread-project')).toHaveTextContent('Projet: Projet Test');
    });
  });

  it('devrait permettre de sélectionner un thread de communauté', async () => {
    const user = userEvent.setup();
    useAuth.mockReturnValue({
      loading: false,
      token: 'test-token',
      user: mockUser,
      onLogout: vi.fn(),
    });
    renderWithProviders(<Chat />);

    const communityThreadButton = screen.getByTestId('select-thread-3');
    await user.click(communityThreadButton);

    await waitFor(() => {
      expect(screen.getByTestId('thread-title')).toHaveTextContent('Thread communauté');
      expect(screen.getByTestId('thread-community')).toHaveTextContent('Communauté: 3 participants');
    });
  });

  it('devrait afficher "Aucun thread sélectionné" par défaut', () => {
    useAuth.mockReturnValue({
      loading: false,
      token: 'test-token',
      user: mockUser,
      onLogout: vi.fn(),
    });
    renderWithProviders(<Chat />);
    expect(screen.getByTestId('no-thread')).toBeInTheDocument();
  });
});

