import { useEffect, useState } from "react";
import { fetchAPI } from "@/utils/api";

export interface SakaSiloData {
  enabled?: boolean;
  total_balance: number;
  total_composted?: number;
  total_cycles?: number;
  last_compost_at?: string | null;
  last_updated?: string;
}

interface UseSakaSiloResult {
  silo: SakaSiloData | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useSakaSilo(): UseSakaSiloResult {
  const [silo, setSilo] = useState<SakaSiloData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAPI("/api/saka/silo/");
      setSilo(data);
    } catch (e: any) {
      setError(e?.message || "Impossible de charger le Silo commun.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return { silo, loading, error, refetch: load };
}

