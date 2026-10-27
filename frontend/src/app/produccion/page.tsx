"use client";

import { useMemo, useState } from "react";
import { Activity, AlertTriangle, Network } from "lucide-react";
import { DependencyGraph } from "@/components/graph/DependencyGraph";
import { ImpactLevels } from "@/components/impact/ImpactLevels";
import { ImpactQueryPanel } from "@/components/impact/ImpactQueryPanel";
import { ImpactSummary } from "@/components/impact/ImpactSummary";
import { Card } from "@/components/ui/Card";
import { CatalogGate } from "@/components/ui/CatalogGate";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { useImpact } from "@/hooks/useImpact";
import type { ImpactHighlight } from "@/lib/graph-view";
import type { ImpactMode } from "@/lib/types";

export default function ProduccionPage() {
  const [originId, setOriginId] = useState("");
  const [mode, setMode] = useState<ImpactMode>("impact");
  const { result, loading, error, run, clear } = useImpact();

  function handleQuery(nextOrigin: string, nextMode: ImpactMode) {
    setOriginId(nextOrigin);
    setMode(nextMode);
    if (nextOrigin) void run(nextOrigin, nextMode);
    else clear();
  }

  const highlight = useMemo<ImpactHighlight | undefined>(
    () =>
      result
        ? {
            mode: result.mode,
            originId: result.origin.id,
            affectedIds: result.levels.flatMap((l) => l.elements.map((e) => e.id)),
          }
        : undefined,
    [result],
  );

  const showLevels = result !== null && result.levels.length > 0;

  return (
    <>
      <PageHeader
        title="Impacto en producción"
        description="Identifique qué productos se afectan cuando un proveedor o insumo deja de estar disponible, o qué necesita un producto para producirse."
      />
      <CatalogGate>
        {(graph) =>
          graph.nodes.length === 0 ? (
            <EmptyState
              icon={Network}
              title="Todavía no hay elementos"
              description="Pida al responsable de compras que registre proveedores, insumos y productos en la vista de Compras."
            />
          ) : (
            <div className="space-y-6">
              <ImpactQueryPanel graph={graph} originId={originId} mode={mode} loading={loading} onChange={handleQuery} />

              {error && (
                <div role="alert" className="flex items-start gap-3 rounded-2xl border border-danger/20 bg-danger-soft p-4">
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-danger" aria-hidden />
                  <div>
                    <p className="font-medium text-danger">No se pudo completar la consulta</p>
                    <p className="mt-1 text-sm text-ink-700">{error.message}</p>
                  </div>
                </div>
              )}

              {result && <ImpactSummary result={result} />}
              {!result && !error && !loading && (
                <EmptyState
                  icon={Activity}
                  title="Seleccione un elemento para analizar su impacto"
                  description="Verá qué se afecta en cadena, en qué orden y por qué ruta. También puede hacer clic en un elemento del mapa."
                />
              )}

              <div className={showLevels ? "grid gap-6 xl:grid-cols-5" : ""}>
                <div className={showLevels ? "xl:col-span-3" : ""}>
                  <Card
                    title="Mapa de dependencias"
                    description="El punto de falla y los elementos afectados se resaltan según la consulta."
                    icon={Network}
                  >
                    <DependencyGraph
                      graph={graph}
                      highlight={highlight}
                      onSelectElement={(id) => handleQuery(id, mode)}
                    />
                  </Card>
                </div>
                {showLevels && result && (
                  <div className="xl:col-span-2">
                    <ImpactLevels result={result} />
                  </div>
                )}
              </div>
            </div>
          )
        }
      </CatalogGate>
    </>
  );
}