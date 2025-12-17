import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders } from '../../../test/test-utils';
import { NotFound } from '../NotFound';

describe('NotFound', () => {
  it('devrait afficher la page 404', () => {
    renderWithProviders(<NotFound />);
    expect(screen.getByTestId('not-found-page')).toBeInTheDocument();
  });

  it('devrait afficher le code 404', () => {
    renderWithProviders(<NotFound />);
    expect(screen.getByText('404')).toBeInTheDocument();
  });

  it('devrait afficher le message d\'erreur', () => {
    renderWithProviders(<NotFound />);
    expect(screen.getByText(/page non trouvée/i)).toBeInTheDocument();
  });

  it('devrait afficher un lien vers l\'accueil', () => {
    renderWithProviders(<NotFound />);
    const link = screen.getByRole('link', { name: /retour à l'accueil/i });
    expect(link).toHaveAttribute('href', '/');
  });
});

