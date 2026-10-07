from abastecepyme.domain.graph.dependency_graph import DependencyGraph
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.application.dtos.graph_dto import GraphEdgeDTO, GraphResponseDTO

class GetDependencyGraphUseCase:
    def __init__(
        self,
        element_repository: ElementRepository,
        dependency_repository: DependencyRepository
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self) -> GraphResponseDTO:
        graph = DependencyGraph.build(
            self.element_repository.get_all(active_only=True),
            self.dependency_repository.get_all()
        )

        nodes = [
            ElementResponseDTO(
                id=e.id,
                name=e.name,
                element_type=e.element_type,
                is_active=e.is_active
            ) for e in graph.nodes
        ]

        edges = []
        for requiring_id, required_id in graph.edges:
            requiring = graph.get_node(requiring_id)
            required = graph.get_node(required_id)
            edges.append(
                GraphEdgeDTO(
                    requiring_element_id=requiring_id,
                    required_element_id=required_id,
                    description=f"Para producir {requiring.name} necesito {required.name}"
                )
            )

        return GraphResponseDTO(nodes=nodes, edges=edges)