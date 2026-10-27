"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { Boxes } from "lucide-react";
import { NAV_ITEMS } from "@/lib/navigation";
import { ConnectionStatus } from "./ConnectionStatus";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden h-screen w-64 shrink-0 flex-col bg-ink-950 p-4 md:sticky md:top-0 md:flex">
      <div className="flex items-center gap-3 px-2 py-3">
        <div className="flex size-10 items-center justify-center rounded-xl bg-brand-600 text-white">
          <Boxes className="size-5" aria-hidden />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">AbastecePyme</p>
          <p className="text-xs text-ink-300">Control de abastecimiento</p>
        </div>
      </div>

      <p className="mt-6 px-3 text-[11px] font-medium uppercase tracking-wider text-ink-500">
        Vistas por rol
      </p>
      <nav className="mt-2 flex flex-col gap-1" aria-label="Navegación principal">
        {NAV_ITEMS.map(({ href, label, role, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={clsx(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 transition-colors focus-visible:outline-2 focus-visible:outline-brand-500",
                active ? "bg-white/10 text-white" : "text-ink-300 hover:bg-white/5 hover:text-white",
              )}
            >
              <Icon className="size-5 shrink-0" aria-hidden />
              <span className="flex flex-col leading-tight">
                <span className="text-sm font-medium">{label}</span>
                <span className="text-xs text-ink-500">{role}</span>
              </span>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto">
        <ConnectionStatus />
      </div>
    </aside>
  );
}