"""
Pruebas del reporte de ciclos (Feature 3) sobre el grafo propio, sin base de datos.

Una arista A -> B se lee "para producir A necesito B". Un ciclo se informa como un camino
cerrado en ese mismo sentido: [A, B, A] = "A necesita B y B necesita A".
"""
import random
from uuid import uuid4

from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.graph.dependency_graph import DependencyGraph


# ---------- Ayudas ----------
def el(name, element_type=ElementType.PRODUCTO):
    return Element(id=uuid4(), name=name, element_type=element_type)


def build(elements, pairs):
    return DependencyGraph.build(
        elements,
        [Dependency(requiring_element_id=a.id, required_element_id=b.id) for a, b in pairs],
    )


def names(graph, ids):
    return [graph.get_node(i).name for i in ids]


def cycle_names(graph, result):
    """Los ciclos del resultado, como listas de nombres (camino cerrado: el primero se repite al final)."""
    return [names(graph, cycle) for cycle in result.cycles]


def stage_names(graph, result):
    return [names(graph, stage) for stage in result.stages]


# ---------- Casos concretos ----------
def test_el_ciclo_se_reporta_con_su_camino_exacto():
    pan, masa = el("Pan"), el("Masa madre")
    g = build([pan, masa], [(pan, masa), (masa, pan)])

    result = g.preparation_order()

    # Empieza por el primer elemento en orden estable (por nombre) y vuelve a él.
    assert cycle_names(g, result) == [["Masa madre", "Pan", "Masa madre"]]
    assert names(g, result.in_cycle) == ["Masa madre", "Pan"]
    assert result.blocked_by_cycle == []


def test_quien_solo_depende_del_ciclo_se_separa_de_quienes_lo_forman():
    molino = el("Molinos SA", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    masa, pan = el("Masa madre"), el("Pan")
    croissant, combo = el("Croissant"), el("Combo")
    g = build(
        [molino, harina, masa, pan, croissant, combo],
        [(harina, molino), (masa, harina), (masa, pan), (pan, masa), (croissant, masa), (combo, croissant)],
    )

    result = g.preparation_order()

    assert names(g, result.in_cycle) == ["Masa madre", "Pan"]
    assert names(g, result.blocked_by_cycle) == ["Combo", "Croissant"]  # bloqueados, pero no son el ciclo
    assert names(g, result.blocked) == ["Combo", "Croissant", "Masa madre", "Pan"]
    assert stage_names(g, result) == [["Molinos SA"], ["Harina"]]


def test_el_camino_del_ciclo_sigue_el_sentido_de_las_aristas():
    # A necesita B, B necesita C, C necesita A: "A -> B -> C -> A".
    a, b, c = el("A"), el("B"), el("C")
    g = build([c, a, b], [(a, b), (b, c), (c, a)])

    result = g.preparation_order()

    assert cycle_names(g, result) == [["A", "B", "C", "A"]]
    path = result.cycles[0]
    assert all(g.has_edge(path[i], path[i + 1]) for i in range(len(path) - 1))


def test_dos_ciclos_independientes_se_reportan_por_separado():
    a, b, c, d = el("A"), el("B"), el("C"), el("D")
    g = build([a, b, c, d], [(a, b), (b, a), (c, d), (d, c)])

    result = g.preparation_order()

    assert cycle_names(g, result) == [["A", "B", "A"], ["C", "D", "C"]]
    assert names(g, result.in_cycle) == ["A", "B", "C", "D"]


def test_se_reporta_el_ciclo_mas_corto_aunque_el_grupo_tenga_mas_elementos():
    # A <-> B y además A -> C -> D -> A: todos se necesitan entre sí; se informa el más corto.
    a, b, c, d = el("A"), el("B"), el("C"), el("D")
    g = build([a, b, c, d], [(a, b), (b, a), (a, c), (c, d), (d, a)])

    result = g.preparation_order()

    assert cycle_names(g, result) == [["A", "B", "A"]]
    assert names(g, result.in_cycle) == ["A", "B", "C", "D"]  # C y D también están en un ciclo
    assert result.blocked_by_cycle == []


def test_sin_ciclos_no_se_reporta_ninguno():
    a, b = el("A"), el("B")
    g = build([a, b], [(b, a)])

    result = g.preparation_order()

    assert result.is_valid
    assert result.cycles == []
    assert result.in_cycle == []
    assert result.blocked_by_cycle == []


def test_un_elemento_que_se_requiere_a_si_mismo_es_un_ciclo():
    # La API lo rechaza al registrar, pero el grafo no debe asumirlo.
    a = el("A")
    g = build([a], [(a, a)])

    result = g.preparation_order()

    assert cycle_names(g, result) == [["A", "A"]]


def test_el_reporte_del_ciclo_no_depende_del_orden_de_registro():
    names_ = ["A", "B", "C", "D", "E"]
    pairs_by_name = [("A", "B"), ("B", "C"), ("C", "A"), ("D", "C"), ("E", "D")]

    reports = []
    for seed in range(5):
        rng = random.Random(seed)
        elements = {n: el(n) for n in names_}
        order = list(names_)
        rng.shuffle(order)
        pairs = list(pairs_by_name)
        rng.shuffle(pairs)
        g = build([elements[n] for n in order], [(elements[a], elements[b]) for a, b in pairs])
        result = g.preparation_order()
        reports.append((cycle_names(g, result), names(g, result.in_cycle), names(g, result.blocked_by_cycle)))

    assert all(r == reports[0] for r in reports)
    assert reports[0] == ([["A", "B", "C", "A"]], ["A", "B", "C"], ["D", "E"])


# ---------- Prueba de propiedad ----------
def test_en_grafos_aleatorios_el_reporte_de_ciclos_es_correcto():
    # 80 grafos con aristas al azar (con y sin ciclos). Un elemento está en un ciclo
    # si y solo si puede alcanzarse a sí mismo siguiendo requisitos.
    for seed in range(80):
        rng = random.Random(seed)
        n = rng.randint(2, 14)
        elements = [el(f"E{i:02d}") for i in range(n)]
        pairs = {(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(1, 2 * n))}
        pairs = {(a, b) for a, b in pairs if a != b}
        g = build(elements, [(elements[a], elements[b]) for a, b in pairs])

        result = g.preparation_order()

        truly_in_cycle = {
            e.id for e in elements if any(g.has_path(r, e.id) for r in g.requirements_of(e.id))
        }
        assert set(result.in_cycle) == truly_in_cycle
        assert set(result.blocked) >= truly_in_cycle
        assert result.is_valid == (not truly_in_cycle)
        for cycle in result.cycles:
            assert cycle[0] == cycle[-1] and len(cycle) >= 2
            assert len(set(cycle[:-1])) == len(cycle) - 1  # sin repetir elementos dentro del ciclo
            assert all(g.has_edge(cycle[i], cycle[i + 1]) for i in range(len(cycle) - 1))
        # Lo bloqueado que no es del ciclo realmente depende (directa o indirectamente) de uno
        for node_id in result.blocked_by_cycle:
            assert any(g.has_path(node_id, member) for member in result.in_cycle)
