from uuid import UUID

from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.application.dtos.impact_dto import ImpactResponseDTO
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.graph.dependency_graph import DependencyGraph
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.core.exceptions import ElementNotFoundException


class AnalyzeImpactUseCase:
    """Recorre dependencias para identificar la cadena de impacto o de suministro."""

    def __init__(
        self,
        element_repository: ElementRepository,
        dependency_repository: DependencyRepository,
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self, element_id: UUID) -> ImpactResponseDTO:
        graph = DependencyGraph.build(
            self.element_repository.get_all(active_only=True),
            self.dependency_repository.get_all(),
        )
        if not graph.has_node(element_id):
            raise ElementNotFoundException(str(element_id))

        element = graph.get_node(element_id)
        follows_dependencies = element.element_type == ElementType.PRODUCTO
        visited_ids = graph.reachable_from(element_id, reverse=not follows_dependencies)
        visited_elements = [
            ElementResponseDTO(
                id=visited.id,
                name=visited.name,
                element_type=visited.element_type,
                is_active=visited.is_active,
            )
            for visited in (graph.get_node(node_id) for node_id in visited_ids)
        ]

        if follows_dependencies:
            direction = "hacia los elementos requeridos por este producto"
            message = (
                f"La cadena de {element.name} alcanza {len(visited_elements)} "
                "elemento(s) requerido(s)."
                if visited_elements
                else f"{element.name} no tiene dependencias registradas."
            )
        else:
            direction = "hacia quienes dependen de este elemento"
            message = (
                f"{element.name} afecta a {len(visited_elements)} elemento(s) "
                "de la cadena."
                if visited_elements
                else f"No hay elementos que dependan de {element.name}."
            )

        return ImpactResponseDTO(
            element=ElementResponseDTO(
                id=element.id,
                name=element.name,
                element_type=element.element_type,
                is_active=element.is_active,
            ),
            direction=direction,
            status="chain_found" if visited_elements else "no_dependencies",
            message=message,
            visited_elements=visited_elements,
        )
