import React from 'react';
import ReactDOM from 'react-dom/client';
import { RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { appRouter } from './app/router';
import { AuthProvider } from './contexts/AuthContext';
import { LanguageProvider } from './contexts/LanguageContext';
import { NotificationProvider } from './contexts/NotificationContext';
import { EcoModeProvider } from './contexts/EcoModeContext';
import { useEasterEgg } from './hooks/useEasterEgg';
import { logger } from './utils/logger';
import { initPerformanceTracking } from './utils/performance-metrics';
import './styles/global.css';
import './styles/eco-mode.css';

// Configuration React Query avec stale-while-revalidate
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes - données considérées fraîches (stale-while-revalidate)
      gcTime: 10 * 60 * 1000, // 10 minutes - données gardées en cache (anciennement cacheTime)
      refetchOnWindowFocus: false, // Ne pas refetch au focus de la fenêtre
      refetchOnReconnect: true, // Refetch si reconnexion réseau
      retry: 2, // Retry 2 fois en cas d'erreur
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Backoff exponentiel
    },
  },
});

// Composant wrapper pour l'easter egg
const AppWrapper = ({ children }) => {
  useEasterEgg();
  return <>{children}</>;
};

// Initialiser Sentry en production si configuré
// Import conditionnel pour éviter l'analyse de Vite en développement
if (import.meta.env.PROD) {
  import('./utils/sentry').then(({ initSentry }) => {
    initSentry();
  }).catch(() => {
    // Ignorer silencieusement si Sentry n'est pas disponible
  });
}

// Initialiser le tracking des métriques de performance
initPerformanceTracking();

// Initialiser le monitoring complet (Sentry, métriques, alertes)
if (import.meta.env.PROD) {
  import('./utils/monitoring').then(({ initMonitoring }) => {
    initMonitoring();
  }).catch(() => {
    // Ignorer silencieusement si le monitoring n'est pas disponible
  });
}

// Point d'entrée principal de l'application React
const rootElement = document.getElementById('root');

if (!rootElement) {
  logger.error("Impossible de trouver l'élément #root dans index.html");
  throw new Error("L'élément #root est requis pour monter l'application React");
}

// Créer la racine React et rendre l'application
const root = ReactDOM.createRoot(rootElement);

root.render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <AppWrapper>
        <EcoModeProvider>
          <NotificationProvider>
            <AuthProvider>
              <LanguageProvider>
                <RouterProvider router={appRouter} />
              </LanguageProvider>
            </AuthProvider>
          </NotificationProvider>
        </EcoModeProvider>
      </AppWrapper>
    </QueryClientProvider>
  </React.StrictMode>
);

// Marquer l'app comme prête pour les tests E2E
// Utiliser requestAnimationFrame pour s'assurer que le DOM est rendu
requestAnimationFrame(() => {
  const appReadyElement = document.createElement('div');
  appReadyElement.setAttribute('data-testid', 'app-ready');
  appReadyElement.style.display = 'none';
  document.body.appendChild(appReadyElement);
});

