from typing import List
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.application.dtos.dependency_dto import DependencyResponseDTO

class ListDependenciesUseCase:
    def __init__(self, dependency_repository: DependencyRepository):
        self.dependency_repository = dependency_repository

    def execute(self) -> List[DependencyResponseDTO]:
        return [
            DependencyResponseDTO(
                requiring_element_id=d.requiring_element_id,
                required_element_id=d.required_element_id
            ) for d in self.dependency_repository.get_all()
        ]
