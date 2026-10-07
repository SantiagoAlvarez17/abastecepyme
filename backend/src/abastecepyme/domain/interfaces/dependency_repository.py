from abc import ABC, abstractmethod
from typing import List
from uuid import UUID
from abastecepyme.domain.entities.dependency import Dependency

class DependencyRepository(ABC):
    """
    Contrato abstracto (Puerto) para la persistencia de Dependencias.
    Asegura el Principio de Segregación de Interfaces (ISP) y DIP.
    """

    @abstractmethod
    def save(self, dependency: Dependency) -> Dependency:
        """Guarda una dependencia nueva. Lanza DuplicateDependencyException si ya existe."""

    @abstractmethod
    def exists(self, requiring_element_id: UUID, required_element_id: UUID) -> bool:
        """Indica si ya está registrada la arista requiring -> required."""

    @abstractmethod
    def get_all(self) -> List[Dependency]:
        """Devuelve todas las dependencias (aristas) registradas."""

    @abstractmethod
    def get_dependencies_for_element(self, element_id: UUID) -> List[Dependency]:
        """Devuelve las dependencias donde el elemento es el que requiere."""
