from fastapi import APIRouter, Depends, status
from typing import List
from abastecepyme.application.dtos.element_dto import ElementCreateDTO, ElementResponseDTO
from abastecepyme.application.use_cases.create_element import CreateElementUseCase
from abastecepyme.application.use_cases.list_elements import ListElementsUseCase
from abastecepyme.presentation.dependencies import get_create_element_use_case, get_list_elements_use_case

router = APIRouter(prefix="/elements", tags=["Elements"])

@router.post("", response_model=ElementResponseDTO, status_code=status.HTTP_201_CREATED)
def create_element(
    dto: ElementCreateDTO,
    use_case: CreateElementUseCase = Depends(get_create_element_use_case)
):
    return use_case.execute(dto)

@router.get("", response_model=List[ElementResponseDTO])
def list_elements(
    use_case: ListElementsUseCase = Depends(get_list_elements_use_case)
):
    return use_case.execute()
