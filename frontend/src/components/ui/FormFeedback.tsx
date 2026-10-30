import clsx from "clsx";
import { AlertCircle, CheckCircle2 } from "lucide-react";

export interface Feedback {
  kind: "success" | "error";
  text: string;
}

export function FormFeedback({ feedback }: Readonly<{ feedback: Feedback | null }>) {
  if (!feedback) return null;
  const ok = feedback.kind === "success";
  const Icon = ok ? CheckCircle2 : AlertCircle;

  return (
    <div
      role={ok ? "status" : "alert"}
      className={clsx(
        "flex items-start gap-2 rounded-xl px-3 py-2.5 text-sm text-ink-900",
        ok ? "bg-success-soft" : "bg-danger-soft",
      )}
    >
      <Icon className={clsx("mt-0.5 size-4 shrink-0", ok ? "text-success" : "text-danger")} aria-hidden />
      <span>{feedback.text}</span>
    </div>
  );
}