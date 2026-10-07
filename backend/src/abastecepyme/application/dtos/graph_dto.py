from typing import Dict, List
from uuid import UUID
from pydantic import BaseModel
from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.application.dtos.dependency_dto import DependencyResponseDTO

class GraphResponseDTO(BaseModel):
    direction: str
    nodes: List[ElementResponseDTO]
    edges: List[DependencyResponseDTO]
    adjacency: Dict[UUID, List[UUID]]
