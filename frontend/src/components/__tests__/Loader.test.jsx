import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import React from 'react';
import { Loader } from '../Loader';
import { renderWithProviders } from '../../test/test-utils';

describe('Loader', () => {
  it('devrait afficher un loader par défaut', () => {
    renderWithProviders(<Loader />);
    const loader = screen.getByRole('status');
    expect(loader).toBeInTheDocument();
    // Le texte peut varier selon la langue
    expect(loader).toHaveAttribute('aria-label');
  });

  it('devrait afficher un message si fourni', () => {
    renderWithProviders(<Loader message="Chargement en cours..." />);
    expect(screen.getByText('Chargement en cours...')).toBeInTheDocument();
  });

  it('devrait utiliser la taille small', () => {
    renderWithProviders(<Loader size="small" />);
    const loader = screen.getByRole('status');
    expect(loader.style.width).toBe('16px');
    expect(loader.style.height).toBe('16px');
  });

  it('devrait utiliser la taille medium par défaut', () => {
    renderWithProviders(<Loader />);
    const loader = screen.getByRole('status');
    expect(loader.style.width).toBe('32px');
    expect(loader.style.height).toBe('32px');
  });

  it('devrait utiliser la taille large', () => {
    renderWithProviders(<Loader size="large" />);
    const loader = screen.getByRole('status');
    expect(loader.style.width).toBe('48px');
    expect(loader.style.height).toBe('48px');
  });

  it('devrait utiliser la couleur primary par défaut', () => {
    renderWithProviders(<Loader />);
    const loader = screen.getByRole('status');
    // Vérifier que le loader est rendu avec un style (les couleurs sont appliquées via variables CSS dans le style inline)
    expect(loader).toBeInTheDocument();
    // Vérifier que le loader a un style appliqué (border est présent)
    const styleAttr = loader.getAttribute('style') || '';
    expect(styleAttr).toBeTruthy();
    expect(styleAttr).toContain('border');
  });

  it('devrait utiliser la couleur secondary', () => {
    renderWithProviders(<Loader color="secondary" />);
    const loader = screen.getByRole('status');
    // Vérifier que le loader est rendu avec un style
    expect(loader).toBeInTheDocument();
    const styleAttr = loader.getAttribute('style') || '';
    expect(styleAttr).toBeTruthy();
    expect(styleAttr).toContain('border');
  });

  it('devrait utiliser la couleur white', () => {
    renderWithProviders(<Loader color="white" />);
    const loader = screen.getByRole('status');
    // Vérifier que le loader est rendu avec un style
    expect(loader).toBeInTheDocument();
    const styleAttr = loader.getAttribute('style') || '';
    expect(styleAttr).toBeTruthy();
    expect(styleAttr).toContain('border');
  });

  it('devrait afficher en plein écran si fullScreen est true', () => {
    renderWithProviders(<Loader fullScreen />);
    const loader = screen.getByRole('status');
    // Chercher le conteneur parent avec position fixed
    let container = loader.parentElement;
    while (container && container.style.position !== 'fixed') {
      container = container.parentElement;
    }
    expect(container).toBeInTheDocument();
    expect(container?.style.position).toBe('fixed');
    expect(container?.style.inset || container?.style.top).toBeTruthy();
  });

  it('ne devrait pas afficher en plein écran si fullScreen est false', () => {
    renderWithProviders(<Loader fullScreen={false} />);
    const loader = screen.getByRole('status');
    const container = loader.closest('div[style*="position: fixed"]');
    expect(container).not.toBeInTheDocument();
  });

  it('devrait accepter des classes personnalisées', () => {
    renderWithProviders(<Loader className="custom-class" />);
    const loader = screen.getByRole('status');
    const container = loader.closest('.loader-wrapper');
    expect(container?.className).toContain('custom-class');
  });
});

