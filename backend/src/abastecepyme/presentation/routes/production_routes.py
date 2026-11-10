from fastapi import APIRouter, Depends

from abastecepyme.application.dtos.production_order_dto import ProductionOrderResponseDTO
from abastecepyme.application.use_cases.get_production_order import GetProductionOrderUseCase
from abastecepyme.presentation.dependencies import get_production_order_use_case

router = APIRouter(prefix="/production-order", tags=["Production"])


@router.get("", response_model=ProductionOrderResponseDTO)
def get_production_order(
    use_case: GetProductionOrderUseCase = Depends(get_production_order_use_case),
):
    """
    Orden de trabajo válido: cada elemento aparece después de todo lo que necesita.
    Si las dependencias forman un ciclo no existe tal orden y responde 409 ERR_CYCLE_DETECTED.
    """
    return use_case.execute()