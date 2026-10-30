import type { LucideIcon } from "lucide-react";

interface Props {
  icon: LucideIcon;
  title: string;
  description: string;
}

export function EmptyState({ icon: Icon, title, description }: Readonly<Props>) {
  return (
    <div className="flex flex-col items-center rounded-2xl border border-dashed border-ink-200 bg-white px-6 py-14 text-center">
      <div className="flex size-12 items-center justify-center rounded-full bg-brand-100 text-brand-600">
        <Icon className="size-6" aria-hidden />
      </div>
      <h2 className="mt-4 text-base font-semibold text-ink-900">{title}</h2>
      <p className="mt-1 max-w-md text-sm text-ink-500">{description}</p>
    </div>
  );
}