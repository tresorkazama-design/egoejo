import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter, MemoryRouter } from 'react-router-dom';
import React from 'react';
import { Navbar } from '../Navbar';

const renderWithRouter = (component, { route = '/' } = {}) => {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {component}
    </MemoryRouter>
  );
};

describe('Navbar', () => {
  it('devrait afficher le logo', () => {
    renderWithRouter(<Navbar />);
    expect(screen.getByText('EGOEJO')).toBeInTheDocument();
  });

  it('devrait afficher un logo personnalisé', () => {
    renderWithRouter(<Navbar logo="Mon Logo" />);
    expect(screen.getByText('Mon Logo')).toBeInTheDocument();
  });

  it('devrait afficher les liens de navigation par défaut', () => {
    renderWithRouter(<Navbar />);
    expect(screen.getByText('Accueil')).toBeInTheDocument();
    expect(screen.getByText('Univers')).toBeInTheDocument();
    expect(screen.getByText('Vision')).toBeInTheDocument();
    expect(screen.getByText('Alliances')).toBeInTheDocument();
    expect(screen.getByText('Projets')).toBeInTheDocument();
    expect(screen.getByText('Rejoindre')).toBeInTheDocument();
  });

  it('devrait afficher les liens personnalisés', () => {
    const customLinks = [
      { path: '/custom1', label: 'Custom 1' },
      { path: '/custom2', label: 'Custom 2' }
    ];
    renderWithRouter(<Navbar links={customLinks} />);
    expect(screen.getByText('Custom 1')).toBeInTheDocument();
    expect(screen.getByText('Custom 2')).toBeInTheDocument();
    expect(screen.queryByText('Accueil')).not.toBeInTheDocument();
  });

  it('devrait mettre en évidence le lien actif', () => {
    renderWithRouter(<Navbar />, { route: '/projets' });
    const activeLink = screen.getByText('Projets');
    expect(activeLink).toHaveAttribute('aria-current', 'page');
    expect(activeLink.className).toContain('bg-blue-600');
  });

  it('devrait ouvrir/fermer le menu mobile', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Navbar />);
    
    const menuButton = screen.getByLabelText('Toggle menu');
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
    
    await user.click(menuButton);
    expect(menuButton).toHaveAttribute('aria-expanded', 'true');
    
    await user.click(menuButton);
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('devrait appeler onMenuToggle quand le menu est ouvert/fermé', async () => {
    const user = userEvent.setup();
    const onMenuToggle = vi.fn();
    renderWithRouter(<Navbar onMenuToggle={onMenuToggle} />);
    
    const menuButton = screen.getByLabelText('Toggle menu');
    await user.click(menuButton);
    
    expect(onMenuToggle).toHaveBeenCalledWith(true);
    
    await user.click(menuButton);
    expect(onMenuToggle).toHaveBeenCalledWith(false);
  });

  it('devrait fermer le menu mobile quand on clique sur un lien', async () => {
    const user = userEvent.setup();
    renderWithRouter(<Navbar />);
    
    const menuButton = screen.getByLabelText('Toggle menu');
    await user.click(menuButton);
    
    // Il y a deux éléments "Projets" (desktop et mobile), prenons celui du menu mobile
    const links = screen.getAllByText('Projets');
    const mobileLink = links.find(link => link.closest('.md\\:hidden'));
    await user.click(mobileLink || links[0]);
    
    expect(menuButton).toHaveAttribute('aria-expanded', 'false');
  });

  it('devrait avoir un attribut role="navigation"', () => {
    renderWithRouter(<Navbar />);
    const nav = screen.getByRole('navigation');
    expect(nav).toHaveAttribute('aria-label', 'Navigation principale');
  });

  it('devrait accepter des classes personnalisées', () => {
    renderWithRouter(<Navbar className="custom-nav" />);
    const nav = screen.getByRole('navigation');
    expect(nav.className).toContain('custom-nav');
  });
});

