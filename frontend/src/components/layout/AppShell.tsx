"use client";

import { usePathname } from "next/navigation";
import { RefreshCw, ShieldCheck } from "lucide-react";
import { useCatalogContext } from "@/context/CatalogContext";
import { NAV_ITEMS } from "@/lib/navigation";
import { MobileNav } from "./MobileNav";
import { Sidebar } from "./Sidebar";

function TopHeader() {
  const pathname = usePathname();
  const { graph, loading, refresh } = useCatalogContext();
  const activeNav = NAV_ITEMS.find((item) => pathname.startsWith(item.href)) ?? NAV_ITEMS[0];

  const isolatedCount = graph
    ? graph.nodes.filter((n) => {
        const hasOut = (graph.adjacency[n.id]?.length ?? 0) > 0;
        const hasIn = graph.edges.some((e) => e.required_element_id === n.id);
        return !hasOut && !hasIn;
      }).length
    : 0;

  return (
    <header className="sticky top-0 z-20 hidden border-b border-ink-100 bg-white/90 px-8 py-3.5 backdrop-blur md:flex md:items-center md:justify-between">
      <div className="flex items-center gap-3">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-brand-100 px-3 py-1 text-xs font-semibold text-brand-600">
          <ShieldCheck className="size-3.5" aria-hidden />
          Rol activo: {activeNav.role}
        </span>
        <span className="text-xs text-ink-500">
          Módulo de {activeNav.label}
        </span>
      </div>

      <div className="flex items-center gap-4">
        {graph && (
          <div className="flex items-center gap-3 text-xs text-ink-500">
            <span>
              <strong className="font-semibold text-ink-900">{graph.nodes.length}</strong> elementos
            </span>
            <span className="text-ink-200">•</span>
            <span>
              <strong className="font-semibold text-ink-900">{graph.edges.length}</strong> dependencias
            </span>
            {isolatedCount > 0 && (
              <>
                <span className="text-ink-200">•</span>
                <span className="rounded-full bg-proveedor-soft px-2 py-0.5 font-medium text-proveedor">
                  {isolatedCount} aislado{isolatedCount === 1 ? "" : "s"}
                </span>
              </>
            )}
          </div>
        )}
        <button
          type="button"
          onClick={() => void refresh()}
          disabled={loading}
          className="inline-flex items-center gap-1.5 rounded-xl border border-ink-200 bg-white px-3 py-1.5 text-xs font-medium text-ink-700 transition-colors hover:bg-ink-50 disabled:opacity-50"
        >
          <RefreshCw className={`size-3.5 ${loading ? "animate-spin" : ""}`} aria-hidden />
          Sincronizar
        </button>
      </div>
    </header>
  );
}

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <div className="min-h-screen md:flex">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <MobileNav />
        <TopHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-6 sm:px-8 sm:py-8">
          {children}
        </main>
      </div>
    </div>
  );
}
