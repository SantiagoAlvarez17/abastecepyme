from uuid import uuid4

import pytest

from abastecepyme.application.use_cases.analyze_impact import AnalyzeImpactUseCase
from abastecepyme.core.exceptions import ElementNotFoundException
from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.enums.element_type import ElementType


class InMemoryElementRepository:
    def __init__(self, elements):
        self.elements = elements

    def get_all(self, active_only=True):
        return [element for element in self.elements if not active_only or element.is_active]


class InMemoryDependencyRepository:
    def __init__(self, dependencies):
        self.dependencies = dependencies

    def get_all(self):
        return self.dependencies


def create_element(name, element_type):
    return Element(id=uuid4(), name=name, element_type=element_type)


def create_use_case(elements, dependencies):
    return AnalyzeImpactUseCase(
        InMemoryElementRepository(elements),
        InMemoryDependencyRepository(dependencies),
    )


def test_proveedor_recorre_en_sentido_inverso_hasta_productos():
    proveedor = create_element("Molinos", ElementType.PROVEEDOR)
    harina = create_element("Harina", ElementType.INSUMO)
    pan = create_element("Pan", ElementType.PRODUCTO)
    use_case = create_use_case(
        [proveedor, harina, pan],
        [
            Dependency(requiring_element_id=harina.id, required_element_id=proveedor.id),
            Dependency(requiring_element_id=pan.id, required_element_id=harina.id),
        ],
    )

    result = use_case.execute(proveedor.id)

    assert result.status == "chain_found"
    assert result.direction == "hacia quienes dependen de este elemento"
    assert [element.name for element in result.visited_elements] == ["Harina", "Pan"]


def test_producto_recorre_en_direccion_de_sus_requisitos():
    harina = create_element("Harina", ElementType.INSUMO)
    pan = create_element("Pan", ElementType.PRODUCTO)
    use_case = create_use_case(
        [harina, pan],
        [Dependency(requiring_element_id=pan.id, required_element_id=harina.id)],
    )

    result = use_case.execute(pan.id)

    assert result.status == "chain_found"
    assert result.direction == "hacia los elementos requeridos por este producto"
    assert [element.name for element in result.visited_elements] == ["Harina"]


def test_elemento_existente_sin_vecinos_reporta_estado_sin_dependencias():
    proveedor = create_element("Proveedor aislado", ElementType.PROVEEDOR)
    result = create_use_case([proveedor], []).execute(proveedor.id)

    assert result.status == "no_dependencies"
    assert result.visited_elements == []


def test_elemento_inexistente_lanza_error_de_no_encontrado():
    use_case = create_use_case([], [])

    with pytest.raises(ElementNotFoundException):
        use_case.execute(uuid4())
