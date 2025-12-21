/**
 * Sélecteur de niveau de sobriété (1-5) avec dropdown
 * Remplace le simple toggle par un sélecteur complet avec informations
 */
import { useState, useRef, useEffect } from 'react';
import { useEcoMode } from '../contexts/EcoModeContext';
import { useLanguage } from '../contexts/LanguageContext';
import { SobrietyLevel, zIndexLayers, sobrietyConfig } from '../design-tokens';
import { t } from '../utils/i18n';

export const EcoModeToggle = () => {
  const { sobrietyLevel, setSobrietyLevel, sobrietyConfig: currentConfig } = useEcoMode();
  const { language } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Niveaux disponibles avec descriptions
  const levels = [
    {
      level: SobrietyLevel.FULL,
      name: sobrietyConfig[SobrietyLevel.FULL].name,
      description: sobrietyConfig[SobrietyLevel.FULL].description,
      icon: '✨',
      performance: sobrietyConfig[SobrietyLevel.FULL].performance,
      impact: 'Performance maximale',
    },
    {
      level: SobrietyLevel.SIMPLIFIED,
      name: sobrietyConfig[SobrietyLevel.SIMPLIFIED].name,
      description: sobrietyConfig[SobrietyLevel.SIMPLIFIED].description,
      icon: '🎨',
      performance: sobrietyConfig[SobrietyLevel.SIMPLIFIED].performance,
      impact: 'Performance élevée',
    },
    {
      level: SobrietyLevel.FLAT,
      name: sobrietyConfig[SobrietyLevel.FLAT].name,
      description: sobrietyConfig[SobrietyLevel.FLAT].description,
      icon: '🖼️',
      performance: sobrietyConfig[SobrietyLevel.FLAT].performance,
      impact: 'Performance moyenne',
    },
    {
      level: SobrietyLevel.MINIMAL,
      name: sobrietyConfig[SobrietyLevel.MINIMAL].name,
      description: sobrietyConfig[SobrietyLevel.MINIMAL].description,
      icon: '🌿',
      performance: sobrietyConfig[SobrietyLevel.MINIMAL].performance,
      impact: 'Performance faible',
    },
    {
      level: SobrietyLevel.TEXT_ONLY,
      name: sobrietyConfig[SobrietyLevel.TEXT_ONLY].name,
      description: sobrietyConfig[SobrietyLevel.TEXT_ONLY].description,
      icon: '📝',
      performance: sobrietyConfig[SobrietyLevel.TEXT_ONLY].performance,
      impact: 'Performance minimale',
    },
  ];

  const currentLevel = levels.find(l => l.level === sobrietyLevel) || levels[0];

  // Fermer le menu si on clique en dehors
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const handleLevelChange = (level) => {
    setSobrietyLevel(level);
    setIsOpen(false);
  };

  return (
    <div 
      className="eco-mode-toggle" 
      ref={dropdownRef}
      style={{
        position: 'fixed',
        bottom: '20px',
        right: '20px',
        zIndex: zIndexLayers.floating,
      }}
    >
      <button
        type="button"
        className="eco-mode-toggle__button"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-label={`Niveau de sobriété : ${currentLevel.name} (${currentLevel.description})`}
        aria-controls="sobriety-menu"
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '10px 15px',
          backgroundColor: 'rgba(0, 0, 0, 0.85)',
          border: '1px solid rgba(0, 245, 160, 0.3)',
          borderRadius: '8px',
          cursor: 'pointer',
          color: '#fff',
          fontSize: '14px',
          transition: 'all 0.2s ease',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.95)';
          e.currentTarget.style.borderColor = 'rgba(0, 245, 160, 0.5)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'rgba(0, 0, 0, 0.85)';
          e.currentTarget.style.borderColor = 'rgba(0, 245, 160, 0.3)';
        }}
      >
        <span style={{ fontSize: '16px' }}>{currentLevel.icon}</span>
        <span>
          <strong>{t('eco_mode.label', language) || 'Sobriété'}</strong> : Niveau {sobrietyLevel}
        </span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          style={{
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
            transition: 'transform 0.2s ease',
          }}
          aria-hidden="true"
        >
          <path
            d="M3 4.5L6 7.5L9 4.5"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>

      {isOpen && (
        <div
          id="sobriety-menu"
          role="listbox"
          aria-label="Sélectionner un niveau de sobriété"
          style={{
            position: 'absolute',
            bottom: '100%',
            right: 0,
            marginBottom: '8px',
            minWidth: '280px',
            backgroundColor: 'rgba(5, 6, 7, 0.98)',
            border: '1px solid rgba(0, 245, 160, 0.3)',
            borderRadius: '8px',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.5)',
            overflow: 'hidden',
            zIndex: zIndexLayers.dropdown,
          }}
        >
          <div style={{ padding: '8px 12px', borderBottom: '1px solid rgba(0, 245, 160, 0.2)', fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)' }}>
            Choisir un niveau de sobriété
          </div>
          {levels.map((level) => (
            <button
              key={level.level}
              type="button"
              className={`sobriety-level-option ${sobrietyLevel === level.level ? 'is-active' : ''}`}
              onClick={() => handleLevelChange(level.level)}
              role="option"
              aria-selected={sobrietyLevel === level.level}
              style={{
                width: '100%',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px',
                padding: '12px 16px',
                backgroundColor: sobrietyLevel === level.level 
                  ? 'rgba(0, 245, 160, 0.15)' 
                  : 'transparent',
                border: 'none',
                borderBottom: '1px solid rgba(0, 245, 160, 0.1)',
                cursor: 'pointer',
                color: '#fff',
                textAlign: 'left',
                transition: 'background-color 0.2s ease',
              }}
              onMouseEnter={(e) => {
                if (sobrietyLevel !== level.level) {
                  e.currentTarget.style.backgroundColor = 'rgba(0, 245, 160, 0.08)';
                }
              }}
              onMouseLeave={(e) => {
                if (sobrietyLevel !== level.level) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '18px' }}>{level.icon}</span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '2px' }}>
                    <strong style={{ fontSize: '14px' }}>
                      Niveau {level.level} : {level.name}
                    </strong>
                    {sobrietyLevel === level.level && (
                      <span style={{ fontSize: '12px', color: '#00f5a0' }}>✓ Actif</span>
                    )}
                  </div>
                  <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.7)', marginTop: '2px' }}>
                    {level.description}
                  </div>
                </div>
              </div>
              <div style={{ fontSize: '11px', color: 'rgba(255, 255, 255, 0.5)', marginTop: '4px', display: 'flex', justifyContent: 'space-between' }}>
                <span>Performance : {level.performance}</span>
                <span>{level.impact}</span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

