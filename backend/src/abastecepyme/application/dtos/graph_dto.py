from typing import Dict, List
from uuid import UUID
from pydantic import BaseModel
from abastecepyme.application.dtos.element_dto import ElementResponseDTO

class GraphEdgeDTO(BaseModel):
    requiring_element_id: UUID
    required_element_id: UUID
    description: str  # "Para producir X necesito Y"

class GraphResponseDTO(BaseModel):
    direction: str
    nodes: List[ElementResponseDTO]
    edges: List[GraphEdgeDTO]
    adjacency: Dict[UUID, List[UUID]]
