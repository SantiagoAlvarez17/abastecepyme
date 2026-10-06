from uuid import uuid4
from abastecepyme.domain.entities.element import Element
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.application.dtos.element_dto import ElementCreateDTO, ElementResponseDTO

class CreateElementUseCase:
    def __init__(self, element_repository: ElementRepository):
        self.element_repository = element_repository

    def execute(self, dto: ElementCreateDTO) -> ElementResponseDTO:
        element = Element(
            id=uuid4(),
            name=dto.name,
            element_type=dto.element_type,
            is_active=True
        )
        saved_element = self.element_repository.save(element)
        return ElementResponseDTO(
            id=saved_element.id,
            name=saved_element.name,
            element_type=saved_element.element_type,
            is_active=saved_element.is_active
        )
