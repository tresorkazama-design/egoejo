import React, { useState, useRef, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { t } from '../utils/i18n';

export default function LanguageSelector() {
  const { language, changeLanguage } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const languages = [
    { code: 'fr', label: 'FR', fullName: 'Français', ariaLabel: 'Français' },
    { code: 'en', label: 'EN', fullName: 'English', ariaLabel: 'English' },
    { code: 'es', label: 'ES', fullName: 'Español', ariaLabel: 'Español' },
    { code: 'de', label: 'DE', fullName: 'Deutsch', ariaLabel: 'Deutsch' },
    { code: 'ar', label: 'AR', fullName: 'العربية', ariaLabel: 'العربية' },
    { code: 'sw', label: 'SW', fullName: 'Kiswahili', ariaLabel: 'Kiswahili' },
  ];

  const currentLanguage = languages.find(lang => lang.code === language) || languages[0];

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

  const handleLanguageChange = (langCode) => {
    changeLanguage(langCode);
    setIsOpen(false);
  };

  return (
    <div className="language-selector" ref={dropdownRef}>
      <button
        type="button"
        className="language-selector__toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="listbox"
        aria-label={t("nav.languages", language) + " - " + currentLanguage.fullName}
        aria-controls="language-menu"
      >
        <span className="language-selector__label" aria-hidden="true">{t("nav.languages", language).toUpperCase()}</span>
        <span className="language-selector__current" aria-hidden="true">{currentLanguage.label}</span>
        <svg
          width="12"
          height="12"
          viewBox="0 0 12 12"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className={`language-selector__icon ${isOpen ? 'is-open' : ''}`}
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
        <div className="language-selector__menu" id="language-menu" role="listbox" aria-label={t("nav.languages", language)}>
          {languages.map((lang) => (
            <button
              key={lang.code}
              type="button"
              className={`language-selector__option ${language === lang.code ? "is-active" : ""}`}
              onClick={() => handleLanguageChange(lang.code)}
              aria-label={lang.ariaLabel}
              role="option"
              aria-selected={language === lang.code}
            >
              <span className="language-selector__option-label" aria-hidden="true">{lang.label}</span>
              <span className="language-selector__option-name">{lang.fullName}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

