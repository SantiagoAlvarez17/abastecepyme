from pydantic import BaseModel
from uuid import UUID

class DependencyCreateDTO(BaseModel):
    requiring_element_id: UUID
    required_element_id: UUID

class DependencyResponseDTO(BaseModel):
    requiring_element_id: UUID
    required_element_id: UUID

    class Config:
        orm_mode = True
