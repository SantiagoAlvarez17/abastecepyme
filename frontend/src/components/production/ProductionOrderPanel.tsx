"use client";

import { useMemo } from "react";
import Link from "next/link";
import { AlertTriangle, CheckCircle2, ListOrdered, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { primaryButtonClass } from "@/components/ui/Field";
import { TypeBadge } from "@/components/ui/TypeBadge";
import { useProductionOrder } from "@/hooks/useProductionOrder";
import { CYCLE_ERROR_CODE, groupByStage } from "@/lib/production-order";

export function ProductionOrderPanel() {
  const { order, loading, error, generate } = useProductionOrder();

  const isCycle = error?.code === CYCLE_ERROR_CODE;
  const stages = useMemo(() => (order ? groupByStage(order.steps) : []), [order]);

  return (
    <Card
      title="Orden de preparación"
      description="Una secuencia de trabajo válida: cada elemento se prepara cuando ya está listo todo lo que necesita."
      icon={ListOrdered}
    >
      <button
        type="button"
        onClick={() => void generate()}
        disabled={loading}
        aria-busy={loading}
        className={primaryButtonClass}
      >
        {loading && <Loader2 className="size-4 animate-spin" aria-hidden />}
        {loading ? "Calculando…" : order || error ? "Volver a generar el orden" : "Generar orden de preparación"}
      </button>

      <div aria-live="polite" className="mt-5 space-y-4">
        {!loading && error && isCycle && (
          <div role="alert" className="flex items-start gap-4 rounded-2xl border border-danger/20 bg-danger-soft p-5">
            <AlertTriangle className="mt-0.5 size-6 shrink-0 text-danger" aria-hidden />
            <div>
              <h3 className="font-semibold text-danger">No existe un orden válido: las dependencias se contradicen</h3>
              <p className="mt-1 text-sm text-ink-700">{error.message}</p>
              <p className="mt-2 text-sm text-ink-700">
                Algunos elementos se necesitan entre sí, directa o indirectamente, y ninguno puede prepararse primero.
                Por eso no se muestra ningún orden.
              </p>
              <Link href="/compras" className="mt-3 inline-block text-sm font-medium text-brand-600 hover:underline">
                Revisar las dependencias en Compras
              </Link>
            </div>
          </div>
        )}

        {!loading && error && !isCycle && (
          <div role="alert" className="flex items-start gap-3 rounded-2xl border border-danger/20 bg-danger-soft p-4">
            <AlertTriangle className="mt-0.5 size-5 shrink-0 text-danger" aria-hidden />
            <div>
              <p className="font-medium text-danger">No se pudo generar el orden</p>
              <p className="mt-1 text-sm text-ink-700">{error.message}</p>
            </div>
          </div>
        )}

        {!loading && order && (
          <>
            <div className="flex items-start gap-3 rounded-2xl border border-success/20 bg-success-soft p-4">
              <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden />
              <p className="text-sm text-ink-900">{order.summary}</p>
            </div>

            <ol className="space-y-5">
              {stages.map(({ stage, steps }) => (
                <li key={stage}>
                  <h3 className="mb-2 flex flex-wrap items-center gap-2 text-xs font-semibold uppercase tracking-wide text-ink-500">
                    <span className="flex size-6 items-center justify-center rounded-full bg-ink-900 text-[11px] text-white">
                      {stage}
                    </span>
                    <span>Etapa {stage}</span>
                    {steps.length > 1 && (
                      <span className="rounded-full bg-ink-100 px-2 py-0.5 normal-case tracking-normal text-ink-700">
                        {steps.length} en paralelo
                      </span>
                    )}
                  </h3>
                  <ul className="grid gap-2.5 sm:grid-cols-2 xl:grid-cols-3">
                    {steps.map((step) => (
                      <li key={step.id} className="rounded-xl border border-ink-100 bg-white px-3 py-2.5">
                        <div className="flex items-start justify-between gap-3">
                          <span className="text-sm font-medium text-ink-900">
                            <span className="mr-1.5 tabular-nums text-ink-500">{step.position}.</span>
                            {step.name}
                          </span>
                          <TypeBadge type={step.element_type} />
                        </div>
                        <p className="mt-1 text-xs text-ink-500">
                          {step.requires.length === 0
                            ? "No necesita otros elementos"
                            : `Necesita: ${step.requires.join(", ")}`}
                        </p>
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ol>
          </>
        )}

        {!loading && !order && !error && (
          <p className="text-sm text-ink-500">Pulse el botón para calcular el orden de trabajo del catálogo actual.</p>
        )}
      </div>
    </Card>
  );
}