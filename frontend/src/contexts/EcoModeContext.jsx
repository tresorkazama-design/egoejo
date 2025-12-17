/**
 * Contexte pour le mode éco-responsable
 * Réduit l'empreinte carbone en désactivant les animations et images haute définition
 */
import { createContext, useContext, useState, useEffect } from 'react';

const EcoModeContext = createContext();

export const EcoModeProvider = ({ children }) => {
  const [ecoMode, setEcoMode] = useState(() => {
    // Récupérer depuis localStorage
    if (typeof window !== 'undefined') {
      return localStorage.getItem('ecoMode') === 'true';
    }
    return false;
  });

  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Sauvegarder dans localStorage
    localStorage.setItem('ecoMode', ecoMode.toString());
    
    // Appliquer les classes CSS
    if (ecoMode) {
      document.documentElement.classList.add('eco-mode');
    } else {
      document.documentElement.classList.remove('eco-mode');
    }
  }, [ecoMode]);

  return (
    <EcoModeContext.Provider value={{ ecoMode, setEcoMode }}>
      {children}
    </EcoModeContext.Provider>
  );
};

export const useEcoMode = () => {
  const context = useContext(EcoModeContext);
  if (!context) {
    throw new Error('useEcoMode must be used within EcoModeProvider');
  }
  return context;
};

