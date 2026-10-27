"""
Pruebas de la Feature 2: recorrido BFS propio (DependencyGraph.reach) y caso de uso
AnalyzeImpactUseCase, sin base de datos (repositorios en memoria).

Grafo de referencia (A -> B se lee "para producir A necesito B"):

    Molinos SA  <-  Harina  <-  Masa madre  <-  Pan
                                     ^
    Molinos SA  <-  Levadura  <-------+
"""
from uuid import uuid4

import pytest

from abastecepyme.application.use_cases.analyze_impact import AnalyzeImpactUseCase
from abastecepyme.core.exceptions import ElementNotFoundException
from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.enums.impact import ImpactMode, ImpactOutcome
from abastecepyme.domain.graph.dependency_graph import DependencyGraph
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository


# ---------- Ayudas ----------
def el(name, element_type=ElementType.PRODUCTO, is_active=True):
    return Element(id=uuid4(), name=name, element_type=element_type, is_active=is_active)


def dep(requiring, required):
    return Dependency(requiring_element_id=requiring.id, required_element_id=required.id)


class InMemoryElementRepository(ElementRepository):
    def __init__(self, elements):
        self.items = list(elements)

    def save(self, element):
        self.items.append(element)
        return element

    def get_by_id(self, element_id):
        return next((e for e in self.items if e.id == element_id), None)

    def get_by_name(self, name):
        return next((e for e in self.items if e.name.lower() == name.lower()), None)

    def get_all(self, active_only=True):
        return [e for e in self.items if e.is_active or not active_only]


class InMemoryDependencyRepository(DependencyRepository):
    def __init__(self, dependencies):
        self.items = list(dependencies)

    def save(self, dependency):
        self.items.append(dependency)
        return dependency

    def exists(self, requiring_element_id, required_element_id):
        return any(
            d.requiring_element_id == requiring_element_id and d.required_element_id == required_element_id
            for d in self.items
        )

    def get_all(self):
        return list(self.items)

    def get_dependencies_for_element(self, element_id):
        return [d for d in self.items if d.requiring_element_id == element_id]


@pytest.fixture
def cadena():
    """Molinos SA <- Harina, Levadura <- Masa madre <- Pan, más Panela (aislado)."""
    molinos = el("Molinos SA", ElementType.PROVEEDOR)
    harina = el("Harina", ElementType.INSUMO)
    levadura = el("Levadura", ElementType.INSUMO)
    masa = el("Masa madre")
    pan = el("Pan")
    panela = el("Panela")
    deps = [dep(harina, molinos), dep(levadura, molinos), dep(masa, harina), dep(masa, levadura), dep(pan, masa)]
    return {
        "molinos": molinos, "harina": harina, "levadura": levadura,
        "masa": masa, "pan": pan, "panela": panela,
        "elements": [molinos, harina, levadura, masa, pan, panela],
        "deps": deps,
    }


def graph_of(c, extra_deps=()):
    return DependencyGraph.build(c["elements"], c["deps"] + list(extra_deps))


def use_case_of(c, extra_deps=(), elements=None):
    return AnalyzeImpactUseCase(
        InMemoryElementRepository(elements if elements is not None else c["elements"]),
        InMemoryDependencyRepository(c["deps"] + list(extra_deps)),
    )


# ---------- DependencyGraph.reach (BFS propio) ----------
def test_reach_inverso_recorre_quienes_dependen_del_origen_por_niveles(cadena):
    visitas = graph_of(cadena).reach(cadena["molinos"].id, reverse=True)

    niveles = {}
    for v in visitas:
        niveles.setdefault(v.level, set()).add(v.node_id)

    assert niveles == {
        1: {cadena["harina"].id, cadena["levadura"].id},
        2: {cadena["masa"].id},
        3: {cadena["pan"].id},
    }


def test_reach_directo_recorre_lo_que_el_origen_necesita(cadena):
    visitas = graph_of(cadena).reach(cadena["pan"].id)

    assert [v.level for v in visitas] == [1, 2, 2, 3]
    assert visitas[0].node_id == cadena["masa"].id
    assert {v.node_id for v in visitas} == {
        cadena["masa"].id, cadena["harina"].id, cadena["levadura"].id, cadena["molinos"].id
    }


def test_reach_no_incluye_al_origen(cadena):
    visitas = graph_of(cadena).reach(cadena["molinos"].id, reverse=True)
    assert cadena["molinos"].id not in {v.node_id for v in visitas}


def test_reach_via_apunta_al_elemento_desde_el_que_se_llego(cadena):
    por_id = {v.node_id: v for v in graph_of(cadena).reach(cadena["molinos"].id, reverse=True)}

    assert por_id[cadena["harina"].id].via_id == cadena["molinos"].id
    assert por_id[cadena["masa"].id].via_id in {cadena["harina"].id, cadena["levadura"].id}
    assert por_id[cadena["pan"].id].via_id == cadena["masa"].id


def test_reach_elemento_alcanzable_por_dos_caminos_se_visita_una_vez_con_nivel_minimo():
    # Combo -> Croissant -> Masa y también Combo -> Masa (más corto): Masa debe quedar en nivel 1.
    masa, croissant, combo = el("Masa"), el("Croissant"), el("Combo")
    g = DependencyGraph.build(
        [masa, croissant, combo], [dep(croissant, masa), dep(combo, croissant), dep(combo, masa)]
    )

    visitas = g.reach(masa.id, reverse=True)

    assert sorted(v.level for v in visitas) == [1, 1]
    assert len({v.node_id for v in visitas}) == len(visitas)


