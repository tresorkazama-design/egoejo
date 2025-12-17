/**
 * Hook pour récupérer les assets globaux de l'utilisateur (liquidités, pockets, dons, equity, SAKA)
 * Utilisé dans Dashboard, PollDetail, ProjectCard, etc.
 */
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchAPI } from '../utils/api';

export const useGlobalAssets = () => {
  const { user } = useAuth();
  const [assets, setAssets] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadAssets = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchAPI('/api/impact/global-assets/');
      setAssets(data);
    } catch (err) {
      console.error('Erreur chargement assets:', err);
      setError(err.message || 'Erreur lors du chargement des assets');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadAssets();
  }, [loadAssets]);

  return {
    data: assets,
    loading,
    error,
    refetch: loadAssets,
  };
};

