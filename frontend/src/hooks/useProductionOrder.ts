"use client";

import { useCallback, useRef, useState } from "react";
import { ApiError } from "@/services/api-client";
import { productionService } from "@/services/production.service";
import type { ProductionOrderDTO } from "@/lib/types";

export function useProductionOrder() {
  const [order, setOrder] = useState<ProductionOrderDTO | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  // Si se pulsa el botón varias veces seguidas, solo cuenta la respuesta de la última consulta.
  const latest = useRef(0);

  const generate = useCallback(async () => {
    const ticket = ++latest.current;
    setLoading(true);
    setError(null);
    try {
      const data = await productionService.getOrder();
      if (ticket === latest.current) setOrder(data);
    } catch (e) {
      if (ticket === latest.current) {
        setOrder(null);
        setError(e instanceof ApiError ? e : new ApiError(0, "ERR_UNKNOWN", String(e)));
      }
    } finally {
      if (ticket === latest.current) setLoading(false);
    }
  }, []);

  return { order, loading, error, generate };
}