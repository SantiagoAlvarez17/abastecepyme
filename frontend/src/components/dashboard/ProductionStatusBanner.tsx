import { Fragment } from "react";
import clsx from "clsx";
import { AlertTriangle, ArrowRight, CheckCircle2, CircleDashed } from "lucide-react";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { DashboardSummaryDTO } from "@/lib/types";

const TONE = {
  valid: { box: "border-success/25 bg-success-soft", icon: CheckCircle2, iconClass: "text-success" },
  cycle: { box: "border-danger/25 bg-danger-soft", icon: AlertTriangle, iconClass: "text-danger" },
  empty: { box: "border-ink-200 bg-white", icon: CircleDashed, iconClass: "text-ink-500" },
} as const;

/** Headline of the dashboard: can production be organized right now, and if not, why. */
export function ProductionStatusBanner({ production }: Readonly<{ production: DashboardSummaryDTO["production"] }>) {
  const tone = TONE[production.status];
  const Icon = tone.icon;

  return (
    <section role={production.status === "cycle" ? "alert" : "status"} className={clsx("rounded-2xl border p-5", tone.box)}>
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex min-w-0 items-start gap-3">
          <Icon className={clsx("mt-0.5 size-6 shrink-0", tone.iconClass)} aria-hidden />
          <div className="min-w-0">
            <h2 className="text-base font-semibold text-ink-900">
              {production.status === "cycle"
                ? "Alerta: las dependencias forman un ciclo"
                : production.status === "valid"
                  ? "La producción se puede organizar"
                  : "Todavía no hay nada que organizar"}
            </h2>
            <p className="mt-1 text-sm text-ink-700">{production.message}</p>
          </div>
        </div>
        {production.status !== "empty" && (
          <a href="#orden" className="shrink-0 text-sm font-medium text-brand-600 hover:underline">
            {production.status === "cycle" ? "Ver detalle del ciclo" : "Ver orden de preparación"}
          </a>
        )}
      </div>

      {production.cycles.map((cycle) => (
        <ol
          key={cycle.text}
          aria-label={`Ciclo: ${cycle.text}`}
          className="mt-4 flex flex-wrap items-center gap-2 sm:pl-9"
        >
          {cycle.elements.map((element, position) => (
            <Fragment key={`${element.id}-${position}`}>
              {position > 0 && <ArrowRight className="size-4 shrink-0 text-danger" aria-hidden />}
              <li className="flex items-center gap-2 rounded-lg border border-danger/30 bg-white px-2.5 py-1.5">
                <span className="text-sm font-semibold text-ink-900">{element.name}</span>
                <TypeBadge type={element.element_type} />
              </li>
            </Fragment>
          ))}
        </ol>
      ))}
    </section>
  );
}