def test_reach_termina_aunque_haya_un_ciclo(cadena):
    # Se cierra el ciclo Pan <-> Masa madre. El recorrido debe terminar sin repetir elementos.
    g = graph_of(cadena, extra_deps=[dep(cadena["masa"], cadena["pan"])])

    visitas = g.reach(cadena["molinos"].id, reverse=True)
    ids = [v.node_id for v in visitas]

    assert len(ids) == len(set(ids)) == 4
    assert cadena["molinos"].id not in ids


def test_reach_en_ciclo_el_origen_no_se_cuenta_como_afectado(cadena):
    g = graph_of(cadena, extra_deps=[dep(cadena["masa"], cadena["pan"])])

    visitas = g.reach(cadena["pan"].id, reverse=True)

    assert [v.node_id for v in visitas] == [cadena["masa"].id]


def test_reach_de_elemento_aislado_devuelve_lista_vacia(cadena):
    g = graph_of(cadena)
    assert g.reach(cadena["panela"].id, reverse=True) == []
    assert g.reach(cadena["panela"].id) == []


def test_reach_con_origen_inexistente_lanza_error(cadena):
    with pytest.raises(ValueError):
        graph_of(cadena).reach(uuid4())


# ---------- AnalyzeImpactUseCase ----------
def test_impacto_de_un_proveedor_es_una_cadena(cadena):
    r = use_case_of(cadena).execute(cadena["molinos"].id, ImpactMode.IMPACT)

    assert r.outcome == ImpactOutcome.CHAIN
    assert r.affected_count == 4
    assert r.max_level == 3
    assert r.affected_by_type == {"insumo": 2, "producto": 2}
    assert [l.level for l in r.levels] == [1, 2, 3]
    assert r.levels[0].label == "Afectación directa"
    assert r.levels[1].label == "Afectación en cadena · nivel 2"
    assert {e.name for e in r.levels[0].elements} == {"Harina", "Levadura"}
    assert [e.name for e in r.levels[2].elements] == ["Pan"]


def test_impacto_explica_cada_paso_con_la_frase_del_negocio(cadena):
    r = use_case_of(cadena).execute(cadena["molinos"].id, ImpactMode.IMPACT)

    harina = next(e for l in r.levels for e in l.elements if e.name == "Harina")
    pan = next(e for l in r.levels for e in l.elements if e.name == "Pan")

    assert harina.reason == "Para producir Harina necesito Molinos SA"
    assert pan.reason == "Para producir Pan necesito Masa madre"
    assert pan.path[0] == "Molinos SA" and pan.path[-1] == "Pan" and len(pan.path) == 4


def test_consulta_de_requisitos_usa_la_frase_con_el_sentido_correcto(cadena):
    r = use_case_of(cadena).execute(cadena["pan"].id, ImpactMode.REQUIREMENTS)

    assert r.outcome == ImpactOutcome.CHAIN
    assert r.affected_count == 4 and r.max_level == 3
    assert r.levels[0].label == "Requisitos directos"
    assert r.levels[0].elements[0].reason == "Para producir Pan necesito Masa madre"
    molinos = next(e for l in r.levels for e in l.elements if e.name == "Molinos SA")
    assert molinos.path[0] == "Pan" and molinos.path[-1] == "Molinos SA"


def test_elemento_inexistente_lanza_not_found(cadena):
    with pytest.raises(ElementNotFoundException) as err:
        use_case_of(cadena).execute(uuid4(), ImpactMode.IMPACT)
    assert err.value.status_code == 404
    assert err.value.error_code == "ERR_ELEMENT_NOT_FOUND"


def test_elemento_inactivo_se_trata_como_inexistente(cadena):
    inactivo = el("Antiguo", ElementType.PROVEEDOR, is_active=False)
    uc = use_case_of(cadena, elements=cadena["elements"] + [inactivo])

    with pytest.raises(ElementNotFoundException):
        uc.execute(inactivo.id, ImpactMode.IMPACT)


def test_elemento_aislado_se_distingue_del_que_no_alcanza_a_nadie(cadena):
    uc = use_case_of(cadena)

    aislado = uc.execute(cadena["panela"].id, ImpactMode.IMPACT)
    assert aislado.outcome == ImpactOutcome.ISOLATED
    assert aislado.affected_count == 0 and aislado.levels == []

    sin_alcance = uc.execute(cadena["pan"].id, ImpactMode.IMPACT)  # tiene relaciones, pero nadie lo necesita
    assert sin_alcance.outcome == ImpactOutcome.NO_REACH
    assert sin_alcance.affected_count == 0 and sin_alcance.levels == []
    assert "Nadie necesita" in sin_alcance.summary


def test_proveedor_en_modo_requisitos_no_alcanza_nada(cadena):
    r = use_case_of(cadena).execute(cadena["molinos"].id, ImpactMode.REQUIREMENTS)
    assert r.outcome == ImpactOutcome.NO_REACH
    assert "no necesita ningún otro elemento" in r.summary


def test_resumen_usa_singular_cuando_se_afecta_un_solo_elemento(cadena):
    r = use_case_of(cadena).execute(cadena["masa"].id, ImpactMode.IMPACT)  # solo Pan
    assert r.affected_count == 1
    assert "1 elemento en 1 nivel" in r.summary


def test_impacto_con_ciclo_termina_y_reporta_sin_repetidos(cadena):
    uc = use_case_of(cadena, extra_deps=[dep(cadena["masa"], cadena["pan"])])

    r = uc.execute(cadena["molinos"].id, ImpactMode.IMPACT)

    nombres = [e.name for l in r.levels for e in l.elements]
    assert r.outcome == ImpactOutcome.CHAIN
    assert len(nombres) == len(set(nombres)) == 4