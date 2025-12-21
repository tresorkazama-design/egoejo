import React, { useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { zIndexLayers } from '../design-tokens';

export const FullscreenMenu = ({ 
  isOpen, 
  onClose,
  links = [],
  className = ''
}) => {
  const location = useLocation();

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.body.style.overflow = 'hidden';
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.body.style.overflow = '';
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  const defaultLinks = [
    { path: '/', label: 'Accueil' },
    { path: '/univers', label: 'Univers' },
    { path: '/vision', label: 'Vision' },
    { path: '/alliances', label: 'Alliances' },
    { path: '/projets', label: 'Projets' },
    { path: '/rejoindre', label: 'Rejoindre' }
  ];

  const menuLinks = links.length > 0 ? links : defaultLinks;

  if (!isOpen) return null;

  return (
    <div
      className={`fixed inset-0 bg-black bg-opacity-95 flex items-center justify-center ${className}`}
      style={{ zIndex: zIndexLayers.modal }} // Utiliser z-index centralisé
      role="dialog"
      aria-modal="true"
      aria-label="Menu plein écran"
    >
      <button
        onClick={onClose}
        className="absolute top-4 right-4 text-white text-4xl hover:text-gray-300"
        aria-label="Fermer le menu"
      >
        ×
      </button>

      <nav className="flex flex-col items-center space-y-6">
        {menuLinks.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            onClick={onClose}
            className={`text-3xl font-bold transition-colors ${
              location.pathname === link.path
                ? 'text-blue-400'
                : 'text-white hover:text-blue-400'
            }`}
            aria-current={location.pathname === link.path ? 'page' : undefined}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </div>
  );
};

