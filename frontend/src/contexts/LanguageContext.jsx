import { createContext, useContext, useState, useEffect } from 'react';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('fr');

  useEffect(() => {
    // Récupérer la langue depuis localStorage ou détecter depuis le navigateur
    const savedLang = localStorage.getItem('egoejo_lang');
    const supportedLangs = ['fr', 'en', 'ar', 'es', 'de', 'sw'];
    let finalLang = 'fr'; // Par défaut
    
    if (savedLang && supportedLangs.includes(savedLang)) {
      finalLang = savedLang;
    } else {
      // Détecter la langue du navigateur
      const browserLang = navigator.language.split('-')[0].toLowerCase();
      if (supportedLangs.includes(browserLang)) {
        finalLang = browserLang;
      }
      localStorage.setItem('egoejo_lang', finalLang);
    }
    
    setLanguage(finalLang);
    
    // Appliquer la direction RTL pour l'arabe
    if (finalLang === 'ar') {
      document.documentElement.setAttribute('dir', 'rtl');
      document.documentElement.setAttribute('lang', 'ar');
    } else {
      document.documentElement.setAttribute('dir', 'ltr');
      document.documentElement.setAttribute('lang', finalLang);
    }
  }, []);

  const changeLanguage = (lang) => {
    const supportedLangs = ['fr', 'en', 'ar', 'es', 'de', 'sw'];
    if (supportedLangs.includes(lang)) {
      setLanguage(lang);
      localStorage.setItem('egoejo_lang', lang);
      // Mettre à jour la direction du document pour l'arabe (RTL)
      if (lang === 'ar') {
        document.documentElement.setAttribute('dir', 'rtl');
        document.documentElement.setAttribute('lang', 'ar');
      } else {
        document.documentElement.setAttribute('dir', 'ltr');
        document.documentElement.setAttribute('lang', lang);
      }
    }
  };

  return (
    <LanguageContext.Provider value={{ language, changeLanguage }}>
      {children}
    </LanguageContext.Provider>
  );
};

