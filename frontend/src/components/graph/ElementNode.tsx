"use client";

import clsx from "clsx";
import { Handle, Position, type NodeProps } from "@xyflow/react";
import { TYPE_CLASSES, TYPE_LABEL } from "@/lib/business-language";
import type { ElementFlowNode, NodeState } from "@/lib/graph-view";

const STATE_CLASSES: Record<NodeState, string> = {
  normal: "border-ink-200 bg-white hover:border-ink-300",
  selected: "border-brand-600 bg-white ring-2 ring-brand-500/35",
  related: "border-brand-500 bg-brand-100/40",
  dimmed: "border-ink-100 bg-white opacity-35",
  origin: "border-danger bg-danger-soft ring-2 ring-danger/40",
  affected: "border-proveedor bg-proveedor-soft ring-1 ring-proveedor/30",
};

export function ElementNode({ data }: NodeProps<ElementFlowNode>) {
  const { element, state, level, mode } = data;
  const c = TYPE_CLASSES[element.element_type];

  const badge =
    state === "origin"
      ? { text: "Falla", cls: "bg-danger text-white" }
      : state === "selected" && mode === "requirements"
        ? { text: "Origen", cls: "bg-brand-600 text-white" }
        : typeof level === "number"
          ? {
              text: `Nivel ${level}`,
              cls:
                mode === "impact"
                  ? "bg-proveedor text-white"
                  : "bg-brand-600 text-white",
            }
          : null;

  return (
    <div
      className={clsx(
        "flex h-[60px] w-56 cursor-pointer items-center justify-between gap-2.5 rounded-xl border px-3 shadow-sm transition-all",
        STATE_CLASSES[state],
      )}
    >
      <Handle type="target" position={Position.Left} className="size-2! border-0! bg-ink-300!" />
      <div className="flex min-w-0 items-center gap-2.5">
        <span className={clsx("h-8 w-1.5 shrink-0 rounded-full", c.dot)} aria-hidden />
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold text-ink-900" title={element.name}>
            {element.name}
          </p>
          <p className={clsx("text-xs font-medium", c.text)}>{TYPE_LABEL[element.element_type]}</p>
        </div>
      </div>
      {badge && (
        <span className={clsx("shrink-0 rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-wide", badge.cls)}>
          {badge.text}
        </span>
      )}
      <Handle type="source" position={Position.Right} className="size-2! border-0! bg-ink-300!" />
    </div>
  );
}
