import clsx from "clsx";
import { TYPE_CLASSES, TYPE_LABEL } from "@/lib/business-language";
import type { ElementType } from "@/lib/types";

export function TypeBadge({ type }: Readonly<{ type: ElementType }>) {
  const c = TYPE_CLASSES[type];
  return (
    <span className={clsx("inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium text-ink-700", c.soft)}>
      <span className={clsx("size-1.5 rounded-full", c.dot)} aria-hidden />
      {TYPE_LABEL[type]}
    </span>
  );
}