from uuid import UUID
from pydantic import BaseModel

class Dependency(BaseModel):
    """
    Entidad de Dominio: Dependencia.
    Semántica: Para producir 'requiring_element_id' necesito 'required_element_id'.
    """
    requiring_element_id: UUID
    required_element_id: UUID
