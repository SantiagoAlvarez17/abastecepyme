from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints
from uuid import UUID
from abastecepyme.domain.enums.element_type import ElementType

class ElementCreateDTO(BaseModel):
    # strip_whitespace: "   " cuenta como nombre vacío
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=255)]
    element_type: ElementType

class ElementResponseDTO(BaseModel):
    id: UUID
    name: str
    element_type: ElementType
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
