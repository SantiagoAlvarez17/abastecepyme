from typing import Dict, Iterable, List, Tuple
from uuid import UUID

from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element


class DependencyGraph:
    """
    Grafo dirigido propio, implementado con listas de adyacencia (sin librerías externas).

    Una arista A -> B se lee: "para producir A necesito B".

    Se mantienen dos índices:
      - _requires:    nodo -> lista de nodos que ese nodo requiere (aristas salientes)
      - _required_by: nodo -> lista de nodos que lo requieren (aristas entrantes)
    El segundo permite recorrer el grafo "al revés" (análisis de impacto de un
    proveedor) sin tener que recalcular nada.
    """

    def __init__(self) -> None:
        self._nodes: Dict[UUID, Element] = {}
        self._requires: Dict[UUID, List[UUID]] = {}
        self._required_by: Dict[UUID, List[UUID]] = {}

    @classmethod
    def build(
        cls, elements: Iterable[Element], dependencies: Iterable[Dependency]
    ) -> "DependencyGraph":
        graph = cls()
        for element in elements:
            graph.add_node(element)
        for dependency in dependencies:
            # Se ignoran aristas cuyo extremo no está en el grafo (p. ej. elementos inactivos)
            if graph.has_node(dependency.requiring_element_id) and graph.has_node(
                dependency.required_element_id
            ):
                graph.add_edge(dependency.requiring_element_id, dependency.required_element_id)
        return graph

    # ---------- Nodos ----------
    def add_node(self, element: Element) -> None:
        if element.id in self._nodes:
            return
        self._nodes[element.id] = element
        self._requires[element.id] = []
        self._required_by[element.id] = []

    def has_node(self, node_id: UUID) -> bool:
        return node_id in self._nodes

    def get_node(self, node_id: UUID) -> Element:
        return self._nodes[node_id]

    @property
    def nodes(self) -> List[Element]:
        return list(self._nodes.values())

    # ---------- Aristas ----------
    def add_edge(self, requiring_id: UUID, required_id: UUID) -> bool:
        """Agrega la arista requiring -> required. Devuelve False si ya existía."""
        if requiring_id not in self._nodes or required_id not in self._nodes:
            raise ValueError("Ambos extremos de la arista deben existir como nodos del grafo.")
        if self.has_edge(requiring_id, required_id):
            return False
        self._requires[requiring_id].append(required_id)
        self._required_by[required_id].append(requiring_id)
        return True

    def has_edge(self, requiring_id: UUID, required_id: UUID) -> bool:
        return required_id in self._requires.get(requiring_id, [])

    @property
    def edges(self) -> List[Tuple[UUID, UUID]]:
        return [
            (requiring_id, required_id)
            for requiring_id, required_ids in self._requires.items()
            for required_id in required_ids
        ]

    # ---------- Consultas ----------
    def requirements_of(self, node_id: UUID) -> List[UUID]:
        """Nodos que `node_id` requiere directamente."""
        return list(self._requires.get(node_id, []))

    def dependents_of(self, node_id: UUID) -> List[UUID]:
        """Nodos que requieren directamente a `node_id`."""
        return list(self._required_by.get(node_id, []))

    def has_path(self, source: UUID, target: UUID) -> bool:
        """Búsqueda en profundidad iterativa siguiendo la dirección de las aristas."""
        if source == target:
            return True
        visited = {source}
        stack = [source]
        while stack:
            current = stack.pop()
            for neighbour in self._requires.get(current, []):
                if neighbour == target:
                    return True
                if neighbour not in visited:
                    visited.add(neighbour)
                    stack.append(neighbour)
        return False

    def would_create_cycle(self, requiring_id: UUID, required_id: UUID) -> bool:
        """
        Agregar requiring -> required cierra un ciclo si ya existe un camino
        required -> ... -> requiring (o si ambos son el mismo nodo).
        """
        return self.has_path(required_id, requiring_id)