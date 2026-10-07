"""Pruebas del caso de uso RegisterDependencyUseCase (sin base de datos, con repositorios en memoria)."""
from uuid import uuid4

import pytest

from abastecepyme.application.dtos.dependency_dto import DependencyCreateDTO
from abastecepyme.application.use_cases.get_graph import GetDependencyGraphUseCase
from abastecepyme.application.use_cases.list_dependencies import ListDependenciesUseCase
from abastecepyme.application.use_cases.register_dependency import RegisterDependencyUseCase
from abastecepyme.core.exceptions import (
    CycleDependencyException,
    DuplicateDependencyException,
    ElementNotFoundException,
    InvalidDependencyException,
    SelfDependencyException,
)
from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository


class InMemoryElementRepository(ElementRepository):
    def __init__(self):
        self.items = {}

    def save(self, element):
        self.items[element.id] = element
        return element

    def get_by_id(self, element_id):
        return self.items.get(element_id)

    def get_all(self, active_only=True):
        return [e for e in self.items.values() if e.is_active or not active_only]


class InMemoryDependencyRepository(DependencyRepository):
    def __init__(self):
        self.items = []

    def save(self, dependency):
        self.items.append(dependency)
        return dependency

    def exists(self, requiring_element_id, required_element_id):
        return any(
            d.requiring_element_id == requiring_element_id
            and d.required_element_id == required_element_id
            for d in self.items
        )

    def get_all(self):
        return list(self.items)

    def get_dependencies_for_element(self, element_id):
        return [d for d in self.items if d.requiring_element_id == element_id]


@pytest.fixture
def repos():
    return InMemoryElementRepository(), InMemoryDependencyRepository()


def make_element(repo, name, element_type, is_active=True):
    element = Element(id=uuid4(), name=name, element_type=element_type, is_active=is_active)
    repo.save(element)
    return element


def register(repos, requiring, required):
    elements, dependencies = repos
    use_case = RegisterDependencyUseCase(elements, dependencies)
    return use_case.execute(
        DependencyCreateDTO(requiring_element_id=requiring.id, required_element_id=required.id)
    )


def test_registra_insumo_que_requiere_proveedor(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)

    result = register(repos, insumo, proveedor)

    assert result.requiring_element_id == insumo.id
    assert result.required_element_id == proveedor.id
    assert repos[1].exists(insumo.id, proveedor.id)


def test_registra_producto_que_requiere_insumo(repos):
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)
    producto = make_element(repos[0], "Pan", ElementType.PRODUCTO)

    register(repos, producto, insumo)

    assert repos[1].exists(producto.id, insumo.id)


def test_rechaza_autodependencia(repos):
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)

    with pytest.raises(SelfDependencyException) as error:
        register(repos, insumo, insumo)

    assert error.value.status_code == 400
    assert error.value.error_code == "ERR_SELF_DEPENDENCY"


def test_rechaza_dependencia_repetida(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)
    register(repos, insumo, proveedor)

    with pytest.raises(DuplicateDependencyException) as error:
        register(repos, insumo, proveedor)

    assert error.value.status_code == 409
    assert error.value.error_code == "ERR_DEPENDENCY_ALREADY_EXISTS"
    assert len(repos[1].items) == 1


def test_elemento_inexistente(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    fantasma = Element(id=uuid4(), name="Fantasma", element_type=ElementType.INSUMO)

    with pytest.raises(ElementNotFoundException) as error:
        register(repos, fantasma, proveedor)

    assert error.value.status_code == 404


def test_elemento_inactivo_se_trata_como_inexistente(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR, is_active=False)
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)

    with pytest.raises(ElementNotFoundException):
        register(repos, insumo, proveedor)


def test_proveedor_no_puede_requerir_nada(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)

    with pytest.raises(InvalidDependencyException):
        register(repos, proveedor, insumo)


def test_insumo_solo_puede_requerir_proveedor(repos):
    insumo_a = make_element(repos[0], "Harina", ElementType.INSUMO)
    insumo_b = make_element(repos[0], "Levadura", ElementType.INSUMO)

    with pytest.raises(InvalidDependencyException):
        register(repos, insumo_a, insumo_b)


def test_producto_no_puede_requerir_proveedor_directo(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    producto = make_element(repos[0], "Pan", ElementType.PRODUCTO)

    with pytest.raises(InvalidDependencyException):
        register(repos, producto, proveedor)


def test_listar_dependencias(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)
    producto = make_element(repos[0], "Pan", ElementType.PRODUCTO)
    register(repos, insumo, proveedor)
    register(repos, producto, insumo)

    result = ListDependenciesUseCase(repos[1]).execute()

    pares = {(d.requiring_element_id, d.required_element_id) for d in result}
    assert pares == {(insumo.id, proveedor.id), (producto.id, insumo.id)}


def test_listar_dependencias_vacio(repos):
    assert ListDependenciesUseCase(repos[1]).execute() == []


def test_rechaza_ciclo_directo(repos):
    producto_a = make_element(repos[0], "Combo", ElementType.PRODUCTO)
    producto_b = make_element(repos[0], "Pan", ElementType.PRODUCTO)
    register(repos, producto_a, producto_b)

    with pytest.raises(CycleDependencyException) as error:
        register(repos, producto_b, producto_a)

    assert error.value.status_code == 409
    assert error.value.error_code == "ERR_DEPENDENCY_CYCLE"
    assert len(repos[1].items) == 1


def test_rechaza_ciclo_indirecto(repos):
    a = make_element(repos[0], "A", ElementType.PRODUCTO)
    b = make_element(repos[0], "B", ElementType.PRODUCTO)
    c = make_element(repos[0], "C", ElementType.PRODUCTO)
    register(repos, a, b)
    register(repos, b, c)

    with pytest.raises(CycleDependencyException):
        register(repos, c, a)


def test_permite_atajo_sin_ciclo(repos):
    a = make_element(repos[0], "A", ElementType.PRODUCTO)
    b = make_element(repos[0], "B", ElementType.PRODUCTO)
    c = make_element(repos[0], "C", ElementType.PRODUCTO)
    register(repos, a, b)
    register(repos, b, c)

    register(repos, a, c)  # A -> C es redundante pero válido

    assert repos[1].exists(a.id, c.id)


def test_obtener_grafo(repos):
    proveedor = make_element(repos[0], "Molinos S.A.", ElementType.PROVEEDOR)
    insumo = make_element(repos[0], "Harina", ElementType.INSUMO)
    producto = make_element(repos[0], "Pan", ElementType.PRODUCTO)
    register(repos, insumo, proveedor)
    register(repos, producto, insumo)

    graph = GetDependencyGraphUseCase(repos[0], repos[1]).execute()

    assert {n.name for n in graph.nodes} == {"Molinos S.A.", "Harina", "Pan"}
    descripciones = {e.description for e in graph.edges}
    assert descripciones == {
        "Para producir Harina necesito Molinos S.A.",
        "Para producir Pan necesito Harina",
    }


def test_obtener_grafo_vacio(repos):
    graph = GetDependencyGraphUseCase(repos[0], repos[1]).execute()

    assert graph.nodes == []
    assert graph.edges == []