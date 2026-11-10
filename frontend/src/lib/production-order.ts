import type { ProductionStepDTO } from "./types";

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