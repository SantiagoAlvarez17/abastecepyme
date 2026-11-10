"""
Pruebas de la Feature 3 (orden de preparación) sobre el grafo propio, sin base de datos.

Una arista A -> B se lee "para producir A necesito B", así que B debe prepararse antes que A.
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


def dep(requiring, required):
    return Dependency(requiring_element_id=requiring.id, required_element_id=required.id)


def stage_names(graph, result):
    """Las etapas del resultado, como listas de nombres."""
    return [[graph.get_node(i).name for i in stage] for stage in result.stages]


def build(elements, pairs):
    return DependencyGraph.build(elements, [dep(a, b) for a, b in pairs])


# ---------- Casos acíclicos ----------
def test_cadena_lineal_se_ordena_de_proveedor_a_producto_final():
    molino = el("Molinos SA", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    masa = el("Masa madre")
    pan = el("Pan")
    g = build([pan, masa, harina, molino], [(harina, molino), (masa, harina), (pan, masa)])

    result = g.preparation_order()

    assert result.is_valid
    assert stage_names(g, result) == [["Molinos SA"], ["Harina"], ["Masa madre"], ["Pan"]]


def test_elementos_independientes_comparten_etapa_y_se_ordenan_por_tipo_y_nombre():
    molino = el("Molinos SA", ElementType.PROVEEDOR)
    empaques = el("Empaques del Norte", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    bolsas = el("Bolsas", ElementType.INSUMO)
    masa = el("Masa madre")
    pan = el("Pan")
    g = build(
        [pan, bolsas, masa, harina, molino, empaques],
        [(harina, molino), (bolsas, empaques), (masa, harina), (pan, masa), (pan, bolsas)],
    )

    result = g.preparation_order()

    # Pan necesita Masa madre y Bolsas: solo queda listo cuando la etapa 3 terminó.
    assert stage_names(g, result) == [
        ["Empaques del Norte", "Molinos SA"],
        ["Bolsas", "Harina"],
        ["Masa madre"],
        ["Pan"],
    ]


def test_un_elemento_con_varios_requisitos_espera_al_ultimo_de_ellos():
    # Combo necesita Pan (profundo) y Panela (superficial): su etapa la fija el más profundo.
    molino = el("Molinos SA", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    pan = el("Pan")
    panela = el("Panela")
    combo = el("Combo")
    g = build(
        [combo, panela, pan, harina, molino],
        [(harina, molino), (pan, harina), (combo, pan), (combo, panela)],
    )

    names = stage_names(g, g.preparation_order())

    assert names.index(["Combo"]) == len(names) - 1
    assert "Panela" in names[0]  # sin requisitos: puede prepararse desde el inicio


def test_elementos_aislados_quedan_en_la_primera_etapa():
    molino = el("Molinos SA", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    panela = el("Panela")
    g = build([harina, panela, molino], [(harina, molino)])

    result = g.preparation_order()

    assert stage_names(g, result)[0] == ["Molinos SA", "Panela"]


def test_grafo_vacio_devuelve_un_orden_vacio_y_valido():
    result = DependencyGraph().preparation_order()

    assert result.stages == []
    assert result.blocked == []
    assert result.is_valid


def test_todos_los_elementos_aparecen_exactamente_una_vez():
    a, b, c, d = el("A"), el("B"), el("C"), el("D")
    g = build([a, b, c, d], [(b, a), (c, a), (d, b), (d, c)])  # diamante

    result = g.preparation_order()
    ordered = [node_id for stage in result.stages for node_id in stage]

    assert sorted(ordered, key=str) == sorted((e.id for e in (a, b, c, d)), key=str)


def test_consultar_el_orden_dos_veces_da_lo_mismo_y_no_altera_el_grafo():
    a, b, c = el("A"), el("B"), el("C")
    g = build([a, b, c], [(b, a), (c, b)])
    edges_before = list(g.edges)

    first = g.preparation_order()
    second = g.preparation_order()

    assert first == second
    assert g.edges == edges_before


def test_el_resultado_no_depende_del_orden_de_registro():
    names = ["Molinos SA", "Harina", "Levadura", "Masa madre", "Pan", "Panela"]
    pairs_by_name = [("Harina", "Molinos SA"), ("Levadura", "Molinos SA"),
                     ("Masa madre", "Harina"), ("Masa madre", "Levadura"), ("Pan", "Masa madre")]
    types = {"Molinos SA": ElementType.PROVEEDOR, "Harina": ElementType.INSUMO, "Levadura": ElementType.INSUMO}

    results = []
    for seed in range(5):
        rng = random.Random(seed)
        elements = {n: el(n, types.get(n, ElementType.PRODUCTO)) for n in names}
        order = list(names)
        rng.shuffle(order)
        pairs = list(pairs_by_name)
        rng.shuffle(pairs)
        g = build([elements[n] for n in order], [(elements[a], elements[b]) for a, b in pairs])
        results.append(stage_names(g, g.preparation_order()))

    assert all(r == results[0] for r in results)


def test_en_un_grafo_aleatorio_ninguna_dependencia_se_prepara_despues_de_quien_la_necesita():
    # Prueba de propiedad: un DAG de 200 elementos con 600 dependencias al azar (semilla fija).
    rng = random.Random(42)
    elements = [el(f"E{i:03d}") for i in range(200)]
    pairs = set()
    while len(pairs) < 600:
        i, j = sorted(rng.sample(range(200), 2))
        pairs.add((j, i))  # el de índice mayor requiere al menor: nunca hay ciclos
    shuffled = list(elements)
    rng.shuffle(shuffled)
    g = build(shuffled, [(elements[a], elements[b]) for a, b in pairs])

    result = g.preparation_order()

    assert result.is_valid
    position = {n: i for i, stage in enumerate(result.stages) for n in stage}
    assert len(position) == 200
    for a, b in pairs:
        assert position[elements[b].id] < position[elements[a].id]


# ---------- Con ciclos: nunca se presenta un orden falso ----------
def test_un_ciclo_deja_bloqueados_a_sus_miembros_y_a_quienes_dependen_de_ellos():
    molino = el("Molinos SA", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    masa = el("Masa madre")
    pan = el("Pan")
    combo = el("Combo")
    # Ciclo Pan <-> Masa madre; Combo depende de Pan.
    g = build(
        [molino, harina, masa, pan, combo],
        [(harina, molino), (masa, harina), (masa, pan), (pan, masa), (combo, pan)],
    )

    result = g.preparation_order()

    assert not result.is_valid
    assert [g.get_node(i).name for i in result.blocked] == ["Combo", "Masa madre", "Pan"]
    cycle_names = [g.get_node(i).name for i in result.cycle]
    assert cycle_names[0] == cycle_names[-1]
    assert set(cycle_names[:-1]) == {"Masa madre", "Pan"}
    assert all(g.has_edge(a, b) for a, b in zip(result.cycle, result.cycle[1:]))
    # Lo que no depende del ciclo sí se ordena.
    assert stage_names(g, result) == [["Molinos SA"], ["Harina"]]


def test_un_ciclo_largo_tambien_se_detecta():
    a, b, c = el("A"), el("B"), el("C")
    g = build([a, b, c], [(a, b), (b, c), (c, a)])

    result = g.preparation_order()

    assert result.stages == []
    assert len(result.blocked) == 3
    assert result.cycle[0] == result.cycle[-1]
    assert all(g.has_edge(a, b) for a, b in zip(result.cycle, result.cycle[1:]))