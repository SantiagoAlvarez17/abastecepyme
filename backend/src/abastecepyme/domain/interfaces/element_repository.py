from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID
from abastecepyme.domain.entities.element import Element

class ElementRepository(ABC):
    """
    Contrato abstracto (Puerto) para la persistencia de Elementos.
    Asegura el Principio de Inversión de Dependencias (DIP).
    """

    @abstractmethod
    def save(self, element: Element) -> Element:
        pass

    @abstractmethod
    def get_by_id(self, element_id: UUID) -> Optional[Element]:
        pass

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[Element]:
        """Búsqueda sin distinguir mayúsculas/minúsculas."""
        pass

    @abstractmethod
    def get_all(self, active_only: bool = True) -> List[Element]:
        pass
