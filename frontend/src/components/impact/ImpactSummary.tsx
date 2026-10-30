import clsx from "clsx";
import { AlertTriangle, CheckCircle2, Network, Unlink, type LucideIcon } from "lucide-react";
import { StatCard } from "@/components/ui/StatCard";
import { TypeBadge } from "@/components/ui/TypeBadge";
import { TYPE_ORDER } from "@/lib/business-language";
import type { ImpactResponseDTO } from "@/lib/types";

type Tone = "danger" | "brand" | "success" | "neutral";

const TONES: Record<Tone, { box: string; icon: string }> = {
  danger: { box: "border-danger/20 bg-danger-soft", icon: "text-danger" },
  brand: { box: "border-brand-500/20 bg-brand-100", icon: "text-brand-600" },
  success: { box: "border-success/20 bg-success-soft", icon: "text-success" },
  neutral: { box: "border-ink-200 bg-white", icon: "text-ink-500" },
};

function describe(r: ImpactResponseDTO): { tone: Tone; icon: LucideIcon; title: string } {
  if (r.outcome === "isolated") return { tone: "neutral", icon: Unlink, title: "Elemento aislado" };
  if (r.outcome === "no_reach") {
    return {
      tone: "success",
      icon: CheckCircle2,
      title: r.mode === "impact" ? "Sin afectación en la cadena" : "No depende de otros elementos",
    };
  }
  return r.mode === "impact"
    ? { tone: "danger", icon: AlertTriangle, title: "Afectación en cadena" }
    : { tone: "brand", icon: Network, title: "Cadena de abastecimiento" };
}

export function ImpactSummary({ result }: Readonly<{ result: ImpactResponseDTO }>) {
  const { tone, icon: Icon, title } = describe(result);
  const chain = result.outcome === "chain";
  const isFailure = result.mode === "impact";

  return (
    <section className="space-y-4" aria-live="polite">
      <div className={clsx("flex items-start gap-4 rounded-2xl border p-5", TONES[tone].box)}>
        <Icon className={clsx("mt-0.5 size-6 shrink-0", TONES[tone].icon)} aria-hidden />
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-base font-semibold text-ink-900">{title}</h2>
            {chain && isFailure && (
              <span className="rounded-full bg-danger px-2.5 py-0.5 text-xs font-medium text-white">
                Punto crítico
              </span>
            )}
          </div>
          <p className="mt-1 text-sm text-ink-700">{result.summary}</p>
        </div>
      </div>

      {chain && (
        <div className="grid gap-4 sm:grid-cols-3">
          <StatCard label={isFailure ? "Elementos afectados" : "Elementos necesarios"} value={result.affected_count} />
          <StatCard
            label="Niveles de la cadena"
            value={result.max_level}
            hint={isFailure ? "1 = afectación directa" : "1 = requisito directo"}
          />
          <div className="rounded-2xl border border-ink-100 bg-white p-5 shadow-sm">
            <p className="text-sm font-medium text-ink-500">Por tipo</p>
            <ul className="mt-2 space-y-1.5">
              {TYPE_ORDER.filter((t) => result.affected_by_type[t]).map((t) => (
                <li key={t} className="flex items-center justify-between gap-2">
                  <TypeBadge type={t} />
                  <span className="text-sm font-semibold tabular-nums text-ink-900">{result.affected_by_type[t]}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </section>
  );
}