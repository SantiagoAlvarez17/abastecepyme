from abastecepyme.domain.graph.dependency_graph import DependencyGraph
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.application.dtos.dependency_dto import DependencyResponseDTO
from abastecepyme.application.dtos.graph_dto import GraphResponseDTO

class GetGraphUseCase:
    """Construye el grafo propio a partir de lo persistido y lo expone."""

    def __init__(
        self,
        element_repository: ElementRepository,
        dependency_repository: DependencyRepository
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def build_graph(self) -> DependencyGraph:
        graph = DependencyGraph()
        for element in self.element_repository.get_all(active_only=True):
            graph.add_node(element.id)
        for dep in self.dependency_repository.get_all():
            # Aristas hacia elementos inactivos no forman parte de la red visible
            if graph.has_node(dep.requiring_element_id) and graph.has_node(dep.required_element_id):
                graph.add_edge(dep.requiring_element_id, dep.required_element_id)
        return graph

    def execute(self) -> GraphResponseDTO:
        elements = self.element_repository.get_all(active_only=True)
        graph = self.build_graph()
        return GraphResponseDTO(
            direction="A -> B: Para producir A necesito B",
            nodes=[
                ElementResponseDTO(
                    id=e.id,
                    name=e.name,
                    element_type=e.element_type,
                    is_active=e.is_active
                ) for e in elements
            ],
            edges=[
                DependencyResponseDTO(requiring_element_id=a, required_element_id=b)
                for a, b in graph.edges()
            ],
            adjacency=graph.adjacency()
        )
