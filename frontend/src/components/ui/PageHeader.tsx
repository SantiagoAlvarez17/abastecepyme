interface Props {
  title: string;
  description: string;
  actions?: React.ReactNode;
}

export function PageHeader({ title, description, actions }: Readonly<Props>) {
  return (
    <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-ink-900">{title}</h1>
        <p className="mt-1 max-w-2xl text-sm text-ink-500">{description}</p>
      </div>
      {actions}
    </div>
  );
}