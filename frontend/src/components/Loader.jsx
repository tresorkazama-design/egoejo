import React from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../utils/i18n';
import { zIndexLayers } from '../design-tokens';

export const Loader = ({ 
  size = 'medium', 
  color = 'primary',
  fullScreen = false,
  message = null,
  className = ''
}) => {
  const { language } = useLanguage();
  const sizeStyles = {
    small: { width: '16px', height: '16px' },
    medium: { width: '32px', height: '32px' },
    large: { width: '48px', height: '48px' }
  };

  const colorStyles = {
    primary: { borderColor: 'var(--accent)' },
    secondary: { borderColor: 'var(--muted)' },
    white: { borderColor: 'var(--text)' }
  };

  const loader = (
    <div className={`loader-wrapper ${className}`} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'transparent', backgroundColor: 'transparent' }}>
      <div
        className="loader-spinner"
        style={{
          ...sizeStyles[size],
          ...colorStyles[color],
          border: '4px solid',
          borderTopColor: 'transparent',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          background: 'transparent',
          backgroundColor: 'transparent'
        }}
        role="status"
        aria-label={message || t("common.loading", language)}
        aria-live="polite"
        aria-busy="true"
      />
      {message && (
        <p style={{ marginTop: '16px', fontSize: '0.875rem', color: 'var(--muted)', background: 'transparent', backgroundColor: 'transparent' }} aria-live="polite" aria-atomic="true">{message}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div style={{ 
        position: 'fixed', 
        inset: 0, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        backgroundColor: 'rgba(5, 6, 7, 0.8)', 
        zIndex: zIndexLayers.overlay, // Utiliser z-index centralisé
        background: 'rgba(5, 6, 7, 0.8)'
      }}>
        {loader}
      </div>
    );
  }

  return loader;
};

