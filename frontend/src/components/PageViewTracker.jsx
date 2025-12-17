/**
 * Composant pour tracker les changements de page
 */
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { trackPageView } from '../utils/analytics';

export default function PageViewTracker() {
  const location = useLocation();

  useEffect(() => {
    // Tracker chaque changement de page
    trackPageView(location.pathname, {
      search: location.search,
      hash: location.hash,
    });
  }, [location]);

  return null;
}

