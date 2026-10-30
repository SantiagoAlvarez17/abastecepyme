"use client";

import clsx from "clsx";
import { useCatalogContext } from "@/context/CatalogContext";

export function ConnectionStatus() {
  const { graph, error, loading } = useCatalogContext();
  const state = loading ? "checking" : error ? "offline" : "online";

  const label = {
    checking: "Conectando…",
    offline: "Sin conexión con la API",
    online: "API conectada",
  }[state];

  return (
    <div className="rounded-xl bg-white/5 px-3 py-3 text-xs">
      <div className="flex items-center gap-2 text-ink-200">
        <span
          className={clsx("size-2 rounded-full", {
            "animate-pulse bg-ink-300": state === "checking",
            "bg-danger": state === "offline",
            "bg-success": state === "online",
          })}
        />
        <span>{label}</span>
      </div>
      {state === "online" && graph && (
        <p className="mt-1 pl-4 text-ink-300">
          {graph.nodes.length} elementos · {graph.edges.length} dependencias
        </p>
      )}
    </div>
  );
}