"""Pruebas del grafo propio DependencyGraph (estructura y consultas, sin base de datos)."""
from uuid import uuid4

import pytest

from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.graph.dependency_graph import DependencyGraph


def el(name, element_type=ElementType.PRODUCTO):
    return Element(id=uuid4(), name=name, element_type=element_type)


def dep(requiring, required):
    return Dependency(requiring_element_id=requiring.id, required_element_id=required.id)


def test_build_crea_nodos_y_aristas():
    proveedor = el("Molinos", ElementType.PROVEEDOR)
    insumo = el("Harina", ElementType.INSUMO)
    producto = el("Pan")

    graph = DependencyGraph.build(
        [proveedor, insumo, producto], [dep(insumo, proveedor), dep(producto, insumo)]
    )

    assert len(graph.nodes) == 3
    assert set(graph.edges) == {(insumo.id, proveedor.id), (producto.id, insumo.id)}


def test_requisitos_y_dependientes():
    proveedor = el("Molinos", ElementType.PROVEEDOR)
    insumo = el("Harina", ElementType.INSUMO)
    producto = el("Pan")
    graph = DependencyGraph.build(
        [proveedor, insumo, producto], [dep(insumo, proveedor), dep(producto, insumo)]
    )

    assert graph.requirements_of(producto.id) == [insumo.id]
    assert graph.dependents_of(proveedor.id) == [insumo.id]
    assert graph.requirements_of(proveedor.id) == []
    assert graph.dependents_of(producto.id) == []


def test_build_ignora_aristas_con_extremos_ausentes():
    insumo = el("Harina", ElementType.INSUMO)
    fantasma = el("Inactivo", ElementType.PROVEEDOR)

    graph = DependencyGraph.build([insumo], [dep(insumo, fantasma)])

    assert graph.edges == []


def test_add_edge_repetida_devuelve_false():
    a, b = el("A"), el("B")
    graph = DependencyGraph.build([a, b], [])

    assert graph.add_edge(a.id, b.id) is True
    assert graph.add_edge(a.id, b.id) is False
    assert graph.edges == [(a.id, b.id)]


def test_add_edge_con_nodo_inexistente_falla():
    a = el("A")
    graph = DependencyGraph.build([a], [])

    with pytest.raises(ValueError):
        graph.add_edge(a.id, uuid4())


def test_has_path_directo_e_indirecto():
    a, b, c, d = el("A"), el("B"), el("C"), el("D")
    graph = DependencyGraph.build([a, b, c, d], [dep(a, b), dep(b, c)])

    assert graph.has_path(a.id, c.id) is True
    assert graph.has_path(c.id, a.id) is False  # la dirección importa
    assert graph.has_path(a.id, d.id) is False  # nodo aislado
    assert graph.has_path(a.id, a.id) is True


def test_would_create_cycle():
    a, b, c = el("A"), el("B"), el("C")
    graph = DependencyGraph.build([a, b, c], [dep(a, b), dep(b, c)])

    assert graph.would_create_cycle(c.id, a.id) is True   # cierra A->B->C->A
    assert graph.would_create_cycle(b.id, a.id) is True   # cierra A->B->A
    assert graph.would_create_cycle(a.id, c.id) is False  # atajo A->C, sin ciclo
    assert graph.would_create_cycle(a.id, a.id) is True   # autociclo


def test_recorrido_no_se_cuelga_con_ciclos_existentes():
    a, b = el("A"), el("B")
    graph = DependencyGraph.build([a, b], [dep(a, b), dep(b, a)])

    assert graph.has_path(a.id, el("Otro").id) is False