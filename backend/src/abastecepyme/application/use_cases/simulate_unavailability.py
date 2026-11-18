from typing import Dict, List
from uuid import UUID

from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.application.dtos.unavailability_simulation_dto import (
    SimulatedImpactElementDTO,
    SimulatedImpactLevelDTO,
    UnavailabilitySimulationResponseDTO,
)
from abastecepyme.core.exceptions import ElementNotFoundException
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.graph.dependency_graph import DependencyGraph, MultiSourceVisit
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository


class SimulateUnavailabilityUseCase:
    def __init__(
        self,
        element_repository: ElementRepository,
        dependency_repository: DependencyRepository,
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self, element_ids: List[UUID]) -> UnavailabilitySimulationResponseDTO:
        graph = DependencyGraph.build(
            self.element_repository.get_all(active_only=True),
            self.dependency_repository.get_all(),
        )

        for element_id in element_ids:
            if not graph.has_node(element_id):
                raise ElementNotFoundException(str(element_id))

        visits = graph.reach_many(element_ids, reverse=True)
        source_ids = set(element_ids)
        visit_by_id = {visit.node_id: visit for visit in visits}
        source_dtos = [self._element_dto(graph, source_id) for source_id in element_ids]
        reached = [
            self._describe_visit(graph, source_ids, visit_by_id, visit)
            for visit in visits
        ]
        level_groups: Dict[int, List[SimulatedImpactElementDTO]] = {}
        for item in reached:
            level_groups.setdefault(item.level, []).append(item)

        products = [
            element for element in graph.nodes
            if element.element_type == ElementType.PRODUCTO
        ]
        stopped_ids = {
            item.id
            for item in source_dtos
            if item.element_type == ElementType.PRODUCTO
        }
        stopped_ids.update(
            item.id for item in reached if item.element_type == ElementType.PRODUCTO
        )
        stopped_products = [
            self._element_dto(graph, element.id)
            for element in products
            if element.id in stopped_ids
        ]
        available_products = [
            self._element_dto(graph, element.id)
            for element in products
            if element.id not in stopped_ids
        ]
        source_names = ", ".join(element.name for element in source_dtos)
        affected_count = len(reached)
        stopped_count = len(stopped_products)
        available_count = len(available_products)

        return UnavailabilitySimulationResponseDTO(
            sources=source_dtos,
            affected_count=affected_count,
            max_level=max((visit.level for visit in visits), default=0),
            levels=[
                SimulatedImpactLevelDTO(level=level, elements=items)
                for level, items in level_groups.items()
            ],
            stopped_products=stopped_products,
            available_products=available_products,
            summary=(
                f"Si no están disponibles {source_names}, se afectan "
                f"{affected_count} {_count(affected_count, 'elemento', 'elementos')}. "
                f"Se detienen {stopped_count} {_count(stopped_count, 'producto', 'productos')} "
                f"y pueden seguir produciéndose "
                f"{available_count} {_count(available_count, 'producto', 'productos')}."
            ),
        )

    @staticmethod
    def _element_dto(graph: DependencyGraph, element_id: UUID) -> ElementResponseDTO:
        element = graph.get_node(element_id)
        return ElementResponseDTO(
            id=element.id,
            name=element.name,
            element_type=element.element_type,
            is_active=element.is_active,
        )

    @staticmethod
    def _describe_visit(
        graph: DependencyGraph,
        source_ids: set[UUID],
        visit_by_id: Dict[UUID, MultiSourceVisit],
        visit: MultiSourceVisit,
    ) -> SimulatedImpactElementDTO:
        path_ids = [visit.node_id]
        while path_ids[-1] not in source_ids:
            path_ids.append(visit_by_id[path_ids[-1]].via_id)
        path = [graph.get_node(node_id).name for node_id in reversed(path_ids)]
        element = graph.get_node(visit.node_id)
        return SimulatedImpactElementDTO(
            id=element.id,
            name=element.name,
            element_type=element.element_type,
            level=visit.level,
            via_id=visit.via_id,
            source_id=visit.source_id,
            path=path,
        )


def _count(count: int, singular: str, plural: str) -> str:
    return singular if count == 1 else plural
