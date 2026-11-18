"use client";

import { useCallback, useRef, useState } from "react";
import { ApiError } from "@/services/api-client";
import { simulationService } from "@/services/simulation.service";
import type { UnavailabilitySimulationDTO } from "@/lib/types";

export function useUnavailabilitySimulation() {
  const [result, setResult] = useState<UnavailabilitySimulationDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const latest = useRef(0);

  const run = useCallback(async (elementIds: string[]) => {
    const ticket = ++latest.current;
    setLoading(true);
    setError(null);
    try {
      const data = await simulationService.simulateUnavailability(elementIds);
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
