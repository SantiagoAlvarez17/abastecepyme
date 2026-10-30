import type { LucideIcon } from "lucide-react";

interface Props {
  title: string;
  description?: string;
  icon?: LucideIcon;
  children: React.ReactNode;
}

export function Card({ title, description, icon: Icon, children }: Readonly<Props>) {
  return (
    <section className="rounded-2xl border border-ink-100 bg-white p-6 shadow-sm">
      <header className="mb-5 flex items-start gap-3">
        {Icon && (
          <div className="flex size-9 shrink-0 items-center justify-center rounded-lg bg-brand-100 text-brand-600">
            <Icon className="size-5" aria-hidden />
          </div>
        )}
        <div>
          <h2 className="text-base font-semibold text-ink-900">{title}</h2>
          {description && <p className="mt-0.5 text-sm text-ink-500">{description}</p>}
        </div>
      </header>
      {children}
    </section>
  );
}