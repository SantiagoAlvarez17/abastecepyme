"use client";

import { useCallback, useEffect, useState } from "react";
import { ApiError } from "@/services/api-client";
import { catalogService } from "@/services/catalog.service";
import { dashboardService } from "@/services/dashboard.service";
import type { DashboardSummaryDTO, DependencyDTO, ElementType, GraphDTO } from "@/lib/types";

interface CatalogSnapshot {
  graph: GraphDTO;
  summary: DashboardSummaryDTO;
}

/** The graph and its dashboard summary are always fetched together, so they never disagree. */
const loadSnapshot = async (): Promise<CatalogSnapshot> => {
  const [graph, summary] = await Promise.all([catalogService.getGraph(), dashboardService.getSummary()]);
  return { graph, summary };
};

const toApiError = (e: unknown) => (e instanceof ApiError ? e : new ApiError(0, "ERR_UNKNOWN", String(e)));

export function useCatalog() {
  const [snapshot, setSnapshot] = useState<CatalogSnapshot | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ApiError | null>(null);

  const refresh = useCallback(async () => {
    try {
      setSnapshot(await loadSnapshot());
      setError(null);
    } catch (e) {
      setError(toApiError(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    loadSnapshot()
      .then((next) => {
        if (!active) return;
        setSnapshot(next);
        setError(null);
      })
      .catch((e) => {
        if (active) setError(toApiError(e));
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  // Mutations throw ApiError so that the calling form can show the message.
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

  return {
    graph: snapshot?.graph ?? null,
    summary: snapshot?.summary ?? null,
    loading,
    error,
    refresh,
    createElement,
    registerDependency,
  };
}
