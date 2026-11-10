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