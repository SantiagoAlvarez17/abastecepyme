import dagre from "@dagrejs/dagre";
import { MarkerType, type Edge, type Node } from "@xyflow/react";
import type { ElementDTO, GraphDTO, ImpactMode } from "./types";

export const NODE_WIDTH = 208; // = w-52 en ElementNode
export const NODE_HEIGHT = 56; // = h-14 en ElementNode

export type NodeState = "normal" | "selected" | "related" | "dimmed" | "origin" | "affected";

export type ElementNodeData = { element: ElementDTO; state: NodeState };
export type ElementFlowNode = Node<ElementNodeData, "element">;

/**
 * Resultado de una consulta de la Feature 2, listo para pintarse.
 * - mode "impact": origen en rojo (punto de falla) y afectados en naranja.
 * - mode "requirements": origen y requisitos en azul (es una consulta, no una falla).
 */
export interface ImpactHighlight {
  mode: ImpactMode;
  originId: string;
  affectedIds: string[];
}

const COLORS = { normal: "#aab3c5", dim: "#e8ebf1", focus: "#2557d6", impact: "#dc2626" };

/** Solo posiciona las cajas (izquierda → derecha). No interpreta el grafo. */
export function computePositions(graph: GraphDTO): Map<string, { x: number; y: number }> {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 24, ranksep: 96 });
  g.setDefaultEdgeLabel(() => ({}));

  for (const n of graph.nodes) g.setNode(n.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  for (const e of graph.edges) g.setEdge(e.requiring_element_id, e.required_element_id);
  dagre.layout(g);

  const positions = new Map<string, { x: number; y: number }>();
  for (const n of graph.nodes) {
    const p = g.node(n.id);
    positions.set(n.id, { x: p.x - NODE_WIDTH / 2, y: p.y - NODE_HEIGHT / 2 });
  }
  return positions;
}

export function buildFlow(
  graph: GraphDTO,
  positions: Map<string, { x: number; y: number }>,
  selectedId: string | null,
  highlight?: ImpactHighlight,
): { nodes: ElementFlowNode[]; edges: Edge[] } {
  const focus = new Set<string>();
  let view: "none" | "selection" | "impact" = "none";

  if (highlight) {
    view = "impact";
    focus.add(highlight.originId);
    for (const id of highlight.affectedIds) focus.add(id);
  } else if (selectedId) {
    view = "selection";
    focus.add(selectedId);
    for (const e of graph.edges) {
      if (e.requiring_element_id === selectedId) focus.add(e.required_element_id);
      if (e.required_element_id === selectedId) focus.add(e.requiring_element_id);
    }
  }

  const isFailure = highlight?.mode === "impact";

  const stateOf = (id: string): NodeState => {
    if (view === "none") return "normal";
    if (view === "impact") {
      if (id === highlight?.originId) return isFailure ? "origin" : "selected";
      if (focus.has(id)) return isFailure ? "affected" : "related";
      return "dimmed";
    }
    return id === selectedId ? "selected" : focus.has(id) ? "related" : "dimmed";
  };

  const nodes: ElementFlowNode[] = graph.nodes.map((element) => ({
    id: element.id,
    type: "element",
    position: positions.get(element.id) ?? { x: 0, y: 0 },
    data: { element, state: stateOf(element.id) },
    draggable: false,
    connectable: false,
  }));

  const edges: Edge[] = graph.edges.map((e) => {
    const source = e.requiring_element_id;
    const target = e.required_element_id;
    const on =
      view === "impact"
        ? focus.has(source) && focus.has(target)
        : view === "selection"
          ? source === selectedId || target === selectedId
          : false;
    const color = on ? (isFailure ? COLORS.impact : COLORS.focus) : view === "none" ? COLORS.normal : COLORS.dim;

    return {
      id: `${source}->${target}`,
      source,
      target,
      animated: on,
      zIndex: on ? 10 : 0,
      markerEnd: { type: MarkerType.ArrowClosed, color, width: 16, height: 16 },
      style: { stroke: color, strokeWidth: on ? 2.25 : 1.5 },
    };
  });

  return { nodes, edges };
}