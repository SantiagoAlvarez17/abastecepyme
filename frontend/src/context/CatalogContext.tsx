"use client";

import { createContext, useContext } from "react";
import { useCatalog } from "@/hooks/useCatalog";

type CatalogValue = ReturnType<typeof useCatalog>;

const CatalogContext = createContext<CatalogValue | null>(null);

export function CatalogProvider({ children }: Readonly<{ children: React.ReactNode }>) {
  const catalog = useCatalog();
  return <CatalogContext.Provider value={catalog}>{children}</CatalogContext.Provider>;
}

export function useCatalogContext(): CatalogValue {
  const ctx = useContext(CatalogContext);
  if (!ctx) throw new Error("useCatalogContext debe usarse dentro de CatalogProvider");
  return ctx;
}
