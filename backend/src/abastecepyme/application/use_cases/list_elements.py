from typing import List
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.application.dtos.element_dto import ElementResponseDTO

class ListElementsUseCase:
    def __init__(self, element_repository: ElementRepository):
        self.element_repository = element_repository

    def execute(self) -> List[ElementResponseDTO]:
        elements = self.element_repository.get_all(active_only=True)
        return [
            ElementResponseDTO(
                id=e.id,
                name=e.name,
                element_type=e.element_type,
                is_active=e.is_active
            ) for e in elements
        ]
