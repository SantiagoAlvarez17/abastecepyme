from pydantic import BaseModel, Field
from uuid import UUID
from abastecepyme.domain.enums.element_type import ElementType

class ElementCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    element_type: ElementType

class ElementResponseDTO(BaseModel):
    id: UUID
    name: str
    element_type: ElementType
    is_active: bool

    class Config:
        orm_mode = True
