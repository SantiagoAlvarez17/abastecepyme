from typing import List

from abastecepyme.application.dtos.dashboard_dto import (
    CriticalPointDTO,
    DashboardSummaryDTO,
    ProductionStatusDTO,
)
from abastecepyme.application.dtos.element_dto import ElementRefDTO
from abastecepyme.application.use_cases.graph_descriptions import describe_cycle, describe_element
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.graph.dependency_graph import DependencyGraph
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository

# Elements that can "fail" upstream: a supplier that does not deliver or an input that runs out.
_FAILURE_CANDIDATES = (ElementType.PROVEEDOR, ElementType.INSUMO)


class GetDashboardSummaryUseCase:
    """
    One-call overview for the supply dashboard (Feature 4). It integrates the three
    previous features over the same graph instance:

    - catalog (F1): totals by type and isolated elements;
    - impact (F2): critical points, ranked by how many products a failure would stop;
    - production order (F3): whether a valid order exists or which cycle prevents it.

    Cost: O(V + E) for the order, plus one reverse BFS per supplier/input,
    O(K · (V + E)) with K = suppliers + inputs.
    """

    def __init__(
        self,
        element_repository: ElementRepository,
        dependency_repository: DependencyRepository,
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self, limit: int = 5) -> DashboardSummaryDTO:
        graph = DependencyGraph.build(
            self.element_repository.get_all(active_only=True),
            self.dependency_repository.get_all(),
        )

        by_type = {element_type.value: 0 for element_type in ElementType}
        for node in graph.nodes:
            by_type[node.element_type.value] += 1

        isolated_ids = sorted(
            (node.id for node in graph.nodes if graph.is_isolated(node.id)),
            key=graph.display_key,
        )

        return DashboardSummaryDTO(
            total_elements=len(graph.nodes),
            total_dependencies=len(graph.edges),
            by_type=by_type,
            isolated=[ElementRefDTO(**describe_element(graph, node_id)) for node_id in isolated_ids],
            production=self._production_status(graph),
            critical_points=self._critical_points(graph)[:limit],
        )

    @staticmethod
    def _production_status(graph: DependencyGraph) -> ProductionStatusDTO:
        if not graph.nodes:
            return ProductionStatusDTO(
                status="empty",
                message="El catálogo está vacío: todavía no hay nada que producir.",
                stage_count=0,
                blocked_count=0,
                cycles=[],
            )

        ordering = graph.preparation_order()
        if ordering.is_valid:
            stages = len(ordering.stages)
            return ProductionStatusDTO(
                status="valid",
                message=f"Existe un orden de preparación válido en {stages} {'etapa' if stages == 1 else 'etapas'}.",
                stage_count=stages,
                blocked_count=0,
                cycles=[],
            )

        cycles = [describe_cycle(graph, cycle) for cycle in ordering.cycles]
        return ProductionStatusDTO(
            status="cycle",
            message=(
                f"Ciclo detectado: {cycles[0]['text']}. Las dependencias se contradicen y no existe "
                f"un orden de preparación válido; {len(ordering.blocked)} elementos quedan sin orden."
            ),
            stage_count=0,
            blocked_count=len(ordering.blocked),
            cycles=cycles,
        )

    @staticmethod
    def _critical_points(graph: DependencyGraph) -> List[CriticalPointDTO]:
        """
        Every supplier or input whose failure reaches at least one element, ranked by
        affected products, then by affected elements, then by type and name (stable).
        Reuses the F2 traversal: `reach(..., reverse=True)` walks towards the dependents.
        """
        points: List[CriticalPointDTO] = []
        for node in graph.nodes:
            if node.element_type not in _FAILURE_CANDIDATES:
                continue
            visits = graph.reach(node.id, reverse=True)
            if not visits:
                continue
            products = sorted(
                (
                    graph.get_node(visit.node_id).name
                    for visit in visits
                    if graph.get_node(visit.node_id).element_type == ElementType.PRODUCTO
                ),
                key=str.casefold,
            )
            points.append(
                CriticalPointDTO(
                    **describe_element(graph, node.id),
                    affected_products=len(products),
                    affected_total=len(visits),
                    products=products,
                )
            )

        def rank(point: CriticalPointDTO) -> tuple:
            return (-point.affected_products, -point.affected_total, graph.display_key(point.id))

        return sorted(points, key=rank)
