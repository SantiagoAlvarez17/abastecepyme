"""
Plain descriptions of graph nodes and cycles, shared by the use cases that report them
(production order and dashboard summary), so both endpoints describe them identically.
"""
from typing import List
from uuid import UUID

from abastecepyme.domain.graph.dependency_graph import DependencyGraph


def describe_element(graph: DependencyGraph, node_id: UUID) -> dict:
    node = graph.get_node(node_id)
    return {"id": str(node.id), "name": node.name, "element_type": node.element_type.value}


def describe_cycle(graph: DependencyGraph, cycle: List[UUID]) -> dict:
    """A cycle as a closed walk ([A, B, A]) plus its readable text ("A → B → A")."""
    elements = [describe_element(graph, node_id) for node_id in cycle]
    return {"elements": elements, "text": " → ".join(e["name"] for e in elements)}
