"use client";

import clsx from "clsx";
import { Activity, RotateCcw } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { OptionGroups, byTypeThenName } from "@/components/ui/ElementOptions";
import { Field, inputClass } from "@/components/ui/Field";
import { MODE_LABEL, TYPE_CLASSES } from "@/lib/business-language";
import type { GraphDTO, ImpactMode } from "@/lib/types";

interface Props {
  graph: GraphDTO;
  originId: string;
  mode: ImpactMode;
  loading: boolean;
  onChange: (originId: string, mode: ImpactMode) => void;
}

const MODES: ImpactMode[] = ["impact", "requirements"];

export function ImpactQueryPanel({ graph, originId, mode, loading, onChange }: Readonly<Props>) {
  const elements = [...graph.nodes].sort(byTypeThenName);
  const quickPick = elements.slice(0, 6);

  return (
    <Card
      title="Centro de análisis de afectación y requisitos"
      description="Elija un elemento y el sentido del recorrido, o haga clic directamente sobre cualquier nodo del mapa."
      icon={Activity}
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <Field label="Elemento a evaluar" htmlFor="impact-origin">
          <div className="flex gap-2">
            <select
              id="impact-origin"
              value={originId}
              onChange={(e) => onChange(e.target.value, mode)}
              className={inputClass}
            >
              <option value="" disabled>
                Seleccione un proveedor, insumo o producto…
              </option>
              <OptionGroups elements={elements} />
            </select>
            {originId && (
              <button
                type="button"
                onClick={() => onChange("", mode)}
                title="Limpiar consulta"
                className="inline-flex shrink-0 items-center gap-1.5 rounded-xl border border-ink-200 bg-white px-3 py-2 text-xs font-medium text-ink-700 transition-colors hover:bg-ink-50"
              >
                <RotateCcw className="size-3.5" aria-hidden />
                Limpiar
              </button>
            )}
          </div>
        </Field>

        <div>
          <span className="mb-1.5 block text-sm font-medium text-ink-700">Sentido del recorrido</span>
          <div role="radiogroup" aria-label="Tipo de consulta" className="grid grid-cols-2 gap-2">
            {MODES.map((m) => (
              <button
                key={m}
                type="button"
                role="radio"
                aria-checked={mode === m}
                onClick={() => onChange(originId, m)}
                className={clsx(
                  "rounded-xl border px-3 py-2.5 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-brand-500",
                  mode === m
                    ? "border-brand-500 bg-brand-100 text-ink-900"
                    : "border-ink-200 bg-white text-ink-500 hover:bg-ink-50",
                )}
              >
                {MODE_LABEL[m].title}
              </button>
            ))}
          </div>
          <p className="mt-1.5 text-xs text-ink-500">{MODE_LABEL[mode].hint}</p>
        </div>
      </div>

      {quickPick.length > 0 && (
        <div className="mt-4 flex flex-wrap items-center gap-2 border-t border-ink-100 pt-3.5">
          <span className="text-xs font-medium text-ink-500">Consulta rápida:</span>
          {quickPick.map((item) => (
            <button
              key={item.id}
              type="button"
              onClick={() => onChange(item.id, mode)}
              className={clsx(
                "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-medium transition-colors",
                originId === item.id
                  ? "border-ink-900 bg-ink-900 text-white"
                  : "border-ink-200 bg-white text-ink-700 hover:bg-ink-50",
              )}
            >
              <span className={clsx("size-1.5 rounded-full", TYPE_CLASSES[item.element_type].dot)} aria-hidden />
              {item.name}
            </button>
          ))}
        </div>
      )}

      {loading && (
        <p aria-live="polite" className="mt-3 text-xs font-medium text-brand-600">
          Recorriendo la red de dependencias…
        </p>
      )}
    </Card>
  );
}
