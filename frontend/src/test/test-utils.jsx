import React from 'react';
import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { LanguageProvider } from '../contexts/LanguageContext';
import { AuthProvider } from '../contexts/AuthContext';
import { NotificationProvider } from '../contexts/NotificationContext';
import { EcoModeProvider } from '../contexts/EcoModeContext';

// Liste de toutes les langues supportées
export const SUPPORTED_LANGUAGES = ['fr', 'en', 'ar', 'es', 'de', 'sw'];

/**
 * Helper pour rendre des composants avec tous les providers nécessaires
 * Cela garantit que les tests fonctionnent sans casser le visuel
 * Supporte toutes les langues du projet
 */
export const renderWithProviders = (ui, options = {}) => {
  const {
    language = 'fr',
    user = null,
    ...renderOptions
  } = options;

  const Wrapper = ({ children }) => {
    // Forcer la langue dans localStorage pour les tests
    if (typeof window !== 'undefined') {
      localStorage.setItem('egoejo_lang', language);
      // Éviter la détection automatique de la langue du navigateur
      Object.defineProperty(navigator, 'language', {
        writable: true,
        value: language === 'ar' ? 'ar-SA' : language === 'fr' ? 'fr-FR' : 'en-US'
      });
    }
    
    return (
      <BrowserRouter>
        <EcoModeProvider>
          <LanguageProvider>
            <AuthProvider>
              <NotificationProvider>
                {children}
              </NotificationProvider>
            </AuthProvider>
          </LanguageProvider>
        </EcoModeProvider>
      </BrowserRouter>
    );
  };

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

/**
 * Helper pour tester avec toutes les langues
 * Exécute le test avec chaque langue supportée
 */
export const testWithAllLanguages = (testFn) => {
  SUPPORTED_LANGUAGES.forEach((lang) => {
    testFn(lang);
  });
};

/**
 * Helper pour rendre avec seulement le router (pour les tests simples)
 */
export const renderWithRouter = (ui) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

// Réexporter tout depuis @testing-library/react
export * from '@testing-library/react';

