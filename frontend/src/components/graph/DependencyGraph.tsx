"use client";

import { useMemo, useState } from "react";
import { Background, BackgroundVariant, Controls, Panel, ReactFlow, type NodeTypes } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import clsx from "clsx";
import { Network } from "lucide-react";
import { EmptyState } from "@/components/ui/EmptyState";
import { TYPE_CLASSES, TYPE_LABEL, TYPE_ORDER } from "@/lib/business-language";
import { buildFlow, computePositions, type ImpactHighlight } from "@/lib/graph-view";
import type { GraphDTO } from "@/lib/types";
import { ElementNode } from "./ElementNode";

const nodeTypes: NodeTypes = { element: ElementNode };

interface Props {
  graph: GraphDTO;
  /** Feature 2: resalta el resultado de una consulta de impacto o de requisitos. */
  highlight?: ImpactHighlight;
  /** Si se entrega, un clic en un nodo llama a esta función en lugar de seleccionarlo dentro del grafo. */
  onSelectElement?: (elementId: string) => void;
  className?: string;
}

function LegendDot({ className, label }: Readonly<{ className: string; label: string }>) {
  return (
    <span className="inline-flex items-center gap-1.5">
      <span className={clsx("size-2.5 rounded-full", className)} aria-hidden />
      {label}
    </span>
  );
}

export function DependencyGraph({ graph, highlight, onSelectElement, className }: Readonly<Props>) {
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // El layout solo se recalcula cuando cambia la estructura, no al seleccionar.
  const positions = useMemo(() => computePositions(graph), [graph]);
  const flow = useMemo(
    () => buildFlow(graph, positions, selectedId, highlight),
    [graph, positions, selectedId, highlight],
  );

  const selected = graph.nodes.find((n) => n.id === selectedId);
  const needsCount = graph.edges.filter((e) => e.requiring_element_id === selectedId).length;
  const neededByCount = graph.edges.filter((e) => e.required_element_id === selectedId).length;

  if (graph.nodes.length === 0) {
    return (
      <EmptyState
        icon={Network}
        title="Todavía no hay red para mostrar"
        description="Cuando registre elementos y dependencias, aquí verá cómo se conectan."
      />
    );
  }

  return (
    <div
      className={clsx("h-[440px] overflow-hidden rounded-xl border border-ink-100 bg-ink-50 md:h-[560px]", className)}
      role="img"
      aria-label={`Red de dependencias con ${graph.nodes.length} elementos y ${graph.edges.length} dependencias. La tabla del catálogo tiene la misma información en texto.`}
    >
      <ReactFlow
        key={`${graph.nodes.length}-${graph.edges.length}`}
        nodes={flow.nodes}
        edges={flow.edges}
        nodeTypes={nodeTypes}
        onNodeClick={(_, node) => {
          if (onSelectElement) onSelectElement(node.id);
          else setSelectedId((cur) => (cur === node.id ? null : node.id));
        }}
        onPaneClick={() => setSelectedId(null)}
        nodesDraggable={false}
        nodesConnectable={false}
        fitView
        fitViewOptions={{ padding: 0.16 }}
        minZoom={0.25}
        maxZoom={1.75}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1.5} color="#d7dce6" />
        <Controls showInteractive={false} />

        <Panel position="top-left">
          <div className="rounded-xl border border-ink-100 bg-white/95 px-3.5 py-2.5 text-xs text-ink-700 shadow-sm backdrop-blur">
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 font-medium">
              {TYPE_ORDER.map((t) => (
                <LegendDot key={t} className={TYPE_CLASSES[t].dot} label={TYPE_LABEL[t]} />
              ))}
            </div>
            <p className="mt-1.5 text-ink-500">Arista A → B: “Para producir A necesito B”.</p>
            {highlight?.mode === "impact" && (
              <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 border-t border-ink-100 pt-1.5 font-medium">
                <LegendDot className="bg-danger" label="Punto de falla (Origen)" />
                <LegendDot className="bg-proveedor" label="Afectado por nivel (N1, N2…)" />
              </div>
            )}
            {highlight?.mode === "requirements" && (
              <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-1 border-t border-ink-100 pt-1.5 font-medium">
                <LegendDot className="bg-brand-600" label="Elemento consultado" />
                <LegendDot className="bg-brand-500" label="Requisito por nivel (N1, N2…)" />
              </div>
            )}
          </div>
        </Panel>

        {selected && !highlight && (
          <Panel position="top-right">
            <div className="max-w-64 rounded-xl border border-ink-100 bg-white/95 px-3.5 py-2.5 text-xs shadow-sm backdrop-blur">
              <p className="font-semibold text-ink-900">{selected.name}</p>
              <p className="mt-0.5 text-ink-500">
                Requiere {needsCount} · Requerido por {neededByCount}
              </p>
            </div>
          </Panel>
        )}
      </ReactFlow>
    </div>
  );
}
