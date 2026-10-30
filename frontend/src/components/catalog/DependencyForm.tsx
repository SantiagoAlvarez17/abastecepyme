"use client";

import { useMemo, useState } from "react";
import { Link2, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { OptionGroups, byTypeThenName } from "@/components/ui/ElementOptions";
import { Field, inputClass, primaryButtonClass } from "@/components/ui/Field";
import { FormFeedback, type Feedback } from "@/components/ui/FormFeedback";
import { useCatalogContext } from "@/context/CatalogContext";
import { dependencySentence } from "@/lib/business-language";
import { CAN_REQUIRE, canRequire, dependencyExists, validateDependency } from "@/lib/catalog-rules";
import type { GraphDTO } from "@/lib/types";
import { ApiError } from "@/services/api-client";

export function DependencyForm({ graph }: Readonly<{ graph: GraphDTO }>) {
  const { registerDependency } = useCatalogContext();
  const [requiringId, setRequiringId] = useState("");
  const [requiredId, setRequiredId] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<Feedback | null>(null);

  const byId = useMemo(() => new Map(graph.nodes.map((n) => [n.id, n])), [graph.nodes]);
  const requiring = byId.get(requiringId);
  const required = byId.get(requiredId);

  // Un proveedor nunca "requiere" nada, así que no aparece en la primera lista.
  const requiringOptions = useMemo(
    () => graph.nodes.filter((n) => CAN_REQUIRE[n.element_type].length > 0).sort(byTypeThenName),
    [graph.nodes],
  );

  // Solo se ofrece lo que es válido y todavía no está registrado.
  const requiredOptions = useMemo(() => {
    if (!requiring) return [];
    return graph.nodes
      .filter(
        (n) =>
          n.id !== requiring.id &&
          canRequire(requiring.element_type, n.element_type) &&
          !dependencyExists(graph.edges, requiring.id, n.id),
      )
      .sort(byTypeThenName);
  }, [graph.nodes, graph.edges, requiring]);

  const error = requiring && required ? validateDependency(requiring, required, graph.edges) : null;
  const canSubmit = Boolean(requiring && required) && !error && !submitting;

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!requiring || !required || error) return;

    setSubmitting(true);
    setFeedback(null);
    try {
      await registerDependency({ requiring_element_id: requiring.id, required_element_id: required.id });
      setFeedback({ kind: "success", text: `Registrado: ${dependencySentence(requiring.name, required.name)}.` });
      setRequiredId("");
    } catch (err) {
      setFeedback({ kind: "error", text: err instanceof ApiError ? err.message : "Ocurrió un error inesperado." });
    } finally {
      setSubmitting(false);
    }
  }

  const needsHint =
    requiring && requiredOptions.length === 0
      ? `“${requiring.name}” ya tiene registradas todas las dependencias posibles.`
      : undefined;

  return (
    <Card
      title="Registrar dependencia"
      description="Lea siempre: Para producir [A] necesito [B]."
      icon={Link2}
    >
      <form onSubmit={handleSubmit} className="space-y-4" noValidate>
        <Field label="Para producir…" htmlFor="dep-requiring">
          <select
            id="dep-requiring"
            value={requiringId}
            onChange={(e) => {
              setRequiringId(e.target.value);
              setRequiredId("");
              setFeedback(null);
            }}
            className={inputClass}
          >
            <option value="" disabled>
              Seleccione un producto o insumo
            </option>
            <OptionGroups elements={requiringOptions} />
          </select>
        </Field>

        <Field label="…necesito" htmlFor="dep-required" error={error && required ? error : null} hint={needsHint}>
          <select
            id="dep-required"
            value={requiredId}
            onChange={(e) => {
              setRequiredId(e.target.value);
              setFeedback(null);
            }}
            disabled={!requiring || requiredOptions.length === 0}
            className={inputClass}
            aria-invalid={error && required ? true : undefined}
            aria-describedby={error && required ? "dep-required-error" : undefined}
          >
            <option value="" disabled>
              {requiring ? "Seleccione lo que necesita" : "Primero elija qué va a producir"}
            </option>
            <OptionGroups elements={requiredOptions} />
          </select>
        </Field>

        {requiring && required && !error && (
          <p className="rounded-xl bg-brand-100 px-3 py-2.5 text-sm text-ink-900">
            Para producir <strong>{requiring.name}</strong> necesito <strong>{required.name}</strong>
          </p>
        )}

        <FormFeedback feedback={feedback} />

        <button type="submit" disabled={!canSubmit} className={primaryButtonClass}>
          {submitting && <Loader2 className="size-4 animate-spin" aria-hidden />}
          {submitting ? "Guardando…" : "Registrar dependencia"}
        </button>
      </form>
    </Card>
  );
}