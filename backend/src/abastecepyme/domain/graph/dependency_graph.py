from typing import Dict, List, Tuple
from uuid import UUID

class DependencyGraph:
    """
    Grafo dirigido propio representado con lista de adyacencia.
    Arista A -> B significa: "Para producir A necesito B".

    Se usa lista de adyacencia porque el grafo es disperso (cada elemento
    depende de pocos otros) y los recorridos de F2/F3 necesitan iterar los
    vecinos de un nodo: O(V + E) en memoria y O(grado) por consulta de vecinos.
    """

    def __init__(self):
        self._adjacency: Dict[UUID, List[UUID]] = {}

    def add_node(self, node_id: UUID) -> None:
        if node_id not in self._adjacency:
            self._adjacency[node_id] = []

    def add_edge(self, requiring_id: UUID, required_id: UUID) -> None:
        if requiring_id not in self._adjacency or required_id not in self._adjacency:
            raise ValueError("Ambos extremos de la arista deben existir en el grafo.")
        if required_id not in self._adjacency[requiring_id]:
            self._adjacency[requiring_id].append(required_id)

    def has_node(self, node_id: UUID) -> bool:
        return node_id in self._adjacency

    def has_edge(self, requiring_id: UUID, required_id: UUID) -> bool:
        return required_id in self._adjacency.get(requiring_id, [])

    def nodes(self) -> List[UUID]:
        return list(self._adjacency.keys())

    def successors(self, node_id: UUID) -> List[UUID]:
        """Elementos que 'node_id' necesita directamente."""
        return list(self._adjacency.get(node_id, []))

    def edges(self) -> List[Tuple[UUID, UUID]]:
        return [(origin, target) for origin, targets in self._adjacency.items() for target in targets]

    def adjacency(self) -> Dict[UUID, List[UUID]]:
        return {node: list(targets) for node, targets in self._adjacency.items()}
