import clsx from "clsx";
import { TYPE_CLASSES } from "@/lib/business-language";
import type { ElementType } from "@/lib/types";

interface Props {
  label: string;
  value: number | string;
  tone?: ElementType;
  hint?: string;
}

export function StatCard({ label, value, tone, hint }: Readonly<Props>) {
  return (
    <div className="rounded-2xl border border-ink-100 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-2">
        {tone && <span className={clsx("size-2.5 rounded-full", TYPE_CLASSES[tone].dot)} aria-hidden />}
        <p className="text-sm font-medium text-ink-500">{label}</p>
      </div>
      <p className="mt-2 text-3xl font-semibold tracking-tight text-ink-900">{value}</p>
      {hint && <p className="mt-1 text-xs text-ink-500">{hint}</p>}
    </div>
  );
}