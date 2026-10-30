"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError } from "@/services/api-client";
import { catalogService } from "@/services/catalog.service";
import type { DependencyDTO, ElementType, GraphDTO } from "@/lib/types";

export function useCatalog() {
  const [graph, setGraph] = useState<GraphDTO | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const refresh = useCallback(async () => {
    try {
      const nextGraph = await catalogService.getGraph();
      setGraph(nextGraph);
      setError(null);
    } catch (e) {
      setError(e instanceof ApiError ? e : new ApiError(0, "ERR_UNKNOWN", String(e)));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    catalogService
      .getGraph()
      .then((nextGraph) => {
        if (active) {
          setGraph(nextGraph);
          setError(null);
        }
      })
      .catch((e) => {
        if (active) {
          setError(e instanceof ApiError ? e : new ApiError(0, "ERR_UNKNOWN", String(e)));
        }
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  // Las mutaciones lanzan ApiError para que el formulario muestre el mensaje.
  const createElement = useCallback(
    async (input: { name: string; element_type: ElementType }) => {
      const created = await catalogService.createElement(input);
      await refresh();
      return created;
    },
    [refresh],
  );

  const registerDependency = useCallback(
    async (input: DependencyDTO) => {
      const created = await catalogService.registerDependency(input);
      await refresh();
      return created;
    },
    [refresh],
  );

  return { graph, loading, error, refresh, createElement, registerDependency };
}
