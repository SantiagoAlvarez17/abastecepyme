from typing import List
from uuid import UUID

from pydantic import BaseModel

from abastecepyme.domain.enums.element_type import ElementType


class ProductionStepDTO(BaseModel):
    position: int            # lugar en el orden de trabajo (1, 2, 3, ...)
    stage: int               # etapa; los pasos de una misma etapa pueden prepararse en paralelo
    id: UUID
    name: str
    element_type: ElementType
    requires: List[str]      # nombres de sus requisitos directos (todos aparecen antes en el orden)


class ProductionOrderResponseDTO(BaseModel):
    total_elements: int
    stage_count: int
    summary: str
    steps: List[ProductionStepDTO]  # el orden de trabajo, de la primera a la última preparación


# ---------- Respuesta de error cuando hay un ciclo (409 ERR_CYCLE_DETECTED) ----------
class CycleElementDTO(BaseModel):
    id: UUID
    name: str
    element_type: ElementType


class CycleDTO(BaseModel):
    # Camino cerrado en el sentido de las aristas: el primer elemento se repite al final.
    # [Pan, Masa madre, Pan] = "para producir Pan necesito Masa madre y para producir Masa madre necesito Pan"
    elements: List[CycleElementDTO]
    text: str  # el mismo camino como texto: "Pan → Masa madre → Pan"


class CycleErrorResponseDTO(BaseModel):
    error_code: str  # ERR_CYCLE_DETECTED
    message: str
    cycles: List[CycleDTO]  # un ciclo representativo por cada grupo de elementos que se necesitan entre sí
    blocked_by_cycle: List[CycleElementDTO]  # no forman parte del ciclo, pero dependen de él
