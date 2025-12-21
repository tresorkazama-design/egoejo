/**
 * Hooks pour le Protocole SAKA 🌾
 * Phase 3 : Compostage & Silo Commun
 */
import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchAPI } from '../utils/api';
import { logger } from '../utils/logger';

/**
 * Hook pour récupérer l'état du Silo Commun SAKA
 */
export const useSakaSilo = () => {
  const { user } = useAuth();
  const [silo, setSilo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadSilo = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchAPI('/api/saka/silo/');
      setSilo(data);
    } catch (err) {
      console.error('Erreur chargement Silo SAKA:', err);
      setError(err.message || 'Erreur lors du chargement du Silo Commun');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadSilo();
  }, [loadSilo]);

  return {
    data: silo,
    loading,
    error,
    refetch: loadSilo,
  };
};

/**
 * Hook pour récupérer la preview de compostage pour l'utilisateur courant
 */
export const useSakaCompostPreview = () => {
  const { user } = useAuth();
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      setPreview(null);
      return;
    }

    // Appeler l'API directement dans useEffect pour réagir immédiatement aux changements de user
    const loadPreview = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchAPI('/api/saka/compost-preview/');
        setPreview(data);
      } catch (err) {
        logger.error('Erreur chargement preview compost SAKA:', err);
        setError(err.message || 'Erreur lors du chargement de la preview');
      } finally {
        setLoading(false);
      }
    };

    loadPreview();
  }, [user]); // Dépendre directement de user pour réagir immédiatement aux changements

  const refetch = useCallback(async () => {
    if (!user) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchAPI('/api/saka/compost-preview/');
      setPreview(data);
    } catch (err) {
      console.error('Erreur chargement preview compost SAKA:', err);
      setError(err.message || 'Erreur lors du chargement de la preview');
    } finally {
      setLoading(false);
    }
  }, [user]);

  return {
    data: preview,
    loading,
    error,
    refetch,
  };
};

/**
 * Hook pour récupérer les statistiques SAKA (admin uniquement)
 */
export const useSakaStats = (days = 30, limit = 10) => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadStats = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({ days: days.toString(), limit: limit.toString() });
      const data = await fetchAPI(`/api/saka/stats/?${params}`);
      setStats(data);
    } catch (err) {
      logger.error('Erreur chargement stats SAKA:', err);
      setError(err.message || 'Erreur lors du chargement des statistiques SAKA');
    } finally {
      setLoading(false);
    }
  }, [user, days, limit]);

  useEffect(() => {
    loadStats();
  }, [loadStats]);

  return {
    data: stats,
    loading,
    error,
    refetch: loadStats,
  };
};

/**
 * Hook pour récupérer les logs de compostage SAKA (admin uniquement)
 */
export const useSakaCompostLogs = (limit = 20) => {
  const { user } = useAuth();
  const [logs, setLogs] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadLogs = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const params = new URLSearchParams({ limit: limit.toString() });
      const data = await fetchAPI(`/api/saka/compost-logs/?${params}`);
      setLogs(data);
    } catch (err) {
      logger.error('Erreur chargement logs compost SAKA:', err);
      setError(err.message || 'Erreur lors du chargement des logs de compostage');
    } finally {
      setLoading(false);
    }
  }, [user, limit]);

  useEffect(() => {
    loadLogs();
  }, [loadLogs]);

  return {
    data: logs,
    loading,
    error,
    refetch: loadLogs,
  };
};

/**
 * Hook pour récupérer les cycles SAKA (saisons)
 */
export const useSakaCycles = () => {
  const { user } = useAuth();
  const [cycles, setCycles] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadCycles = useCallback(async () => {
    if (!user) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await fetchAPI('/api/saka/cycles/');
      // L'API retourne un tableau direct, pas un objet avec results/cycles
      setCycles(Array.isArray(data) ? data : []);
    } catch (err) {
      logger.error('Erreur chargement cycles SAKA:', err);
      setError(err.message || 'Erreur lors du chargement des cycles SAKA');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    loadCycles();
  }, [loadCycles]);

  return {
    data: cycles,
    loading,
    error,
    refetch: loadCycles,
  };
};

/**
 * Hook pour lancer un cycle de compost SAKA en mode dry-run (admin uniquement)
 */
export const useSakaCompostRun = () => {
  const { user } = useAuth();
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState(null);

  const runCompostDryRun = useCallback(async () => {
    if (!user) {
      throw new Error('Utilisateur non authentifié');
    }

    try {
      setIsRunning(true);
      setError(null);
      const data = await fetchAPI('/api/saka/compost-run/', {
        method: 'POST',
      });
      return data;
    } catch (err) {
      const errorMessage = err.message || 'Erreur lors du lancement du cycle de compost';
      setError(errorMessage);
      throw err;
    } finally {
      setIsRunning(false);
    }
  }, [user]);

  return {
    runCompostDryRun,
    isRunning,
    error,
  };
};

