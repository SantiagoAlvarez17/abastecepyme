"use client";

import { useEffect, useMemo, useRef } from "react";
import { Unlink, X } from "lucide-react";
import { TypeBadge } from "@/components/ui/TypeBadge";
import type { ElementDTO, GraphDTO } from "@/lib/types";

interface Props {
  element: ElementDTO | null;
  graph: GraphDTO;
  onClose: () => void;
}

function ElementList({
  title,
  items,
  emptyText,
}: Readonly<{ title: string; items: ElementDTO[]; emptyText: string }>) {
  return (
    <div>
      <h3 className="text-xs font-semibold uppercase tracking-wide text-ink-500">{title}</h3>
      {items.length === 0 ? (
        <p className="mt-2 text-sm text-ink-500">{emptyText}</p>
      ) : (
        <ul className="mt-2 space-y-1.5">
          {items.map((i) => (
            <li key={i.id} className="flex items-center justify-between gap-3 rounded-lg bg-ink-50 px-3 py-2 text-sm">
              <span className="font-medium text-ink-900">{i.name}</span>
              <TypeBadge type={i.element_type} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function ElementDialog({ element, graph, onClose }: Readonly<Props>) {
  const ref = useRef<HTMLDialogElement>(null);
  const byId = useMemo(() => new Map(graph.nodes.map((n) => [n.id, n])), [graph.nodes]);

  useEffect(() => {
    const dialog = ref.current;
    if (!dialog) return;
    if (element && !dialog.open) dialog.showModal();
    if (!element && dialog.open) dialog.close();
  }, [element]);

  const lookup = (ids: string[]) => ids.map((id) => byId.get(id)).filter((n): n is ElementDTO => Boolean(n));

  const needs = element
    ? lookup(graph.edges.filter((e) => e.requiring_element_id === element.id).map((e) => e.required_element_id))
    : [];
  const neededBy = element
    ? lookup(graph.edges.filter((e) => e.required_element_id === element.id).map((e) => e.requiring_element_id))
    : [];
  const isolated = element !== null && needs.length === 0 && neededBy.length === 0;

  return (
    <dialog
      ref={ref}
      onClose={onClose}
      onClick={(e) => {
        if (e.target === ref.current) ref.current?.close();
      }}
      aria-labelledby="element-dialog-title"
      className="m-auto w-full max-w-lg rounded-2xl p-0 shadow-xl backdrop:bg-ink-950/50"
    >
      {element && (
        <div className="p-6">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h2 id="element-dialog-title" className="text-lg font-semibold text-ink-900">
                {element.name}
              </h2>
              <div className="mt-1.5">
                <TypeBadge type={element.element_type} />
              </div>
            </div>
            <button
              type="button"
              onClick={() => ref.current?.close()}
              aria-label="Cerrar"
              className="rounded-lg p-1.5 text-ink-500 hover:bg-ink-50 focus-visible:outline-2 focus-visible:outline-brand-500"
            >
              <X className="size-5" aria-hidden />
            </button>
          </div>

          {isolated && (
            <p className="mt-4 flex items-start gap-2 rounded-xl bg-proveedor-soft px-3 py-2.5 text-sm text-ink-900">
              <Unlink className="mt-0.5 size-4 shrink-0 text-proveedor" aria-hidden />
              Elemento aislado: no depende de nada y ningún producto lo necesita todavía.
            </p>
          )}

          <div className="mt-5 space-y-5">
            <ElementList title="Para producirlo necesita" items={needs} emptyText="No necesita otros elementos." />
            <ElementList title="Lo necesitan para producirse" items={neededBy} emptyText="Nadie lo necesita todavía." />
          </div>
        </div>
      )}
    </dialog>
  );
}