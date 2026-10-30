"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import clsx from "clsx";
import { ArrowUpRight, Package, Search, SearchX } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { EmptyState } from "@/components/ui/EmptyState";
import { inputClass } from "@/components/ui/Field";
import { TypeBadge } from "@/components/ui/TypeBadge";
import { TYPE_LABEL_PLURAL, TYPE_ORDER } from "@/lib/business-language";
import type { ElementDTO, ElementType, GraphDTO } from "@/lib/types";

type Filter = ElementType | "todos";

interface Props {
  graph: GraphDTO;
  onSelect: (element: ElementDTO) => void;
}

const Count = ({ value }: Readonly<{ value: number }>) =>
  value === 0 ? <span className="text-ink-300">—</span> : <span className="font-semibold text-ink-900">{value}</span>;

export function CatalogTable({ graph, onSelect }: Readonly<Props>) {
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("todos");

  // Solo para mostrar: cuántos elementos requieren a cada uno (a partir de las aristas del backend).
  const dependentsCount = useMemo(() => {
    const counts = new Map<string, number>();
    for (const e of graph.edges) {
      counts.set(e.required_element_id, (counts.get(e.required_element_id) ?? 0) + 1);
    }
    return counts;
  }, [graph.edges]);

  const rows = useMemo(() => {
    const q = query.trim().toLowerCase();
    return graph.nodes
      .filter((n) => (filter === "todos" || n.element_type === filter) && n.name.toLowerCase().includes(q))
      .sort(
        (a, b) =>
          TYPE_ORDER.indexOf(a.element_type) - TYPE_ORDER.indexOf(b.element_type) ||
          a.name.localeCompare(b.name, "es"),
      );
  }, [graph.nodes, query, filter]);

  const chips: { value: Filter; label: string; count: number }[] = [
    { value: "todos", label: "Todos", count: graph.nodes.length },
    ...TYPE_ORDER.map((t) => ({
      value: t,
      label: TYPE_LABEL_PLURAL[t],
      count: graph.nodes.filter((n) => n.element_type === t).length,
    })),
  ];

  return (
    <Card
      title="Directorio del catálogo"
      description="Consulte el detalle de cada elemento o salte directamente a su análisis de impacto en Producción."
    >
      {graph.nodes.length === 0 ? (
        <EmptyState
          icon={Package}
          title="El catálogo está vacío"
          description="Registre su primer proveedor, insumo o producto con el formulario superior."
        />
      ) : (
        <>
          <div className="mb-4 flex flex-wrap items-center gap-3">
            <div className="relative min-w-56 flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-ink-300" aria-hidden />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Buscar proveedor, insumo o producto por nombre…"
                aria-label="Buscar elemento por nombre"
                className={clsx(inputClass, "pl-9")}
              />
            </div>
            <div className="flex flex-wrap gap-2" role="group" aria-label="Filtrar por tipo">
              {chips.map((c) => (
                <button
                  key={c.value}
                  type="button"
                  aria-pressed={filter === c.value}
                  onClick={() => setFilter(c.value)}
                  className={clsx(
                    "rounded-full border px-3 py-1.5 text-xs font-medium transition-colors focus-visible:outline-2 focus-visible:outline-brand-500",
                    filter === c.value
                      ? "border-ink-900 bg-ink-900 text-white"
                      : "border-ink-200 bg-white text-ink-700 hover:bg-ink-50",
                  )}
                >
                  {c.label} · {c.count}
                </button>
              ))}
            </div>
          </div>

          {rows.length === 0 ? (
            <EmptyState
              icon={SearchX}
              title="Sin resultados"
              description="Ningún elemento coincide con la búsqueda y el filtro actuales."
            />
          ) : (
            <div className="overflow-x-auto rounded-xl border border-ink-100">
              <table className="w-full text-left text-sm">
                <thead className="bg-ink-50 text-xs uppercase tracking-wide text-ink-500">
                  <tr>
                    <th scope="col" className="px-4 py-3 font-medium">Elemento</th>
                    <th scope="col" className="px-4 py-3 font-medium">Tipo</th>
                    <th scope="col" className="px-4 py-3 font-medium">Estado en red</th>
                    <th scope="col" className="px-4 py-3 text-right font-medium">Necesita</th>
                    <th scope="col" className="px-4 py-3 text-right font-medium">Lo necesitan</th>
                    <th scope="col" className="px-4 py-3 text-right font-medium">Acciones</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ink-100">
                  {rows.map((n) => {
                    const needs = graph.adjacency[n.id]?.length ?? 0;
                    const neededBy = dependentsCount.get(n.id) ?? 0;
                    const isolated = needs === 0 && neededBy === 0;
                    const defaultMode = n.element_type === "producto" && neededBy === 0 ? "requirements" : "impact";

                    return (
                      <tr key={n.id} className="transition-colors hover:bg-ink-50/80">
                        <td className="px-4 py-3">
                          <button
                            type="button"
                            onClick={() => onSelect(n)}
                            className="font-semibold text-ink-900 hover:text-brand-600 hover:underline focus-visible:outline-2 focus-visible:outline-brand-500"
                          >
                            {n.name}
                          </button>
                        </td>
                        <td className="px-4 py-3">
                          <TypeBadge type={n.element_type} />
                        </td>
                        <td className="px-4 py-3">
                          {isolated ? (
                            <span className="inline-flex items-center rounded-full bg-ink-100 px-2.5 py-0.5 text-xs font-medium text-ink-500">
                              Aislado
                            </span>
                          ) : (
                            <span className="inline-flex items-center rounded-full bg-success-soft px-2.5 py-0.5 text-xs font-medium text-success">
                              Conectado
                            </span>
                          )}
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums">
                          <Count value={needs} />
                        </td>
                        <td className="px-4 py-3 text-right tabular-nums">
                          <Count value={neededBy} />
                        </td>
                        <td className="px-4 py-3 text-right">
                          <Link
                            href={`/produccion?element=${n.id}&mode=${defaultMode}`}
                            className="inline-flex items-center gap-1 rounded-lg border border-ink-200 bg-white px-2.5 py-1 text-xs font-medium text-ink-700 transition-colors hover:border-brand-500 hover:text-brand-600"
                          >
                            Analizar
                            <ArrowUpRight className="size-3.5" aria-hidden />
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </Card>
  );
}
