from typing import List
from uuid import UUID

from pydantic import BaseModel, field_validator

from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.domain.enums.element_type import ElementType


class UnavailabilitySimulationRequestDTO(BaseModel):
    element_ids: List[UUID]

    @field_validator("element_ids")
    @classmethod
    def validate_element_ids(cls, element_ids: List[UUID]) -> List[UUID]:
        if not element_ids:
            raise ValueError("Debe seleccionar al menos un elemento.")
        if len(set(element_ids)) != len(element_ids):
            raise ValueError("No se permiten identificadores repetidos.")
        return element_ids


class SimulatedImpactElementDTO(BaseModel):
    id: UUID
    name: str
    element_type: ElementType
    level: int
    via_id: UUID
    source_id: UUID
    path: List[str]


class SimulatedImpactLevelDTO(BaseModel):
    level: int
    elements: List[SimulatedImpactElementDTO]


class UnavailabilitySimulationResponseDTO(BaseModel):
    sources: List[ElementResponseDTO]
    affected_count: int
    max_level: int
    levels: List[SimulatedImpactLevelDTO]
    stopped_products: List[ElementResponseDTO]
    available_products: List[ElementResponseDTO]
    summary: str
