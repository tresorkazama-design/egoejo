
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor, render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { appRouter } from '../router';
import { LanguageProvider } from '../../contexts/LanguageContext';
import { NotificationProvider } from '../../contexts/NotificationContext';
import { EcoModeProvider } from '../../contexts/EcoModeContext';
import { fetchAPI } from '../../utils/api';

// Mock AuthContext
const mockUser = {
  id: 1,
  username: 'testuser',
  email: 'test@example.com',
};

let mockAuthState = {
  loading: false,
  token: 'test-token',
  user: mockUser,
  onLogout: vi.fn(),
};

vi.mock('../../contexts/AuthContext', () => ({
  AuthProvider: ({ children }) => children,
  useAuth: () => mockAuthState,
}));

// Mock des composants de chat
vi.mock('../../components/ChatList', () => ({
  default: ({ onSelectThread, selectedThreadId }) => {
    const threads = [
      { id: 1, title: 'Chat généralisé', project: null },
      { id: 2, title: 'Chat Projet A', project: { id: 1, titre: 'Projet A' } },
      { id: 3, title: 'Chat Communauté', project: null, participants: [{ id: 1 }, { id: 2 }, { id: 3 }] },
    ];

    return (
      <div data-testid="chat-list">
        {threads.map((thread) => (
          <button
            key={thread.id}
            data-testid={`thread-${thread.id}`}
            onClick={() => onSelectThread(thread)}
            className={selectedThreadId === thread.id ? 'is-active' : ''}
          >
            {thread.title}
          </button>
        ))}
      </div>
    );
  },
}));

vi.mock('../../components/ChatWindow', () => ({
  default: ({ thread }) => (
    <div data-testid="chat-window">
      {thread ? (
        <>
          <h3 data-testid="thread-title">{thread.title}</h3>
          {thread.project && (
            <div data-testid="thread-project-link">
              <a href={`/projets/${thread.project.id}`} data-testid="project-link">
                Voir le projet: {thread.project.titre}
              </a>
            </div>
          )}
        </>
      ) : (
        <p data-testid="no-thread">Aucun thread sélectionné</p>
      )}
    </div>
  ),
}));

vi.mock('../../utils/api', () => ({
  fetchAPI: vi.fn(),
  handleAPIError: vi.fn((err) => err.message || 'Erreur'),
}));

vi.mock('../../hooks/useWebSocket', () => ({
  useWebSocket: vi.fn(() => ({
    isConnected: true,
    sendMessage: vi.fn(),
    disconnect: vi.fn(),
  })),
}));

describe('Intégration Chat - Projets et Communautés', () => {
  const renderWithRouter = (router) => {
    return render(
      <EcoModeProvider>
        <LanguageProvider>
          <NotificationProvider>
            <RouterProvider router={router} />
          </NotificationProvider>
        </LanguageProvider>
      </EcoModeProvider>
    );
  };

  beforeEach(() => {
    vi.clearAllMocks();
    mockAuthState = {
      loading: false,
      token: 'test-token',
      user: mockUser,
      onLogout: vi.fn(),
    };
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('egoejo_lang', 'fr');
  });

  it('devrait afficher les threads de chat généralisé (sans projet)', async () => {
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      expect(screen.getByTestId('chat-list')).toBeInTheDocument();
      expect(screen.getByText('Chat généralisé')).toBeInTheDocument();
    });
  });

  it('devrait afficher les threads liés aux projets', async () => {
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      expect(screen.getByText('Chat Projet A')).toBeInTheDocument();
    });
  });

  it('devrait afficher les threads de communauté (multi-participants)', async () => {
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      expect(screen.getByText('Chat Communauté')).toBeInTheDocument();
    });
  });

  it('devrait permettre de sélectionner un thread lié à un projet et afficher le lien vers le projet', async () => {
    const user = userEvent.setup();
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      expect(screen.getByText('Chat Projet A')).toBeInTheDocument();
    });

    const projectThreadButton = screen.getByTestId('thread-2');
    await user.click(projectThreadButton);

    await waitFor(() => {
      expect(screen.getByTestId('thread-title')).toHaveTextContent('Chat Projet A');
      expect(screen.getByTestId('project-link')).toHaveTextContent('Voir le projet: Projet A');
      expect(screen.getByTestId('project-link')).toHaveAttribute('href', '/projets/1');
    });
  });

  it('devrait permettre de naviguer vers un projet depuis son chat', async () => {
    const user = userEvent.setup();
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      expect(screen.getByText('Chat Projet A')).toBeInTheDocument();
    });

    const projectThreadButton = screen.getByTestId('thread-2');
    await user.click(projectThreadButton);

    await waitFor(() => {
      const projectLink = screen.getByTestId('project-link');
      expect(projectLink).toBeInTheDocument();
      // Vérifier que le lien a le bon href
      expect(projectLink).toHaveAttribute('href', '/projets/1');
    });
  });

  it('devrait différencier les threads généralisés, projets et communautés', async () => {
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      // Vérifier que tous les types de threads sont présents
      expect(screen.getByText('Chat généralisé')).toBeInTheDocument();
      expect(screen.getByText('Chat Projet A')).toBeInTheDocument();
      expect(screen.getByText('Chat Communauté')).toBeInTheDocument();
    });
  });

  it('devrait mettre en évidence le thread sélectionné', async () => {
    const user = userEvent.setup();
    const router = createMemoryRouter(appRouter.routes, {
      initialEntries: ['/chat'],
    });

    renderWithRouter(router);

    await waitFor(() => {
      expect(screen.getByText('Chat généralisé')).toBeInTheDocument();
    });

    const generalThreadButton = screen.getByTestId('thread-1');
    await user.click(generalThreadButton);

    await waitFor(() => {
      expect(generalThreadButton).toHaveClass('is-active');
    });
  });
});

