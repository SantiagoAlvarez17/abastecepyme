"use client";

import { useCallback, useRef, useState } from "react";
import { ApiError } from "@/services/api-client";
import { impactService } from "@/services/impact.service";
import type { ImpactMode, ImpactResponseDTO } from "@/lib/types";

export function useImpact() {
  const [result, setResult] = useState<ImpactResponseDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  // Si el usuario cambia de consulta rápido, solo cuenta la respuesta de la última.
  const latest = useRef(0);

  const run = useCallback(async (elementId: string, mode: ImpactMode) => {
    const ticket = ++latest.current;
    setLoading(true);
    setError(null);
    try {
      const data = await impactService.analyze(elementId, mode);
      if (ticket === latest.current) setResult(data);
    } catch (e) {
      if (ticket === latest.current) {
        setResult(null);
        setError(e instanceof ApiError ? e : new ApiError(0, "ERR_UNKNOWN", String(e)));
      }
    } finally {
      if (ticket === latest.current) setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    latest.current++;
    setResult(null);
    setError(null);
    setLoading(false);
  }, []);

  return { result, loading, error, run, clear };
}