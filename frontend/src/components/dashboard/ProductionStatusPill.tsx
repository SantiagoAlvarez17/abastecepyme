import clsx from "clsx";
import { AlertTriangle, CheckCircle2, CircleDashed, type LucideIcon } from "lucide-react";
import type { ProductionStatus } from "@/lib/types";

const STATUS: Record<ProductionStatus, { label: string; icon: LucideIcon; className: string }> = {
  valid: { label: "Plan de producción válido", icon: CheckCircle2, className: "bg-success-soft text-success" },
  cycle: { label: "Ciclo detectado", icon: AlertTriangle, className: "bg-danger-soft text-danger" },
  empty: { label: "Catálogo vacío", icon: CircleDashed, className: "bg-ink-100 text-ink-500" },
};

/** Compact production health indicator; the status itself is computed by the backend. */
export function ProductionStatusPill({ status }: Readonly<{ status: ProductionStatus }>) {
  const { label, icon: Icon, className } = STATUS[status];
  return (
    <span className={clsx("inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold", className)}>
      <Icon className="size-3.5" aria-hidden />
      {label}
    </span>
  );
}
