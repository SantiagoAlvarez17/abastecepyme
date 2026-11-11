from fastapi import APIRouter, Depends

from abastecepyme.application.dtos.production_order_dto import (
    CycleErrorResponseDTO,
    ProductionOrderResponseDTO,
)
from abastecepyme.application.use_cases.get_production_order import GetProductionOrderUseCase
from abastecepyme.presentation.dependencies import get_production_order_use_case

router = APIRouter(prefix="/production-order", tags=["Production"])


@router.get(
    "",
    response_model=ProductionOrderResponseDTO,
    responses={
        409: {
            "model": CycleErrorResponseDTO,
            "description": "Las dependencias forman un ciclo: no existe un orden válido. Indica el ciclo exacto.",
        }
    },
)
def get_production_order(
    use_case: GetProductionOrderUseCase = Depends(get_production_order_use_case),
):
    """
    Orden de trabajo válido: cada elemento aparece después de todo lo que necesita.
    Si las dependencias forman un ciclo no existe tal orden: responde 409 ERR_CYCLE_DETECTED con el
    ciclo exacto (`cycles`) y los elementos que solo dependen de él (`blocked_by_cycle`).
    """
    return use_case.execute()