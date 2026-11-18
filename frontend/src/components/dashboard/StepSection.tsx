interface Props {
  step: number;
  title: string;
  id?: string;
  children: React.ReactNode;
}

/** Numbered block of the guided demo flow (load → simulate → order). */
export function StepSection({ step, title, id, children }: Readonly<Props>) {
  return (
    <section id={id} className="scroll-mt-24 space-y-3" aria-label={`Paso ${step}: ${title}`}>
      <h2 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-ink-500">
        <span className="flex size-6 items-center justify-center rounded-full bg-brand-600 text-[11px] text-white">
          {step}
        </span>
        {title}
      </h2>
      {children}
    </section>
  );
}
