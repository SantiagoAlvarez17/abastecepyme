interface FieldProps {
  label: string;
  htmlFor: string;
  error?: string | null;
  hint?: string;
  children: React.ReactNode;
}

export const inputClass =
  "w-full rounded-xl border border-ink-200 bg-white px-3 py-2.5 text-sm text-ink-900 placeholder:text-ink-300 focus:border-brand-500 focus:outline-2 focus:outline-brand-100 disabled:bg-ink-50 disabled:text-ink-300 aria-invalid:border-danger";

export const primaryButtonClass =
  "inline-flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-4 py-2.5 text-sm font-medium text-white transition-colors hover:bg-brand-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-brand-500 disabled:cursor-not-allowed disabled:bg-ink-200 disabled:text-ink-500";

export function Field({ label, htmlFor, error, hint, children }: Readonly<FieldProps>) {
  return (
    <div>
      <label htmlFor={htmlFor} className="mb-1.5 block text-sm font-medium text-ink-700">
        {label}
      </label>
      {children}
      {error ? (
        <p id={`${htmlFor}-error`} role="alert" className="mt-1.5 text-xs text-danger">
          {error}
        </p>
      ) : hint ? (
        <p className="mt-1.5 text-xs text-ink-500">{hint}</p>
      ) : null}
    </div>
  );
}