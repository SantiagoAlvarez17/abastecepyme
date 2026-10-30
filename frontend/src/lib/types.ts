export type ElementType = "proveedor" | "insumo" | "producto";

export interface ElementDTO {
  id: string;
  name: string;
  element_type: ElementType;
  is_active: boolean;
}

export interface DependencyDTO {
  requiring_element_id: string; // "Para producir ESTE..."
  required_element_id: string;  // "...necesito ESTE"
}

export interface GraphEdgeDTO extends DependencyDTO {
  description: string;
}

export interface GraphDTO {
  direction: string;
  nodes: ElementDTO[];
  edges: GraphEdgeDTO[];
  adjacency: Record<string, string[]>;
}

export interface ApiErrorBody {
  error_code: string;
  message: string;
  details?: { field: string; message: string }[];
}

// ---------- Feature 2: análisis de impacto ----------
export type ImpactMode = "impact" | "requirements";
export type ImpactOutcome = "chain" | "no_reach" | "isolated";

export interface ReachedElementDTO {
  id: string;
  name: string;
  element_type: ElementType;
  level: number;
  via_id: string;
  reason: string;
  path: string[];
}

export interface ImpactLevelDTO {
  level: number;
  label: string;
  elements: ReachedElementDTO[];
}

export interface ImpactResponseDTO {
  mode: ImpactMode;
  origin: ElementDTO;
  outcome: ImpactOutcome;
  summary: string;
  affected_count: number;
  max_level: number;
  affected_by_type: Partial<Record<ElementType, number>>;
  levels: ImpactLevelDTO[];
}