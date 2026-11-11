import type { CycleDTO, CycleElementDTO, CycleErrorBody, ProductionStepDTO } from "./types";
import type { CycleHighlight } from "./graph-view";

/** Código con el que el backend avisa que las dependencias se contradicen (hay un ciclo). */
export const CYCLE_ERROR_CODE = "ERR_CYCLE_DETECTED";

export interface StageGroup {
  stage: number;
  steps: ProductionStepDTO[];
}

/**
 * Agrupa los pasos del orden por etapa para mostrarlos. No calcula nada del grafo:
 * el orden y las etapas las decide el backend; aquí solo se presentan.
 */
export function groupByStage(steps: ProductionStepDTO[]): StageGroup[] {
  const groups = new Map<number, ProductionStepDTO[]>();
  for (const step of steps) {
    const group = groups.get(step.stage);
    if (group) group.push(step);
    else groups.set(step.stage, [step]);
  }
  return [...groups.entries()]
    .sort(([a], [b]) => a - b)
    .map(([stage, items]) => ({ stage, steps: items }));
}

export interface CycleReport {
  cycles: CycleDTO[];
  blockedByCycle: CycleElementDTO[];
}

/**
 * Extrae del error de la API el reporte del ciclo (qué ciclos hay y qué elementos solo dependen de ellos).
 * Devuelve null si el error no es de ciclo o no trae el detalle, para mostrar entonces solo el mensaje.
 */
export function parseCycleReport(error: { code: string; body: unknown } | null): CycleReport | null {
  if (!error || error.code !== CYCLE_ERROR_CODE) return null;
  const body = error.body as Partial<CycleErrorBody> | null;
  if (!body || !Array.isArray(body.cycles) || body.cycles.length === 0) return null;
  return { cycles: body.cycles, blockedByCycle: body.blocked_by_cycle ?? [] };
}

/** Qué resaltar en el mapa: los elementos de cada ciclo y las dependencias que lo cierran. */
export function cycleHighlightOf(report: CycleReport): CycleHighlight {
  const nodeIds = new Set<string>();
  const edgeKeys = new Set<string>();
  for (const cycle of report.cycles) {
    const path = cycle.elements;
    for (const element of path) nodeIds.add(element.id);
    for (let i = 0; i < path.length - 1; i++) edgeKeys.add(`${path[i].id}->${path[i + 1].id}`);
  }
  return { nodeIds: [...nodeIds], edgeKeys: [...edgeKeys] };
}
