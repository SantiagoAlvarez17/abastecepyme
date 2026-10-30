"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
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

function ProduccionContent() {
  const searchParams = useSearchParams();
  const initialElement = searchParams.get("element") ?? "";
  const initialMode: ImpactMode =
    searchParams.get("mode") === "requirements" ? "requirements" : "impact";

  const [originId, setOriginId] = useState(initialElement);
  const [mode, setMode] = useState<ImpactMode>(initialMode);
  const { result, loading, error, run, clear } = useImpact();

  useEffect(() => {
    if (!initialElement) return;
    const timer = window.setTimeout(() => {
      void run(initialElement, initialMode);
    }, 0);
    return () => window.clearTimeout(timer);
  }, [initialElement, initialMode, run]);

  function handleQuery(nextOrigin: string, nextMode: ImpactMode) {
    setOriginId(nextOrigin);
    setMode(nextMode);
    if (nextOrigin) void run(nextOrigin, nextMode);
    else clear();
  }

  const highlight = useMemo<ImpactHighlight | undefined>(() => {
    if (!result) return undefined;
    const levelById: Record<string, number> = {};
    for (const lv of result.levels) {
      for (const el of lv.elements) {
        levelById[el.id] = el.level;
      }
    }
    return {
      mode: result.mode,
      originId: result.origin.id,
      affectedIds: result.levels.flatMap((l) => l.elements.map((e) => e.id)),
      levelById,
    };
  }, [result]);

  const showLevels = result !== null && result.levels.length > 0;

  return (
    <>
      <PageHeader
        title="Impacto en producción y trazabilidad"
        description="Simule la indisponibilidad de un proveedor, insumo o producto intermedio para identificar qué líneas se afectan, o consulte los requisitos completos de un producto."
      />
      <CatalogGate>
        {(graph) =>
          graph.nodes.length === 0 ? (
            <EmptyState
              icon={Network}
              title="Todavía no hay elementos registrados"
              description="Pida al responsable de compras que registre proveedores, insumos y productos en el módulo de Compras."
            />
          ) : (
            <div className="space-y-6">
              <ImpactQueryPanel
                graph={graph}
                originId={originId}
                mode={mode}
                loading={loading}
                onChange={handleQuery}
              />

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
                  description="Verá qué se afecta en cadena, agrupado por niveles y con su ruta completa. También puede hacer clic directamente en un nodo del mapa inferior."
                />
              )}

              <div className={showLevels ? "grid gap-6 xl:grid-cols-5" : ""}>
                <div className={showLevels ? "xl:col-span-3" : ""}>
                  <Card
                    title="Mapa interactivo de dependencias"
                    description="El punto de falla y los elementos alcanzados por nivel (Nivel 1, Nivel 2…) se resaltan automáticamente."
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
                    <ImpactLevels result={result} onSelectElement={(id) => handleQuery(id, mode)} />
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

export default function ProduccionPage() {
  return (
    <Suspense fallback={null}>
      <ProduccionContent />
    </Suspense>
  );
}
