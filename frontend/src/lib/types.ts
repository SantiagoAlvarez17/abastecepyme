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


// ---------- Feature 3: orden de preparación ----------
export interface ProductionStepDTO {
  position: number; // lugar en el orden de trabajo (1, 2, 3, ...)
  stage: number;    // los pasos de una misma etapa pueden prepararse en paralelo
  id: string;
  name: string;
  element_type: ElementType;
  requires: string[]; // nombres de sus requisitos directos (todos aparecen antes)
}

export interface ProductionOrderDTO {
  total_elements: number;
  stage_count: number;
  summary: string;
  steps: ProductionStepDTO[];
}

/** Un elemento mencionado en el reporte de un ciclo. */
export interface CycleElementDTO {
  id: string;
  name: string;
  element_type: ElementType;
}

/**
 * Un ciclo: camino cerrado en el sentido de las dependencias. El primer elemento se repite al final:
 * [Pan, Masa madre, Pan] = "para producir Pan necesito Masa madre y para producir Masa madre necesito Pan".
 */
export interface CycleDTO {
  elements: CycleElementDTO[];
  text: string; // "Pan → Masa madre → Pan"
}

/** Cuerpo del 409 ERR_CYCLE_DETECTED de GET /production-order. */
export interface CycleErrorBody {
  error_code: string;
  message: string;
  cycles: CycleDTO[];
  blocked_by_cycle: CycleElementDTO[]; // no forman parte del ciclo, pero dependen de él
}
