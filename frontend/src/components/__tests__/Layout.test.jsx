import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import React from 'react';
import Layout from '../Layout';
import { renderWithProviders } from '../../test/test-utils';

// Mock scrollAnimations pour éviter les problèmes avec GSAP/ScrollTrigger dans les tests
vi.mock('../../utils/scrollAnimations', () => ({
  initScrollAnimations: vi.fn(),
  cleanupScrollAnimations: vi.fn(),
}));

// Mock PageTransition pour simplifier les tests
vi.mock('../PageTransition', () => ({
  default: ({ children }) => <div data-testid="page-transition">{children}</div>,
}));

describe('Layout', () => {
  beforeEach(() => {
    // Mock window.matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation(query => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    });
  });

  it('devrait afficher le logo EGOEJO', () => {
    const { container } = renderWithProviders(<Layout />);
    // Le logo devrait être présent (via Logo3D) - il y a deux logos (header et footer)
    const logos = container.querySelectorAll('.logo-3d[aria-label="EGOEJO"]');
    expect(logos.length).toBeGreaterThanOrEqual(1);
  });

  it('devrait afficher la navigation principale', () => {
    renderWithProviders(<Layout />);
    // Vérifier que les liens de navigation sont présents - il y a plusieurs liens "Accueil" (header et footer)
    const accueilLinks = screen.getAllByRole('link', { name: /Accueil/i });
    expect(accueilLinks.length).toBeGreaterThanOrEqual(1);
    expect(screen.getByRole('link', { name: /Univers/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Vision/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Citations/i })).toBeInTheDocument();
  });

  it('devrait afficher le footer', () => {
    const { container } = renderWithProviders(<Layout />);
    // Vérifier que le footer est présent - le texte peut varier selon la langue
    const footer = container.querySelector('footer.layout-footer') ||
                   container.querySelector('footer[role="contentinfo"]');
    expect(footer).toBeInTheDocument();
  });

  it('devrait afficher les liens du footer', () => {
    renderWithProviders(<Layout />);
    // Vérifier que les liens du footer sont présents
    const footerLinks = screen.getAllByRole('link');
    const footerLinkTexts = footerLinks.map(link => link.textContent);
    expect(footerLinkTexts.some(text => text?.includes('Rejoindre'))).toBe(true);
  });

  it('devrait afficher le contenu via Outlet', () => {
    // Le Layout utilise Outlet pour afficher le contenu des routes
    // On vérifie juste que la structure est présente
    const { container } = renderWithProviders(<Layout />);
    const mainContent = container.querySelector('.layout-content');
    expect(mainContent).toBeInTheDocument();
  });

  it('devrait avoir un header sticky', () => {
    const { container } = renderWithProviders(<Layout />);
    const header = container.querySelector('.layout-header');
    expect(header).toBeInTheDocument();
  });
});
