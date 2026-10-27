"use client";

import clsx from "clsx";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { TYPE_CLASSES, TYPE_LABEL } from "@/lib/business-language";
import type { ElementFlowNode, NodeState } from "@/lib/graph-view";

const STATE_CLASSES: Record<NodeState, string> = {
  normal: "border-ink-200 bg-white",
  selected: "border-brand-500 bg-white ring-2 ring-brand-500/40",
  related: "border-brand-500 bg-white",
  dimmed: "border-ink-100 bg-white opacity-40",
  origin: "border-danger bg-danger-soft ring-2 ring-danger/40",
  affected: "border-proveedor bg-proveedor-soft",
};

export function ElementNode({ data }: NodeProps<ElementFlowNode>) {
  const { element, state } = data;
  const c = TYPE_CLASSES[element.element_type];

  return (
    <div
      className={clsx(
        "flex h-14 w-52 cursor-pointer items-center gap-3 rounded-xl border px-3 shadow-sm transition-opacity",
        STATE_CLASSES[state],
      )}
    >
      <Handle type="target" position={Position.Left} className="size-2! border-0! bg-ink-300!" />
      <span className={clsx("h-8 w-1.5 shrink-0 rounded-full", c.dot)} aria-hidden />
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-ink-900" title={element.name}>
          {element.name}
        </p>
        <p className={clsx("text-xs", c.text)}>{TYPE_LABEL[element.element_type]}</p>
      </div>
      <Handle type="source" position={Position.Right} className="size-2! border-0! bg-ink-300!" />
    </div>
  );
}