"use client";

import clsx from "clsx";
import { AlertTriangle, CheckCircle2, Loader2, RotateCcw, Zap } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { byTypeThenName } from "@/components/ui/ElementOptions";
import { Field, inputClass } from "@/components/ui/Field";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { useUnavailabilitySimulation } from "@/hooks/useUnavailabilitySimulation";
import type { GraphDTO } from "@/lib/types";

interface Props {
  graph: GraphDTO;
  selectedIds: string[];
  simulation: ReturnType<typeof useUnavailabilitySimulation>;
  onSimulate: (elementIds: string[]) => void;
  onClear: () => void;
}

export function SimulationCard({
  graph,
  selectedIds,
  simulation,
  onSimulate,
  onClear,
}: Readonly<Props>) {
  const elements = [...graph.nodes].sort(byTypeThenName);
  const sourceNames = new Map(simulation.result?.sources.map((source) => [source.id, source.name]));

  return (
    <Card
      title="Simular indisponibilidad múltiple"
      description="Seleccione los proveedores, insumos o productos que dejan de estar disponibles al mismo tiempo."
      icon={Zap}
    >
      <div className="space-y-4">
        <Field label="Elementos que dejan de estar disponibles" htmlFor="simulation-origins">
          <div className="flex flex-col gap-2 sm:flex-row">
            <select
              id="simulation-origins"
              multiple
              size={Math.min(Math.max(elements.length, 4), 8)}
              value={selectedIds}
              onChange={(event) =>
                onSimulate(Array.from(event.currentTarget.selectedOptions, (option) => option.value))
              }
              aria-describedby="simulation-selection-help"
              className={inputClass}
            >
              {elements.map((element) => (
                <option key={element.id} value={element.id}>
                  {element.name} · {element.element_type}
                </option>
              ))}
            </select>
            {selectedIds.length > 0 && (
              <button
                type="button"
                onClick={onClear}
                title="Terminar la simulación"
                className="inline-flex shrink-0 items-center gap-1.5 self-start rounded-xl border border-ink-200 bg-white px-3 py-2 text-xs font-medium text-ink-700 transition-colors hover:bg-ink-50"
              >
                <RotateCcw className="size-3.5" aria-hidden />
                Limpiar
              </button>
            )}
          </div>
          <span id="simulation-selection-help" className="mt-1 block text-xs text-ink-500">
            Mantenga Ctrl (Windows) o Cmd (Mac) para seleccionar varios elementos.
          </span>
        </Field>

        <div aria-live="polite" className={clsx(simulation.loading && "opacity-60")}>
          {simulation.loading && (
            <p className="flex items-center gap-2 text-xs font-medium text-brand-600">
              <Loader2 className="size-3.5 animate-spin" aria-hidden />
              Recorriendo una vez la red de dependencias…
            </p>
          )}
          {!simulation.loading && simulation.error && (
            <p role="alert" className="rounded-xl bg-danger-soft px-3 py-2.5 text-sm text-ink-900">
              {simulation.error.message}
            </p>
          )}
          {!simulation.loading && simulation.result && (
            <div
              className={clsx(
                "space-y-3 rounded-xl border p-3.5",
                simulation.result.affected_count > 0
                  ? "border-danger/20 bg-danger-soft"
                  : "border-success/20 bg-success-soft",
              )}
            >
              <div className="flex items-start gap-3">
                {simulation.result.affected_count > 0 ? (
                  <AlertTriangle className="mt-0.5 size-5 shrink-0 text-danger" aria-hidden />
                ) : (
                  <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden />
                )}
                <div>
                  <p className="text-sm font-semibold text-ink-900">
                    Simulación: {simulation.result.sources.map((source) => source.name).join(", ")}
                  </p>
                  <p className="mt-0.5 text-sm text-ink-700">{simulation.result.summary}</p>
                </div>
              </div>

              <div className="grid gap-3 sm:grid-cols-2 sm:pl-8">
                <section className="rounded-lg border border-danger/20 bg-white p-3">
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-600">
                    Productos detenidos ({simulation.result.stopped_products.length})
                  </h3>
                  {simulation.result.stopped_products.length === 0 ? (
                    <p className="mt-2 text-sm text-ink-500">Ningún producto queda detenido.</p>
                  ) : (
                    <ul className="mt-2 space-y-1.5">
                      {simulation.result.stopped_products.map((product) => (
                        <li key={product.id} className="flex items-center justify-between gap-2">
                          <span className="text-sm font-medium text-ink-900">{product.name}</span>
                          <TypeBadge type={product.element_type} />
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
                <section className="rounded-lg border border-success/20 bg-white p-3">
                  <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-600">
                    Productos disponibles ({simulation.result.available_products.length})
                  </h3>
                  {simulation.result.available_products.length === 0 ? (
                    <p className="mt-2 text-sm text-ink-500">No hay otros productos disponibles.</p>
                  ) : (
                    <ul className="mt-2 space-y-1.5">
                      {simulation.result.available_products.map((product) => (
                        <li key={product.id} className="flex items-center justify-between gap-2">
                          <span className="text-sm font-medium text-ink-900">{product.name}</span>
                          <TypeBadge type={product.element_type} />
                        </li>
                      ))}
                    </ul>
                  )}
                </section>
              </div>

              {simulation.result.levels.length > 0 && (
                <section className="sm:pl-8">
                  <h3 className="mb-1.5 text-xs font-semibold uppercase tracking-wide text-ink-500">
                    Elementos afectados por nivel
                  </h3>
                  <ol className="space-y-2">
                    {simulation.result.levels.map((level) => (
                      <li key={level.level}>
                        <h4 className="mb-1 text-xs font-medium text-ink-600">Nivel {level.level}</h4>
                        <ul className="flex flex-wrap gap-1.5">
                          {level.elements.map((element) => (
                            <li
                              key={element.id}
                              title={`Ruta: ${element.path.join(" → ")}. Fuente: ${sourceNames.get(element.source_id) ?? "desconocida"}`}
                              className="rounded-full border border-danger/25 bg-white px-2.5 py-0.5 text-xs font-medium text-ink-900"
                            >
                              {element.name}
                            </li>
                          ))}
                        </ul>
                      </li>
                    ))}
                  </ol>
                </section>
              )}
            </div>
          )}
          {!simulation.loading && !simulation.result && !simulation.error && (
            <p className="text-sm text-ink-500">Aún no hay una simulación activa.</p>
          )}
        </div>
      </div>
    </Card>
  );
}
