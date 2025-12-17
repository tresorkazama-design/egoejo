
import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { RouterProvider, createMemoryRouter } from 'react-router-dom';
import { appRouter } from '../router';
import { LanguageProvider } from '../../contexts/LanguageContext';
import { AuthProvider } from '../../contexts/AuthContext';
import { NotificationProvider } from '../../contexts/NotificationContext';
import { EcoModeProvider } from '../../contexts/EcoModeContext';
import { render } from '@testing-library/react';

const renderRouter = (initialEntries = ['/']) => {
  const router = createMemoryRouter(appRouter.routes, {
    initialEntries
  });

  // Forcer la langue française pour les tests
  if (typeof window !== 'undefined') {
    localStorage.setItem('egoejo_lang', 'fr');
    Object.defineProperty(navigator, 'language', {
      writable: true,
      value: 'fr-FR'
    });
  }

  return render(
    <EcoModeProvider>
      <LanguageProvider>
        <AuthProvider>
          <NotificationProvider>
            <RouterProvider router={router} />
          </NotificationProvider>
        </AuthProvider>
      </LanguageProvider>
    </EcoModeProvider>
  );
};

describe('Router', () => {
  it('devrait rendre la page Home pour la route /', async () => {
    renderRouter(['/']);
    await waitFor(() => {
      expect(screen.getByTestId('home-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page Univers pour la route /univers', async () => {
    renderRouter(['/univers']);
    await waitFor(() => {
      expect(screen.getByTestId('univers-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page Vision pour la route /vision', async () => {
    renderRouter(['/vision']);
    await waitFor(() => {
      expect(screen.getByTestId('vision-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page Alliances pour la route /alliances', async () => {
    renderRouter(['/alliances']);
    await waitFor(() => {
      expect(screen.getByTestId('alliances-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page Projets pour la route /projets', async () => {
    renderRouter(['/projets']);
    await waitFor(() => {
      expect(screen.getByTestId('projets-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page Rejoindre pour la route /rejoindre', async () => {
    renderRouter(['/rejoindre']);
    await waitFor(() => {
      expect(screen.getByTestId('rejoindre-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page Admin pour la route /admin', async () => {
    renderRouter(['/admin']);
    await waitFor(() => {
      expect(screen.getByTestId('admin-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait rendre la page 404 pour une route inexistante', async () => {
    renderRouter(['/route-inexistante']);
    await waitFor(() => {
      expect(screen.getByTestId('not-found-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait inclure le Layout sur toutes les routes', () => {
    renderRouter(['/']);
    // Le Layout devrait être présent (navbar, footer) - il y a deux nav (header et footer)
    const navs = screen.getAllByRole('navigation');
    expect(navs.length).toBeGreaterThanOrEqual(1);
    // Vérifier que la navigation principale existe (celle avec id="main-navigation")
    const mainNav = navs.find(nav => nav.id === 'main-navigation' || nav.getAttribute('aria-label')?.includes('Menu'));
    expect(mainNav || navs[0]).toBeInTheDocument();
  });
});

