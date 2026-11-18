import { ShieldAlert, Zap } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { CriticalPointDTO } from "@/lib/types";

interface Props {
  points: CriticalPointDTO[];
  totalProducts: number;
  activeId: string | null;
  onSimulate: (elementId: string) => void;
}

const MAX_LISTED_PRODUCTS = 4;

function listProducts(products: string[]): string {
  const shown = products.slice(0, MAX_LISTED_PRODUCTS).join(", ");
  const rest = products.length - MAX_LISTED_PRODUCTS;
  return rest > 0 ? `${shown} y ${rest} más` : shown;
}

/** Ranking computed by the backend: which supplier or input failure stops the most products. */
export function CriticalPointsCard({ points, totalProducts, activeId, onSimulate }: Readonly<Props>) {
  return (
    <Card
      title="Puntos críticos de abastecimiento"
      description="Proveedores e insumos ordenados por cuántos productos se detienen si fallan."
      icon={ShieldAlert}
    >
      {points.length === 0 ? (
        <p className="text-sm text-ink-500">
          Ningún proveedor o insumo tiene dependientes todavía: registre dependencias para ver los riesgos.
        </p>
      ) : (
        <ol className="space-y-3">
          {points.map((point, index) => {
            const share = totalProducts > 0 ? Math.round((point.affected_products / totalProducts) * 100) : 0;
            return (
              <li key={point.id} className="rounded-xl border border-ink-100 p-3.5">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex min-w-0 items-center gap-2">
                    <span className="w-5 text-sm font-semibold tabular-nums text-ink-500">{index + 1}.</span>
                    <span className="truncate text-sm font-semibold text-ink-900">{point.name}</span>
                    <TypeBadge type={point.element_type} />
                  </div>
                  <button
                    type="button"
                    onClick={() => onSimulate(point.id)}
                    aria-pressed={activeId === point.id}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-ink-200 bg-white px-2.5 py-1 text-xs font-medium text-ink-700 transition-colors hover:bg-ink-50 aria-pressed:border-danger aria-pressed:bg-danger-soft aria-pressed:text-danger"
                  >
                    <Zap className="size-3.5" aria-hidden />
                    {activeId === point.id ? "Simulando" : "Simular falla"}
                  </button>
                </div>
                <div className="mt-2.5 flex items-center gap-3">
                  <div
                    className="h-2 flex-1 overflow-hidden rounded-full bg-ink-100"
                    role="meter"
                    aria-valuemin={0}
                    aria-valuemax={totalProducts}
                    aria-valuenow={point.affected_products}
                    aria-label={`Productos detenidos por ${point.name}`}
                  >
                    <div className="h-full rounded-full bg-danger" style={{ width: `${share}%` }} />
                  </div>
                  <span className="shrink-0 text-xs font-medium tabular-nums text-ink-700">
                    {point.affected_products} de {totalProducts} productos
                  </span>
                </div>
                {point.products.length > 0 && (
                  <p className="mt-1.5 text-xs text-ink-500">Detiene: {listProducts(point.products)}</p>
                )}
              </li>
            );
          })}
        </ol>
      )}
    </Card>
  );
}
