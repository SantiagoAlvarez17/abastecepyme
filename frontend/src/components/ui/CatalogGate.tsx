"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";
import { useCatalogContext } from "@/context/CatalogContext";
import type { GraphDTO } from "@/lib/types";

export function CatalogGate({ children }: Readonly<{ children: (graph: GraphDTO) => React.ReactNode }>) {
  const { graph, loading, error, refresh } = useCatalogContext();

  if (loading) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-busy="true" aria-label="Cargando datos">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="h-28 animate-pulse rounded-2xl bg-ink-100" />
        ))}
      </div>
    );
  }

  if (error || !graph) {
    return (
      <div role="alert" className="flex items-start gap-4 rounded-2xl border border-danger/20 bg-danger-soft p-5">
        <AlertTriangle className="mt-0.5 size-5 shrink-0 text-danger" aria-hidden />
        <div className="flex-1">
          <p className="font-medium text-danger">No pudimos cargar los datos</p>
          <p className="mt-1 text-sm text-ink-700">{error?.message ?? "Respuesta vacía del servidor."}</p>
          <button
            type="button"
            onClick={() => void refresh()}
            className="mt-3 inline-flex items-center gap-2 rounded-lg bg-danger px-3 py-1.5 text-sm font-medium text-white hover:opacity-90"
          >
            <RefreshCw className="size-4" aria-hidden />
            Reintentar
          </button>
        </div>
      </div>
    );
  }

  return <>{children(graph)}</>;
}
