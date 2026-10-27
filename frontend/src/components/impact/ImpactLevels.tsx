import { Card } from "@/components/ui/Card";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { ImpactResponseDTO } from "@/lib/types";

export function ImpactLevels({ result }: Readonly<{ result: ImpactResponseDTO }>) {
  const isFailure = result.mode === "impact";

  return (
    <Card
      title={isFailure ? "Elementos afectados" : "Elementos necesarios"}
      description="Del más cercano al más lejano del elemento consultado."
    >
      <ol className="max-h-[520px] space-y-5 overflow-y-auto pr-1">
        {result.levels.map((level) => (
          <li key={level.level}>
            <h3 className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-ink-500">
              <span>{level.label}</span>
              <span className="rounded-full bg-ink-100 px-2 py-0.5 text-ink-700">{level.elements.length}</span>
            </h3>
            <ul className="space-y-2">
              {level.elements.map((e) => (
                <li key={e.id} className="rounded-xl border border-ink-100 bg-white px-3 py-2.5">
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-sm font-medium text-ink-900">{e.name}</span>
                    <TypeBadge type={e.element_type} />
                  </div>
                  <p className="mt-1 text-xs text-ink-500">{e.reason}</p>
                  {e.path.length > 2 && (
                    <p className="mt-1 text-xs text-ink-500">Ruta: {e.path.join(" → ")}</p>
                  )}
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
    </Card>
  );
}