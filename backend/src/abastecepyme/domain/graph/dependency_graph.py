from collections import deque
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Set, Tuple
from uuid import UUID

from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.enums.element_type import ElementType


@dataclass(frozen=True)
class Visit:
    """Un elemento alcanzado por un recorrido."""

    node_id: UUID
    level: int    # cantidad de aristas desde el origen (1 = vecino directo)
    via_id: UUID  # elemento desde el cual se llegó a este (su "padre" en el recorrido)


@dataclass(frozen=True)
class OrderingResult:
    """Resultado de ordenar el grafo según sus requisitos."""

    # Etapas en orden de preparación. Los elementos de una misma etapa no dependen entre sí.
    stages: List[List[UUID]]
    # Elementos que no se pudieron ordenar: los del ciclo y los que dependen de él.
    blocked: List[UUID]
    # Un ciclo representativo por cada grupo de elementos que se necesitan entre sí.
    # Cada ciclo es un camino cerrado en el sentido de las aristas: [A, B, A] = "A necesita B y B necesita A".
    cycles: List[List[UUID]] = field(default_factory=list)
    # Todos los elementos que forman parte de algún ciclo (no solo los del ciclo representativo).
    in_cycle: List[UUID] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """True si todos los elementos quedaron ordenados (no hay contradicciones)."""
        return not self.blocked

    @property
    def blocked_by_cycle(self) -> List[UUID]:
        """Elementos bloqueados que NO forman parte de un ciclo: solo dependen de uno."""
        members = set(self.in_cycle)
        return [node_id for node_id in self.blocked if node_id not in members]

    @property
    def cycle(self) -> List[UUID]:
        """Un ciclo concreto como camino cerrado (el primero de `cycles`); vacío si no hay ciclos."""
        return self.cycles[0] if self.cycles else []


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

    @property
    def adjacency(self) -> Dict[UUID, List[UUID]]:
        """Copy of each node's adjacency list (outgoing edges)."""
        return {node_id: list(required_ids) for node_id, required_ids in self._requires.items()}

    # ---------- Consultas ----------
    def requirements_of(self, node_id: UUID) -> List[UUID]:
        """Nodos que `node_id` requiere directamente."""
        return list(self._requires.get(node_id, []))

    def dependents_of(self, node_id: UUID) -> List[UUID]:
        """Nodos que requieren directamente a `node_id`."""
        return list(self._required_by.get(node_id, []))

    def reach(self, source: UUID, *, reverse: bool = False) -> List[Visit]:
        """
        Recorrido en anchura (BFS) propio desde `source`.

        - reverse=False: sigue las aristas tal como están (A -> B: "A requiere B"),
          o sea, recorre lo que `source` necesita.
        - reverse=True: sigue las aristas al revés, o sea, recorre quienes dependen de
          `source` (impacto de una falla). Usa el índice `_required_by`, sin condicionales.

        Devuelve los elementos alcanzados, sin incluir `source`, en orden de visita:
        primero los de nivel 1, luego los de nivel 2, etc. Cada elemento aparece una vez,
        con su nivel mínimo. El conjunto `visited` evita repetir elementos y garantiza que
        termina aunque existan ciclos. Costo: O(V + E).
        """
        if source not in self._nodes:
            raise ValueError("El elemento de origen no está en el grafo.")

        index = self._required_by if reverse else self._requires
        visited = {source}
        queue = deque([(source, 0)])
        result: List[Visit] = []

        while queue:
            current, level = queue.popleft()
            for neighbour in index[current]:
                if neighbour in visited:
                    continue
                visited.add(neighbour)
                result.append(Visit(node_id=neighbour, level=level + 1, via_id=current))
                queue.append((neighbour, level + 1))

        return result

    def reachable_from(self, node_id: UUID, reverse: bool = False) -> List[UUID]:
        """Devuelve, en orden de proximidad, los nodos alcanzables desde `node_id`."""
        return [visit.node_id for visit in self.reach(node_id, reverse=reverse)]

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

    def preparation_order(self) -> OrderingResult:
        """
        Orden de preparación: ordenamiento topológico propio (algoritmo de Kahn por etapas).

        Una arista A -> B significa "para producir A necesito B", así que B debe estar
        listo antes que A. Se lleva la cuenta de los requisitos pendientes de cada
        elemento. En cada etapa se toman los elementos sin requisitos pendientes
        (proveedores, insumos sin proveedor y elementos aislados en la primera) y, al
        prepararlos, se descuenta un requisito pendiente a quienes los necesitan
        (índice `_required_by`). Los que llegan a cero forman la etapa siguiente.

        Si al terminar quedan elementos con requisitos pendientes, hay un ciclo: esos
        elementos se devuelven en `blocked` y NO se inventa un orden para ellos. Para
        explicar la contradicción se separan los que forman parte de un ciclo de los
        que solo dependen de uno, y se reconstruye un ciclo concreto (`cycles`).

        Dentro de cada etapa los elementos se ordenan por tipo y nombre, para que el
        resultado sea siempre el mismo sin importar el orden en que se registraron.
        Costo: O(V + E) del recorrido, más O(V log V) de ordenar las etapas.
        """
        pending = {node_id: len(required) for node_id, required in self._requires.items()}
        ready = [node_id for node_id, count in pending.items() if count == 0]

        stages: List[List[UUID]] = []
        while ready:
            ready.sort(key=self._display_key)
            stages.append(ready)

            next_ready: List[UUID] = []
            for node_id in ready:
                for dependent_id in self._required_by[node_id]:
                    pending[dependent_id] -= 1
                    if pending[dependent_id] == 0:
                        next_ready.append(dependent_id)
            ready = next_ready

        blocked = sorted((n for n, count in pending.items() if count > 0), key=self._display_key)
        cycles, in_cycle = self._find_cycles(set(blocked)) if blocked else ([], [])
        if blocked and not cycles:
            raise RuntimeError("No se pudo reconstruir el ciclo que bloquea el orden.")
        return OrderingResult(stages=stages, blocked=blocked, cycles=cycles, in_cycle=in_cycle)

    # ---------- Ciclos ----------
    def _find_cycles(self, blocked: Set[UUID]) -> Tuple[List[List[UUID]], List[UUID]]:
        """
        Explica por qué `blocked` no se pudo ordenar.

        Todo elemento bloqueado tiene al menos un requisito también bloqueado, así que
        dentro de `blocked` siempre hay ciclos. Se buscan los grupos de elementos que se
        necesitan entre sí (componentes fuertemente conexos, algoritmo de Tarjan) y, por
        cada grupo, se reconstruye el ciclo más corto que pasa por su primer elemento.
        Los elementos bloqueados que quedan fuera de todo grupo solo dependen de un ciclo.
        Costo: O(V + E) para los grupos y O(V + E) por cada ciclo reconstruido.
        """
        cycles: List[List[UUID]] = []
        in_cycle: List[UUID] = []
        for group in self._strongly_connected_groups(blocked):
            # Un grupo de un solo elemento es un ciclo únicamente si se requiere a sí mismo.
            if len(group) == 1 and group[0] not in self._requires[group[0]]:
                continue
            members = set(group)
            start = min(group, key=self._display_key)
            cycles.append(self._shortest_cycle_through(start, members))
            in_cycle.extend(group)
        cycles.sort(key=lambda cycle: self._display_key(cycle[0]))
        in_cycle.sort(key=self._display_key)
        return cycles, in_cycle

    def _neighbours_within(self, node_id: UUID, allowed: Set[UUID]) -> List[UUID]:
        """Requisitos directos de `node_id` que están en `allowed`, en orden estable."""
        return sorted((n for n in self._requires[node_id] if n in allowed), key=self._display_key)

    def _strongly_connected_groups(self, nodes: Set[UUID]) -> List[List[UUID]]:
        """Algoritmo de Tarjan, iterativo (sin recursión), sobre el subgrafo formado por `nodes`."""
        number: Dict[UUID, int] = {}
        low: Dict[UUID, int] = {}
        on_stack: Set[UUID] = set()
        stack: List[UUID] = []
        groups: List[List[UUID]] = []
        counter = 0

        for root in sorted(nodes, key=self._display_key):
            if root in number:
                continue
            number[root] = low[root] = counter
            counter += 1
            stack.append(root)
            on_stack.add(root)
            work = [(root, iter(self._neighbours_within(root, nodes)))]

            while work:
                node, neighbours = work[-1]
                descended = False
                for neighbour in neighbours:
                    if neighbour not in number:
                        number[neighbour] = low[neighbour] = counter
                        counter += 1
                        stack.append(neighbour)
                        on_stack.add(neighbour)
                        work.append((neighbour, iter(self._neighbours_within(neighbour, nodes))))
                        descended = True
                        break
                    if neighbour in on_stack:
                        low[node] = min(low[node], number[neighbour])
                if descended:
                    continue

                work.pop()
                if work:
                    parent = work[-1][0]
                    low[parent] = min(low[parent], low[node])
                if low[node] == number[node]:
                    group: List[UUID] = []
                    while True:
                        member = stack.pop()
                        on_stack.discard(member)
                        group.append(member)
                        if member == node:
                            break
                    groups.append(group)
        return groups

    def _shortest_cycle_through(self, start: UUID, members: Set[UUID]) -> List[UUID]:
        """
        Ciclo más corto que pasa por `start`, como camino cerrado [start, ..., start]
        en el sentido de las aristas. Recorrido en anchura dentro de `members`.
        """
        parent: Dict[UUID, UUID] = {}
        queue = deque()
        for neighbour in self._neighbours_within(start, members):
            parent[neighbour] = start
            queue.append(neighbour)

        while queue:
            current = queue.popleft()
            if current == start:
                break
            for neighbour in self._neighbours_within(current, members):
                if neighbour not in parent:
                    parent[neighbour] = current
                    queue.append(neighbour)

        middle: List[UUID] = []
        node = parent[start]
        while node != start:
            middle.append(node)
            node = parent[node]
        middle.reverse()
        return [start, *middle, start]

    def _display_key(self, node_id: UUID) -> Tuple[int, str]:
        """Clave de orden estable: primero por tipo (proveedor, insumo, producto) y luego por nombre."""
        element = self._nodes[node_id]
        return list(ElementType).index(element.element_type), element.name.casefold()

    def would_create_cycle(self, requiring_id: UUID, required_id: UUID) -> bool:
        """
        Agregar requiring -> required cierra un ciclo si ya existe un camino
        required -> ... -> requiring (o si ambos son el mismo nodo).
        """
        return self.has_path(required_id, requiring_id)