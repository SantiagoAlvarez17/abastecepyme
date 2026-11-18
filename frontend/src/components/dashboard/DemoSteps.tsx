import clsx from "clsx";
import { Check } from "lucide-react";
import type { ProductionStatus } from "@/lib/types";

interface Props {
  hasDependencies: boolean;
  simulated: boolean;
  productionStatus: ProductionStatus;
}

interface Step {
  title: string;
  detail: string;
  done: boolean;
  alert?: boolean;
}

/** Progress of the client's acceptance demo, derived only from backend data and the current query. */
export function DemoSteps({ hasDependencies, simulated, productionStatus }: Readonly<Props>) {
  const steps: Step[] = [
    {
      title: "Cargar dependencia",
      detail: hasDependencies ? "La red tiene dependencias registradas" : "Registre la primera dependencia",
      done: hasDependencies,
    },
    {
      title: "Simular indisponibilidad",
      detail: simulated ? "Consecuencias identificadas en el mapa" : "Elija qué proveedor o insumo falla",
      done: simulated,
    },
    {
      title: "Orden o alerta de ciclo",
      detail:
        productionStatus === "cycle"
          ? "Ciclo detectado: no hay orden válido"
          : productionStatus === "valid"
            ? "Existe un orden de preparación válido"
            : "Sin elementos para ordenar",
      done: productionStatus !== "empty",
      alert: productionStatus === "cycle",
    },
  ];

  return (
    <ol className="grid gap-3 sm:grid-cols-3" aria-label="Flujo de la demostración">
      {steps.map((step, index) => (
        <li
          key={step.title}
          className={clsx(
            "flex items-start gap-3 rounded-2xl border bg-white p-4 shadow-sm",
            step.alert ? "border-danger/30" : step.done ? "border-success/30" : "border-ink-100",
          )}
        >
          <span
            className={clsx(
              "flex size-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold",
              step.alert
                ? "bg-danger text-white"
                : step.done
                  ? "bg-success text-white"
                  : "bg-ink-100 text-ink-500",
            )}
            aria-hidden
          >
            {step.done && !step.alert ? <Check className="size-4" /> : index + 1}
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-ink-900">{step.title}</p>
            <p className="mt-0.5 text-xs text-ink-500">{step.detail}</p>
          </div>
        </li>
      ))}
    </ol>
  );
}
