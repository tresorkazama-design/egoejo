/**
 * Hook React Query pour récupérer les contenus avec pagination et cache
 */

import { useQuery } from '@tanstack/react-query';
import { fetchAPI, handleAPIError } from '../utils/api';

/**
 * Hook pour récupérer les contenus avec pagination
 * 
 * @param {Object} options - Options de pagination
 * @param {number} options.page - Numéro de page (défaut: 1)
 * @param {number} options.pageSize - Nombre d'éléments par page (défaut: 20)
 * @param {string} options.status - Statut des contenus (défaut: 'published')
 * @param {boolean} options.enabled - Activer/désactiver la requête (défaut: true)
 * 
 * @returns {Object} - Résultat de useQuery avec données paginées
 */
export const useContents = ({ 
  page = 1, 
  pageSize = 20, 
  status = 'published',
  enabled = true 
} = {}) => {
  return useQuery({
    queryKey: ['contents', status, page, pageSize],
    queryFn: async () => {
      try {
        // Construire l'URL avec pagination
        const params = new URLSearchParams({
          status,
          page: page.toString(),
          page_size: Math.min(pageSize, 100).toString(), // Limiter à 100 max
        });
        
        const data = await fetchAPI(`/contents/?${params.toString()}`);
        
        // Gérer les deux formats de réponse (paginée ou liste simple)
        if (data.results !== undefined) {
          // Format paginé DRF
          return {
            contents: data.results,
            count: data.count || data.results.length,
            next: data.next,
            previous: data.previous,
            currentPage: page,
            pageSize: pageSize,
            totalPages: data.count ? Math.ceil(data.count / pageSize) : 1,
          };
        } else if (Array.isArray(data)) {
          // Format liste simple (rétrocompatibilité avec cache)
          return {
            contents: data,
            count: data.length,
            next: null,
            previous: null,
            currentPage: 1,
            pageSize: data.length,
            totalPages: 1,
          };
        } else {
          throw new Error('Format de réponse API inattendu');
        }
      } catch (error) {
        const errorMessage = handleAPIError(error);
        throw new Error(errorMessage);
      }
    },
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes - stale-while-revalidate
    gcTime: 10 * 60 * 1000, // 10 minutes - garder en cache (anciennement cacheTime)
    retry: (failureCount, error) => {
      // Ne pas retry si on est offline (le service worker gère le cache)
      if (typeof navigator !== 'undefined' && !navigator.onLine) {
        return false;
      }
      // Retry 2 fois en cas d'erreur réseau
      return failureCount < 2;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000), // Backoff exponentiel
    // Utiliser le cache en priorité si offline
    networkMode: typeof navigator !== 'undefined' && !navigator.onLine ? 'offlineFirst' : 'online',
  });
};

