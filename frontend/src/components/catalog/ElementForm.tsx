"use client";

import { useState } from "react";
import clsx from "clsx";
import { Loader2, PackagePlus } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Field, inputClass, primaryButtonClass } from "@/components/ui/Field";
import { FormFeedback, type Feedback } from "@/components/ui/FormFeedback";
import { useCatalogContext } from "@/context/CatalogContext";
import { TYPE_LABEL, TYPE_ORDER } from "@/lib/business-language";
import { validateElementName } from "@/lib/catalog-rules";
import type { ElementType, GraphDTO } from "@/lib/types";
import { ApiError } from "@/services/api-client";

const TYPE_HINT: Record<ElementType, string> = {
  proveedor: "Quien le suministra insumos. No depende de nada más.",
  insumo: "Materia prima o material que se compra a un proveedor.",
  producto: "Lo que se fabrica. Necesita insumos u otros productos.",
};

export function ElementForm({ graph }: Readonly<{ graph: GraphDTO }>) {
  const { createElement } = useCatalogContext();
  const [name, setName] = useState("");
  const [type, setType] = useState<ElementType>("proveedor");
  const [touched, setTouched] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const error = validateElementName(name, graph.nodes);
  const showError = touched && error;

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setTouched(true);
    if (error) return;

    setSubmitting(true);
    setFeedback(null);
    try {
      const created = await createElement({ name: name.trim(), element_type: type });
      setFeedback({ kind: "success", text: `${TYPE_LABEL[created.element_type]} “${created.name}” registrado.` });
      setName("");
      setTouched(false);
    } catch (err) {
      setFeedback({ kind: "error", text: err instanceof ApiError ? err.message : "Ocurrió un error inesperado." });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <Card title="Registrar elemento" description="Agregue un proveedor, un insumo o un producto final." icon={PackagePlus}>
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Field label="Nombre" htmlFor="element-name" error={showError ? error : null}>
          <input
            id="element-name"
            value={name}
            onChange={(e) => {
              setName(e.target.value);
              setTouched(true);
              setFeedback(null);
            }}
            placeholder="Ej.: Harina de trigo"
            autoComplete="off"
            className={inputClass}
            aria-invalid={showError ? true : undefined}
            aria-describedby={showError ? "element-name-error" : undefined}
          />
        </Field>

        <div>
          <span className="mb-1.5 block text-sm font-medium text-ink-700">Tipo</span>
          <div role="radiogroup" aria-label="Tipo de elemento" className="grid grid-cols-3 gap-2">
            {TYPE_ORDER.map((t) => (
              <button
                key={t}
                type="button"
                role="radio"
                aria-checked={type === t}
                onClick={() => setType(t)}
                className={clsx(
                  "rounded-xl border px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-2 focus-visible:outline-brand-500",
                  type === t
                    ? "border-brand-500 bg-brand-100 text-ink-900"
                    : "border-ink-200 bg-white text-ink-500 hover:bg-ink-50",
                )}
              >
                {TYPE_LABEL[t]}
              </button>
            ))}
          </div>
          <p className="mt-1.5 text-xs text-ink-500">{TYPE_HINT[type]}</p>
        </div>

        <FormFeedback feedback={feedback} />

        <button type="submit" disabled={submitting} className={primaryButtonClass}>
          {submitting && <Loader2 className="size-4 animate-spin" aria-hidden />}
          {submitting ? "Guardando…" : "Crear elemento"}
        </button>
      </form>
    </Card>
  );
}