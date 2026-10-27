"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { Boxes } from "lucide-react";
import { NAV_ITEMS } from "@/lib/navigation";

export function MobileNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-10 bg-ink-950 px-4 py-3 md:hidden">
      <div className="flex items-center gap-2 text-white">
        <Boxes className="size-5" aria-hidden />
        <span className="text-sm font-semibold">AbastecePyme</span>
      </div>
      <nav className="mt-3 flex gap-2" aria-label="Navegación principal">
        {NAV_ITEMS.map(({ href, label, icon: Icon }) => {
          const active = pathname.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={clsx(
                "flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-medium",
                active ? "bg-white text-ink-950" : "bg-white/10 text-ink-200",
              )}
            >
              <Icon className="size-4" aria-hidden />
              {label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}