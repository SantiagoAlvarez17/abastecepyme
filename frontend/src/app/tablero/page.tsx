"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Network, PackagePlus } from "lucide-react";
import { DependencyForm } from "@/components/catalog/DependencyForm";
import { CriticalPointsCard } from "@/components/dashboard/CriticalPointsCard";
import { DemoSteps } from "@/components/dashboard/DemoSteps";
import { ProductionStatusBanner } from "@/components/dashboard/ProductionStatusBanner";
import { ProductionStatusPill } from "@/components/dashboard/ProductionStatusPill";
import { SimulationCard } from "@/components/dashboard/SimulationCard";
import { StepSection } from "@/components/dashboard/StepSection";
import { DependencyGraph } from "@/components/graph/DependencyGraph";
import { ProductionOrderPanel } from "@/components/production/ProductionOrderPanel";
import { Card } from "@/components/ui/Card";
import { CatalogGate } from "@/components/ui/CatalogGate";
import { EmptyState } from "@/components/ui/EmptyState";
import { PageHeader } from "@/components/ui/PageHeader";
import { StatCard } from "@/components/ui/StatCard";
import { useCatalogContext } from "@/context/CatalogContext";
import { useProductionOrder } from "@/hooks/useProductionOrder";
import { useUnavailabilitySimulation } from "@/hooks/useUnavailabilitySimulation";
import { TYPE_LABEL_PLURAL, TYPE_ORDER } from "@/lib/business-language";
import { impactHighlightOf } from "@/lib/graph-view";
import { cycleHighlightOf, parseCycleReport } from "@/lib/production-order";
import type { DashboardSummaryDTO, GraphDTO } from "@/lib/types";

/** Step 3: the order is regenerated every time the catalog changes, so it is never stale. */
function ProductionStep({ graph }: Readonly<{ graph: GraphDTO }>) {
  const production = useProductionOrder();
  const { generate } = production;
  const cycleReport = useMemo(() => parseCycleReport(production.error), [production.error]);

  useEffect(() => {
    void generate();
  }, [graph, generate]);

  return <ProductionOrderPanel production={production} cycleReport={cycleReport} />;
}

function Dashboard({ graph, summary }: Readonly<{ graph: GraphDTO; summary: DashboardSummaryDTO }>) {
  const simulation = useUnavailabilitySimulation();
  const { run, clear, result } = simulation;
  const [simulatedIds, setSimulatedIds] = useState<string[]>([]);

  // Keep the result synchronized with the selected sources and current backend catalog.
  useEffect(() => {
    if (simulatedIds.length > 0) void run(simulatedIds);
    else clear();
  }, [graph, simulatedIds, run, clear]);

  // The active simulation is the relevant query; otherwise the map points at the cycle, if any.
  const highlight = useMemo(() => (result ? impactHighlightOf(result) : undefined), [result]);
  const cycle = useMemo(
    () => cycleHighlightOf({ cycles: summary.production.cycles, blockedByCycle: [] }),
    [summary.production.cycles],
  );

  return (
    <div className="space-y-8">
      <DemoSteps
        hasDependencies={summary.total_dependencies > 0}
        simulated={result !== null}
        productionStatus={summary.production.status}
      />

      <ProductionStatusBanner production={summary.production} />

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5" aria-label="Indicadores del catálogo">
        {TYPE_ORDER.map((type) => (
          <StatCard key={type} tone={type} label={TYPE_LABEL_PLURAL[type]} value={summary.by_type[type]} />
        ))}
        <StatCard label="Dependencias" value={summary.total_dependencies} hint="“para producir X necesito Y”" />
        <StatCard
          label="Elementos aislados"
          value={summary.isolated.length}
          hint={
            summary.isolated.length > 0
              ? summary.isolated.map((element) => element.name).join(", ")
              : "Todos participan en la red"
          }
        />
      </section>

      <div className="grid gap-8 xl:grid-cols-5">
        <div className="space-y-8 xl:col-span-2">
          <StepSection step={1} title="Cargar una dependencia">
            <DependencyForm graph={graph} />
          </StepSection>
          <StepSection step={2} title="Simular una indisponibilidad">
            <SimulationCard
              graph={graph}
              selectedIds={simulatedIds}
              simulation={simulation}
              onSimulate={setSimulatedIds}
              onClear={() => setSimulatedIds([])}
            />
          </StepSection>
        </div>

        <div className="space-y-6 xl:col-span-3">
          <Card
            title="Mapa de dependencias"
            description={
              result
                ? "Se resaltan el punto de falla y lo que se afecta en cadena; el resto queda atenuado."
                : summary.production.status === "cycle"
                  ? "Se resaltan los elementos y las dependencias que forman el ciclo."
                  : "Haga clic en un nodo para simular que deja de estar disponible."
            }
            icon={Network}
          >
            <DependencyGraph
              graph={graph}
              highlight={highlight}
              cycle={cycle}
              onSelectElement={(elementId) => setSimulatedIds([elementId])}
            />
          </Card>
          <CriticalPointsCard
            points={summary.critical_points}
            totalProducts={summary.by_type.producto}
            activeId={simulatedIds[0] ?? null}
            onSimulate={(elementId) => setSimulatedIds([elementId])}
          />
        </div>
      </div>

      <StepSection step={3} title="Organizar la producción" id="orden">
        <ProductionStep graph={graph} />
      </StepSection>
    </div>
  );
}

export default function TableroPage() {
  const { summary } = useCatalogContext();

  return (
    <>
      <PageHeader
        title="Tablero de abastecimiento"
        description="Qué falla, qué se afecta y cómo organizar la producción, en una sola vista calculada por el backend."
        actions={summary ? <ProductionStatusPill status={summary.production.status} /> : undefined}
      />
      <CatalogGate>
        {(graph) =>
          graph.nodes.length === 0 || !summary ? (
            <div className="space-y-4">
              <EmptyState
                icon={PackagePlus}
                title="Todavía no hay elementos registrados"
                description="Registre proveedores, insumos y productos en el módulo de Compras para ver aquí el estado del abastecimiento."
              />
              <Link href="/compras" className="block text-center text-sm font-medium text-brand-600 hover:underline">
                Ir al catálogo de Compras
              </Link>
            </div>
          ) : (
            <Dashboard graph={graph} summary={summary} />
          )
        }
      </CatalogGate>
    </>
  );
}
