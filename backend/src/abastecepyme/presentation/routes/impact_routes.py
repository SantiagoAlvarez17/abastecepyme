from uuid import UUID

from fastapi import APIRouter, Depends

from abastecepyme.application.dtos.impact_dto import ImpactResponseDTO
from abastecepyme.application.use_cases.analyze_impact import AnalyzeImpactUseCase
from abastecepyme.domain.enums.impact import ImpactMode
from abastecepyme.presentation.dependencies import get_impact_use_case

router = APIRouter(prefix="/impact", tags=["Impact"])


@router.get("/{element_id}", response_model=ImpactResponseDTO)
def analyze_impact(
    element_id: UUID,
    mode: ImpactMode = ImpactMode.IMPACT,
    use_case: AnalyzeImpactUseCase = Depends(get_impact_use_case),
):
    """
    mode=impact (por defecto): qué se afecta si este elemento no está disponible.
    mode=requirements: qué necesita este elemento para producirse.
    """
    return use_case.execute(element_id, mode)
