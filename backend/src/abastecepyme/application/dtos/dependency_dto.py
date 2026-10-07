from pydantic import BaseModel, ConfigDict
from uuid import UUID

class DependencyCreateDTO(BaseModel):
    requiring_element_id: UUID
    required_element_id: UUID

class DependencyResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    requiring_element_id: UUID
    required_element_id: UUID