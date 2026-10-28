from uuid import UUID
from fastapi import APIRouter, Depends
from abastecepyme.application.dtos.impact_dto import ImpactResponseDTO
from abastecepyme.application.use_cases.analyze_impact import AnalyzeImpactUseCase
from abastecepyme.presentation.dependencies import get_impact_use_case

router = APIRouter(prefix="/impact", tags=["Impact"])


@router.get("/{element_id}", response_model=ImpactResponseDTO)
def analyze_impact(
    element_id: UUID,
    use_case: AnalyzeImpactUseCase = Depends(get_impact_use_case),
):
    return use_case.execute(element_id)
