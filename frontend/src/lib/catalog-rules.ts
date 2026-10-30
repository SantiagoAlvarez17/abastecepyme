import type { ElementDTO, ElementType, GraphEdgeDTO } from "./types";

export const MAX_NAME_LENGTH = 255;

// Espejo de las reglas del backend (el backend siempre las valida de nuevo).
export const CAN_REQUIRE: Record<ElementType, ElementType[]> = {
  proveedor: [],
  insumo: ["proveedor"],
  producto: ["insumo", "producto"],
};

const TYPE_RULE_MESSAGE: Record<ElementType, string> = {
  proveedor: "Un proveedor no depende de ningún elemento: es el origen de la cadena.",
  insumo: "Un insumo solo puede depender de un proveedor.",
  producto: "Un producto solo puede necesitar insumos u otros productos.",
};

export const canRequire = (requirer: ElementType, required: ElementType) =>
  CAN_REQUIRE[requirer].includes(required);

export const dependencyExists = (edges: GraphEdgeDTO[], requiringId: string, requiredId: string) =>
  edges.some((e) => e.requiring_element_id === requiringId && e.required_element_id === requiredId);

export function validateElementName(name: string, existing: ElementDTO[]): string | null {
  const clean = name.trim();
  if (clean.length === 0) return "Escriba un nombre.";
  if (clean.length > MAX_NAME_LENGTH) return `El nombre no puede superar ${MAX_NAME_LENGTH} caracteres.`;
  if (existing.some((e) => e.name.trim().toLowerCase() === clean.toLowerCase())) {
    return `Ya existe un elemento llamado “${clean}”.`;
  }
  return null;
}

export function validateDependency(
  requiring: ElementDTO | undefined,
  required: ElementDTO | undefined,
  edges: GraphEdgeDTO[],
): string | null {
  if (!requiring || !required) return "Seleccione ambos elementos.";
  if (requiring.id === required.id) return "Un elemento no puede necesitarse a sí mismo.";
  if (!canRequire(requiring.element_type, required.element_type)) {
    return TYPE_RULE_MESSAGE[requiring.element_type];
  }
  if (dependencyExists(edges, requiring.id, required.id)) return "Esta dependencia ya está registrada.";
  return null;
}