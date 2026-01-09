
import { describe, it, expect } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
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

describe('Navigation', () => {
  it('devrait naviguer vers la page Univers', async () => {
    const user = userEvent.setup();
    renderRouter(['/']);

    const link = screen.getByRole('link', { name: /univers/i });
    await user.click(link);

    await waitFor(() => {
      expect(screen.getByTestId('univers-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait naviguer vers la page Projets', async () => {
    const user = userEvent.setup();
    renderRouter(['/']);

    // Il y a plusieurs liens "Projets" (navbar et footer), prenons celui de la navbar
    const links = screen.getAllByRole('link', { name: /projets/i });
    const navbarLink = links.find(link => link.closest('nav'));
    await user.click(navbarLink || links[0]);

    await waitFor(() => {
      expect(screen.getByTestId('projets-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait naviguer vers la page Rejoindre', async () => {
    const user = userEvent.setup();
    renderRouter(['/']);

    // Il y a deux liens "Rejoindre" (navbar et Home), prenons celui de la navbar
    const links = screen.getAllByRole('link', { name: /rejoindre/i });
    const navbarLink = links.find(link => link.closest('nav'));
    await user.click(navbarLink || links[0]);

    // Attendre que la page se charge (lazy loading)
    await waitFor(() => {
      expect(screen.getByTestId('rejoindre-page')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  it('devrait mettre en évidence le lien actif', async () => {
    renderRouter(['/univers']);
    await waitFor(() => {
      const activeLink = screen.getByRole('link', { name: /univers/i });
      expect(activeLink).toHaveAttribute('aria-current', 'page');
    }, { timeout: 3000 });
  });
});

