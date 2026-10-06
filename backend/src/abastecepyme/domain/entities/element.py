from uuid import UUID
from pydantic import BaseModel, Field
from abastecepyme.domain.enums.element_type import ElementType

class Element(BaseModel):
    """
    Entidad de Dominio: Elemento.
    Representa un nodo en el catálogo (Proveedor, Insumo o Producto).
    """
    id: UUID
    name: str = Field(..., min_length=1, max_length=255)
    element_type: ElementType
    is_active: bool = True
