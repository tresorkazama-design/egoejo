import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';

// Composant ErrorBoundary de base pour les tests
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Log l'erreur (peut être mocké pour les tests)
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div role="alert">
          <h2>Une erreur s'est produite</h2>
          {this.props.showDetails && this.state.error && (
            <p>{this.state.error.message}</p>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

// Composant qui lance une erreur pour les tests
const ThrowError = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Erreur de test');
  }
  return <div>Pas d'erreur</div>;
};

describe('ErrorBoundary', () => {
  let consoleError;

  beforeEach(() => {
    // Supprimer les erreurs console attendues de React
    consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    consoleError.mockRestore();
  });

  it('devrait afficher les enfants normalement quand il n\'y a pas d\'erreur', () => {
    render(
      <ErrorBoundary>
        <div>Contenu normal</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Contenu normal')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('devrait capturer les erreurs et afficher un message d\'erreur', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText("Une erreur s'est produite")).toBeInTheDocument();
  });

  it('devrait afficher les détails de l\'erreur si showDetails est true', () => {
    render(
      <ErrorBoundary showDetails={true}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Erreur de test')).toBeInTheDocument();
  });

  it('devrait utiliser le fallback personnalisé si fourni', () => {
    const CustomFallback = () => <div>Erreur personnalisée</div>;

    render(
      <ErrorBoundary fallback={<CustomFallback />}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(screen.getByText('Erreur personnalisée')).toBeInTheDocument();
    expect(screen.queryByText("Une erreur s'est produite")).not.toBeInTheDocument();
  });

  it('devrait appeler onError callback quand une erreur est capturée', () => {
    const onError = vi.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalled();
    expect(onError.mock.calls[0][0]).toBeInstanceOf(Error);
    expect(onError.mock.calls[0][0].message).toBe('Erreur de test');
  });
});

