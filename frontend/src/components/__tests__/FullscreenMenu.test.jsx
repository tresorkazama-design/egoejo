import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import { FullscreenMenu } from '../FullscreenMenu';

describe('FullscreenMenu', () => {
  beforeEach(() => {
    document.body.style.overflow = '';
  });

  afterEach(() => {
    document.body.style.overflow = '';
  });

  it('ne devrait pas s\'afficher si isOpen est false', () => {
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={false} onClose={vi.fn()} />
      </MemoryRouter>
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('devrait s\'afficher si isOpen est true', () => {
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('devrait appeler onClose quand on clique sur le bouton fermer', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={onClose} />
      </MemoryRouter>
    );

    const closeButton = screen.getByLabelText('Fermer le menu');
    await user.click(closeButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('devrait appeler onClose quand on appuie sur ESC', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={onClose} />
      </MemoryRouter>
    );

    await user.keyboard('{Escape}');

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('devrait appeler onClose quand on clique sur un lien', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={onClose} />
      </MemoryRouter>
    );

    const link = screen.getByText('Accueil');
    await user.click(link);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('devrait afficher les liens par défaut', () => {
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(screen.getByText('Accueil')).toBeInTheDocument();
    expect(screen.getByText('Univers')).toBeInTheDocument();
    expect(screen.getByText('Vision')).toBeInTheDocument();
  });

  it('devrait afficher les liens personnalisés', () => {
    const customLinks = [
      { path: '/custom1', label: 'Custom 1' },
      { path: '/custom2', label: 'Custom 2' }
    ];
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} links={customLinks} />
      </MemoryRouter>
    );

    expect(screen.getByText('Custom 1')).toBeInTheDocument();
    expect(screen.getByText('Custom 2')).toBeInTheDocument();
    expect(screen.queryByText('Accueil')).not.toBeInTheDocument();
  });

  it('devrait mettre en évidence le lien actif', () => {
    render(
      <MemoryRouter initialEntries={['/projets']}>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    const activeLink = screen.getByText('Projets');
    expect(activeLink).toHaveAttribute('aria-current', 'page');
    expect(activeLink.className).toContain('text-blue-400');
  });

  it('devrait bloquer le scroll du body quand ouvert', () => {
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(document.body.style.overflow).toBe('hidden');
  });

  it('devrait restaurer le scroll du body quand fermé', () => {
    const { rerender } = render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(document.body.style.overflow).toBe('hidden');

    rerender(
      <MemoryRouter>
        <FullscreenMenu isOpen={false} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(document.body.style.overflow).toBe('');
  });

  it('devrait avoir un attribut aria-modal', () => {
    render(
      <MemoryRouter>
        <FullscreenMenu isOpen={true} onClose={vi.fn()} />
      </MemoryRouter>
    );

    expect(screen.getByRole('dialog')).toHaveAttribute('aria-modal', 'true');
  });
});

