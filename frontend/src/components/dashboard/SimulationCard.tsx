"use client";

import Link from "next/link";
import clsx from "clsx";
import { AlertTriangle, CheckCircle2, Loader2, RotateCcw, Unlink, Zap } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { OptionGroups, byTypeThenName } from "@/components/ui/ElementOptions";
import { Field, inputClass } from "@/components/ui/Field";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { useImpact } from "@/hooks/useImpact";
import type { GraphDTO, ImpactResponseDTO, ReachedElementDTO } from "@/lib/types";

interface Props {
  graph: GraphDTO;
  selectedId: string;
  impact: ReturnType<typeof useImpact>;
  onSimulate: (elementId: string) => void;
  onClear: () => void;
}

const reachedOf = (result: ImpactResponseDTO): ReachedElementDTO[] => result.levels.flatMap((level) => level.elements);

function SimulationResult({ result }: Readonly<{ result: ImpactResponseDTO }>) {
  if (result.outcome !== "chain") {
    const Icon = result.outcome === "isolated" ? Unlink : CheckCircle2;
    return (
      <div className="flex items-start gap-3 rounded-xl border border-ink-200 bg-ink-50 p-3.5">
        <Icon className="mt-0.5 size-5 shrink-0 text-success" aria-hidden />
        <p className="text-sm text-ink-700">{result.summary}</p>
      </div>
    );
  }

  const reached = reachedOf(result);
  const products = reached.filter((element) => element.element_type === "producto");

  return (
    <div className="space-y-3 rounded-xl border border-danger/20 bg-danger-soft p-3.5">
      <div className="flex items-start gap-3">
        <AlertTriangle className="mt-0.5 size-5 shrink-0 text-danger" aria-hidden />
        <div>
          <p className="text-sm font-semibold text-ink-900">
            {result.affected_count} elemento{result.affected_count === 1 ? "" : "s"} afectado
            {result.affected_count === 1 ? "" : "s"} en {result.max_level} nivel{result.max_level === 1 ? "" : "es"}
          </p>
          <p className="mt-0.5 text-sm text-ink-700">{result.summary}</p>
        </div>
      </div>
      {products.length > 0 && (
        <div className="sm:pl-8">
          <p className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-500">Productos que se detienen</p>
          <ul className="flex flex-wrap gap-1.5">
            {products.map((product) => (
              <li
                key={product.id}
                title={product.path.join(" → ")}
                className="rounded-full border border-danger/25 bg-white px-2.5 py-0.5 text-xs font-medium text-ink-900"
              >
                {product.name}
              </li>
            ))}
          </ul>
        </div>
      )}
      <Link
        href={`/produccion?element=${encodeURIComponent(result.origin.id)}&mode=impact`}
        className="inline-block text-sm font-medium text-brand-600 hover:underline sm:pl-8"
      >
        Ver el desglose completo por nivel
      </Link>
    </div>
  );
}

/** Step 2 of the demo: pick what fails; the reverse BFS runs in the backend (GET /impact). */
export function SimulationCard({ graph, selectedId, impact, onSimulate, onClear }: Readonly<Props>) {
  const elements = [...graph.nodes].sort(byTypeThenName);
  const selected = graph.nodes.find((node) => node.id === selectedId);

  return (
    <Card
      title="Simular indisponibilidad"
      description="Elija un proveedor, insumo o producto intermedio, o haga clic en un nodo del mapa."
      icon={Zap}
    >
      <div className="space-y-4">
        <Field label="Elemento que deja de estar disponible" htmlFor="simulation-origin">
          <div className="flex gap-2">
            <select
              id="simulation-origin"
              value={selectedId}
              onChange={(e) => onSimulate(e.target.value)}
              className={inputClass}
            >
              <option value="" disabled>
                Seleccione qué falla…
              </option>
              <OptionGroups elements={elements} />
            </select>
            {selectedId && (
              <button
                type="button"
                onClick={onClear}
                title="Terminar la simulación"
                className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-ink-200 bg-white px-3 py-2 text-xs font-medium text-ink-700 transition-colors hover:bg-ink-50"
              >
                <RotateCcw className="size-3.5" aria-hidden />
                Limpiar
              </button>
            )}
          </div>
        </Field>

        <div aria-live="polite" className={clsx(impact.loading && "opacity-60")}>
          {impact.loading && (
            <p className="flex items-center gap-2 text-xs font-medium text-brand-600">
              <Loader2 className="size-3.5 animate-spin" aria-hidden />
              Recorriendo la red de dependencias…
            </p>
          )}
          {!impact.loading && impact.error && (
            <p role="alert" className="rounded-xl bg-danger-soft px-3 py-2.5 text-sm text-ink-900">
              {impact.error.message}
            </p>
          )}
          {!impact.loading && impact.result && selected && (
            <div className="space-y-2">
              <p className="flex items-center gap-2 text-xs text-ink-500">
                Simulando la falla de <strong className="text-ink-900">{selected.name}</strong>
                <TypeBadge type={selected.element_type} />
              </p>
              <SimulationResult result={impact.result} />
            </div>
          )}
          {!impact.loading && !impact.result && !impact.error && (
            <p className="text-sm text-ink-500">Aún no hay una simulación activa.</p>
          )}
        </div>
      </div>
    </Card>
  );
}
