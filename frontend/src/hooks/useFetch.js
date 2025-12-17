import { useState, useEffect } from 'react';
import { fetchAPI, handleAPIError } from '../utils/api';

export const useFetch = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchAPI(endpoint, options);
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
  }, [endpoint, JSON.stringify(options)]);

  return { data, loading, error, refetch: () => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchAPI(endpoint, options);
        setData(result);
      } catch (err) {
        setError(handleAPIError(err));
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }};
};

