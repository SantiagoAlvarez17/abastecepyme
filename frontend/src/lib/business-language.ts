import type { ElementType, ImpactMode } from "./types";

export const TYPE_LABEL: Record<ElementType, string> = {
  proveedor: "Proveedor",
  insumo: "Insumo",
  producto: "Producto final",
};

export const TYPE_LABEL_PLURAL: Record<ElementType, string> = {
  proveedor: "Proveedores",
  insumo: "Insumos",
  producto: "Productos finales",
};

export const TYPE_ORDER: ElementType[] = ["proveedor", "insumo", "producto"];

export const TYPE_CLASSES: Record<ElementType, { text: string; soft: string; dot: string }> = {
  proveedor: { text: "text-proveedor", soft: "bg-proveedor-soft", dot: "bg-proveedor" },
  insumo: { text: "text-insumo", soft: "bg-insumo-soft", dot: "bg-insumo" },
  producto: { text: "text-producto", soft: "bg-producto-soft", dot: "bg-producto" },
};

export const MODE_LABEL: Record<ImpactMode, { title: string; hint: string }> = {
  impact: {
    title: "Simular indisponibilidad",
    hint: "Si este elemento no está disponible, ¿qué productos y procesos se afectan?",
  },
  requirements: {
    title: "Ver qué necesita",
    hint: "Para producir este elemento, ¿qué necesito hasta llegar a los proveedores?",
  },
};

export const dependencySentence = (producer: string, needed: string) =>
  `Para producir ${producer} necesito ${needed}`;