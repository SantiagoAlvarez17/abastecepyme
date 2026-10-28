from typing import Literal, List
from pydantic import BaseModel
from abastecepyme.application.dtos.element_dto import ElementResponseDTO


class ImpactResponseDTO(BaseModel):
    element: ElementResponseDTO
    direction: str
    status: Literal["no_dependencies", "chain_found"]
    message: str
    visited_elements: List[ElementResponseDTO]
