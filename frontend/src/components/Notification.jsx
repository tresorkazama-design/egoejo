import React, { useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../utils/i18n';

export default function Notification({ message, type = 'success', onClose, duration = 5000 }) {
  const { language } = useLanguage();

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const typeStyles = {
    success: {
      background: 'rgba(0, 245, 160, 0.15)',
      border: '1px solid rgba(0, 245, 160, 0.3)',
      color: 'var(--accent)',
    },
    error: {
      background: 'rgba(255, 0, 0, 0.1)',
      border: '1px solid rgba(255, 0, 0, 0.3)',
      color: '#ff6b6b',
    },
    info: {
      background: 'rgba(13, 228, 255, 0.15)',
      border: '1px solid rgba(13, 228, 255, 0.3)',
      color: '#0de4ff',
    },
  };

  const style = typeStyles[type] || typeStyles.success;

  return (
    <div
      className="notification"
      style={style}
      role="alert"
      aria-live="polite"
    >
      <div className="notification__content">
        <p className="notification__message">{message}</p>
        <button
          type="button"
          className="notification__close"
          onClick={onClose}
          aria-label={t('common.close', language)}
        >
          ×
        </button>
      </div>
    </div>
  );
}

