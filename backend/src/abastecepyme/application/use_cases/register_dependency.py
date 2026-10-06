from abastecepyme.domain.entities.dependency import Dependency
from abastecepyme.domain.enums.element_type import ElementType
from abastecepyme.domain.interfaces.element_repository import ElementRepository
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.application.dtos.dependency_dto import DependencyCreateDTO, DependencyResponseDTO
from abastecepyme.core.exceptions import ElementNotFoundException, InvalidDependencyException

class RegisterDependencyUseCase:
    def __init__(
        self, 
        element_repository: ElementRepository, 
        dependency_repository: DependencyRepository
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self, dto: DependencyCreateDTO) -> DependencyResponseDTO:
        req_id = dto.requiring_element_id
        required_id = dto.required_element_id

        # 1. Validar existencia
        requiring_element = self.element_repository.get_by_id(req_id)
        if not requiring_element or not requiring_element.is_active:
            raise ElementNotFoundException(str(req_id))

        required_element = self.element_repository.get_by_id(required_id)
        if not required_element or not required_element.is_active:
            raise ElementNotFoundException(str(required_id))

        # 2. Validar semántica y lógica de negocio
        req_type = requiring_element.element_type
        required_type = required_element.element_type

        if req_type == ElementType.PROVEEDOR:
            raise InvalidDependencyException("Un proveedor no puede depender de ningún elemento (es un nodo origen).")
        
        if req_type == ElementType.INSUMO and required_type != ElementType.PROVEEDOR:
            raise InvalidDependencyException("Un insumo solo puede depender de un proveedor.")

        if req_type == ElementType.PRODUCTO and required_type == ElementType.PROVEEDOR:
            raise InvalidDependencyException("Un producto no puede depender directamente de un proveedor (requiere insumos).")

        # 3. Guardar dependencia
        dependency = Dependency(
            requiring_element_id=req_id,
            required_element_id=required_id
        )
        saved_dep = self.dependency_repository.save(dependency)

        return DependencyResponseDTO(
            requiring_element_id=saved_dep.requiring_element_id,
            required_element_id=saved_dep.required_element_id
        )
