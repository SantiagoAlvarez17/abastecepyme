import { Card } from "@/components/ui/Card";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { ImpactResponseDTO } from "@/lib/types";

interface Props {
  result: ImpactResponseDTO;
  onSelectElement?: (id: string) => void;
}

export function ImpactLevels({ result, onSelectElement }: Readonly<Props>) {
  const isFailure = result.mode === "impact";

  return (
    <Card
      title={isFailure ? "Desglose por nivel de afectación" : "Desglose por nivel de requisitos"}
      description="Recorrido en anchura (BFS): del impacto directo al más distante en la cadena."
    >
      <ol className="max-h-[520px] space-y-5 overflow-y-auto pr-1">
        {result.levels.map((level) => (
          <li key={level.level}>
            <h3 className="mb-2 flex items-center justify-between text-xs font-semibold uppercase tracking-wide text-ink-500">
              <span>
                Nivel {level.level} · {level.label}
              </span>
              <span className="rounded-full bg-ink-100 px-2 py-0.5 text-ink-700">{level.elements.length}</span>
            </h3>
            <ul className="space-y-2.5">
              {level.elements.map((e) => (
                <li
                  key={e.id}
                  className="rounded-xl border border-ink-100 bg-white px-3.5 py-3 shadow-2xs transition-colors hover:border-ink-200"
                >
                  <div className="flex items-center justify-between gap-3">
                    {onSelectElement ? (
                      <button
                        type="button"
                        onClick={() => onSelectElement(e.id)}
                        className="text-left text-sm font-semibold text-ink-900 hover:text-brand-600 hover:underline"
                      >
                        {e.name}
                      </button>
                    ) : (
                      <span className="text-sm font-semibold text-ink-900">{e.name}</span>
                    )}
                    <TypeBadge type={e.element_type} />
                  </div>
                  <p className="mt-1.5 text-xs font-medium text-ink-700">“{e.reason}”</p>
                  <p className="mt-1 text-xs text-ink-500">
                    <span className="font-medium text-ink-700">Ruta:</span> {e.path.join(" → ")}
                  </p>
                </li>
              ))}
            </ul>
          </li>
        ))}
      </ol>
    </Card>
  );
}
