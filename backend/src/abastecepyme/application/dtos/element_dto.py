from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from abastecepyme.domain.enums.element_type import ElementType

class ElementCreateDTO(BaseModel):
    # Se recortan los espacios antes de validar: un nombre de solo espacios se rechaza
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=1, max_length=255)
    element_type: ElementType

class ElementResponseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    element_type: ElementType
    is_active: bool
