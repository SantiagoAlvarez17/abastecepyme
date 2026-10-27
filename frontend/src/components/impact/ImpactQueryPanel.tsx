"use client";

import clsx from "clsx";
import { Activity } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { OptionGroups, byTypeThenName } from "@/components/ui/ElementOptions";
import { Field, inputClass } from "@/components/ui/Field";
import { MODE_LABEL } from "@/lib/business-language";
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

  return (
    <Card
      title="Consulta de afectación"
      description="Elija un elemento y el tipo de consulta. También puede hacer clic en un elemento del mapa."
      icon={Activity}
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <Field label="Elemento" htmlFor="impact-origin">
          <select
            id="impact-origin"
            value={originId}
            onChange={(e) => onChange(e.target.value, mode)}
            className={inputClass}
          >
            <option value="" disabled>
              Seleccione un proveedor, insumo o producto
            </option>
            <OptionGroups elements={elements} />
          </select>
        </Field>

        <div>
          <span className="mb-1.5 block text-sm font-medium text-ink-700">Tipo de consulta</span>
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
      <p aria-live="polite" className="mt-3 h-4 text-xs text-ink-500">
        {loading ? "Analizando…" : ""}
      </p>
    </Card>
  );
}