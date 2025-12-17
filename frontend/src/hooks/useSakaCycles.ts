import { useEffect, useState } from "react";
import { fetchAPI } from "@/utils/api";

export interface SakaCycle {
  id: number;
  name: string;        // ex: "Cycle Q1 2025"
  start_date: string;
  end_date: string;
  is_active: boolean;
  stats: {
    saka_harvested: number;
    saka_planted: number;
    saka_composted: number;
  };
}

interface UseSakaCyclesResult {
  cycles: SakaCycle[];
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useSakaCycles(): UseSakaCyclesResult {
  const [cycles, setCycles] = useState<SakaCycle[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAPI("/api/saka/cycles/");
      // L'API retourne un tableau direct
      setCycles(Array.isArray(data) ? data : []);
    } catch (e: any) {
      setError(e?.message || "Impossible de charger les cycles SAKA.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return { cycles, loading, error, refetch: load };
}

