import React from 'react';
import { logger } from '../utils/logger';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    logger.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      // Afficher un message d'erreur humain et utile
      return (
        <div 
          style={{ 
            padding: '3rem 2rem',
            textAlign: 'center',
            minHeight: '50vh',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: 'var(--surface)',
            borderRadius: 'var(--radius)',
            margin: '2rem',
            border: '1px solid var(--border)',
          }}
          role="alert"
          aria-live="assertive"
        >
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }} aria-hidden="true">
            ⚠️
          </div>
          <h2 style={{ 
            margin: 0, 
            marginBottom: '1rem', 
            fontSize: '1.5rem',
            fontWeight: '600',
            color: 'var(--text)',
          }}>
            Oups, quelque chose s'est mal passé
          </h2>
          <p style={{ 
            margin: 0, 
            marginBottom: '2rem', 
            fontSize: '1rem',
            color: 'var(--muted)',
            maxWidth: '500px',
            lineHeight: 1.6,
          }}>
            Une erreur inattendue s'est produite. Notre équipe a été notifiée.
            Vous pouvez rafraîchir la page ou revenir à l'accueil.
          </p>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', justifyContent: 'center' }}>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: 'var(--accent)',
                color: 'white',
                border: 'none',
                borderRadius: 'var(--radius)',
                fontSize: '0.875rem',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'opacity 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
            >
              Rafraîchir la page
            </button>
            <a
              href="/"
              style={{
                padding: '0.75rem 1.5rem',
                backgroundColor: 'transparent',
                color: 'var(--accent)',
                border: '1px solid var(--accent)',
                borderRadius: 'var(--radius)',
                fontSize: '0.875rem',
                fontWeight: '500',
                textDecoration: 'none',
                transition: 'opacity 0.2s',
              }}
              onMouseEnter={(e) => e.currentTarget.style.opacity = '0.9'}
              onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
            >
              Retour à l'accueil
            </a>
          </div>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details style={{ 
              marginTop: '2rem', 
              textAlign: 'left',
              maxWidth: '600px',
              width: '100%',
            }}>
              <summary style={{ 
                cursor: 'pointer', 
                color: 'var(--muted)',
                fontSize: '0.875rem',
                marginBottom: '0.5rem',
              }}>
                Détails techniques (mode développement)
              </summary>
              <pre style={{ 
                padding: '1rem',
                backgroundColor: 'var(--bg)',
                borderRadius: 'var(--radius)',
                fontSize: '0.75rem',
                overflow: 'auto',
                color: 'var(--text)',
              }}>
                {this.state.error.toString()}
                {this.state.errorInfo && `\n\n${this.state.errorInfo.componentStack}`}
              </pre>
            </details>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

