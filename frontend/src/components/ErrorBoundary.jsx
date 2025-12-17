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
      // En cas d'erreur, retourner null pour ne rien afficher (fond transparent)
      // ou retourner un fallback minimal transparent
      return (
        <div style={{ 
          background: 'transparent', 
          backgroundColor: 'transparent',
          minHeight: '100vh',
          width: '100%'
        }} />
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

