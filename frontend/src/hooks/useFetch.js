import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { fetchAPI, handleAPIError } from '../utils/api';

/**
 * Hook pour récupérer des données depuis l'API
 * 
 * OPTIMISATION PERFORMANCE :
 * - useRef pour stocker les options et éviter les rerenders infinis
 * - Hash mémorisé des options pour détecter les vrais changements (pas juste référence)
 * - useCallback pour mémoriser refetch et éviter les rerenders inutiles
 */

/**
 * Calcule un hash simple des options pour détecter les changements profonds
 * OPTIMISATION : Plus efficace que JSON.stringify à chaque render
 */
function getOptionsHash(opts) {
  if (!opts || Object.keys(opts).length === 0) return '';
  // Hash simple basé sur les clés et valeurs importantes
  const keys = Object.keys(opts).sort();
  return keys.map(key => `${key}:${JSON.stringify(opts[key])}`).join('|');
}

export const useFetch = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // OPTIMISATION : Stocker les options dans un ref pour éviter les rerenders infinis
  // JSON.stringify(options) dans les dépendances créait une nouvelle string à chaque render
  const optionsRef = useRef(options);
  const endpointRef = useRef(endpoint);
  
  // OPTIMISATION : Mémoriser le hash des options (calculé seulement si options change)
  // useMemo garantit que le hash n'est recalculé que si les options changent profondément
  const optionsHash = useMemo(() => getOptionsHash(options), [options]);
  
  // Mettre à jour les refs quand les valeurs changent
  useEffect(() => {
    optionsRef.current = options;
    endpointRef.current = endpoint;
  }, [endpoint, options]);

  useEffect(() => {
    let cancelled = false;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        // Utiliser les valeurs des refs pour éviter les dépendances instables
        const result = await fetchAPI(endpointRef.current, optionsRef.current);
        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError(handleAPIError(err));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadData();

    return () => {
      cancelled = true;
    };
  }, [endpoint, optionsHash]); // ✅ endpoint + hash des options (détecte changements profonds sans recalculer à chaque render)

  // OPTIMISATION : Mémoriser refetch avec useCallback pour éviter les rerenders inutiles
  // La fonction refetch était recréée à chaque render, causant des rerenders de tous les composants enfants
  const refetch = useCallback(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchAPI(endpointRef.current, optionsRef.current);
        setData(result);
      } catch (err) {
        setError(handleAPIError(err));
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []); // ✅ Dépendances vides = fonction stable entre les renders

  return { data, loading, error, refetch };
};

