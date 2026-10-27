from typing import Dict, List
from uuid import UUID

from pydantic import BaseModel

from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.enums.impact import ImpactMode, ImpactOutcome


class ReachedElementDTO(BaseModel):
    id: UUID
    name: str
    element_type: ElementType
    level: int            # 1 = relación directa con el origen
    via_id: UUID          # elemento a través del cual se llegó a este
    reason: str           # frase "Para producir X necesito Y" de la arista recorrida en este paso
    path: List[str]       # nombres desde el origen hasta este elemento


class ImpactLevelDTO(BaseModel):
    level: int
    label: str
    elements: List[ReachedElementDTO]


class ImpactResponseDTO(BaseModel):
    mode: ImpactMode
    origin: ElementResponseDTO
    outcome: ImpactOutcome
    summary: str
    affected_count: int
    max_level: int
    affected_by_type: Dict[str, int]
    levels: List[ImpactLevelDTO]  # los elementos visitados, en orden de recorrido, agrupados por nivel