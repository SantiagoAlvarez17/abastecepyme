from fastapi import APIRouter, Depends, status
from abastecepyme.application.dtos.dependency_dto import DependencyCreateDTO, DependencyResponseDTO
from abastecepyme.application.use_cases.register_dependency import RegisterDependencyUseCase
from abastecepyme.presentation.dependencies import get_register_dependency_use_case

router = APIRouter(prefix="/dependencies", tags=["Dependencies"])

@router.post("", response_model=DependencyResponseDTO, status_code=status.HTTP_201_CREATED)
def register_dependency(
    dto: DependencyCreateDTO,
    use_case: RegisterDependencyUseCase = Depends(get_register_dependency_use_case)
):
    return use_case.execute(dto)
