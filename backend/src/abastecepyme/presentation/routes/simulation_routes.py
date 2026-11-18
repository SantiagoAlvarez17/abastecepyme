from fastapi import APIRouter, Depends

from abastecepyme.application.dtos.unavailability_simulation_dto import (
    UnavailabilitySimulationRequestDTO,
    UnavailabilitySimulationResponseDTO,
)
from abastecepyme.application.use_cases.simulate_unavailability import (
    SimulateUnavailabilityUseCase,
)
from abastecepyme.presentation.dependencies import get_unavailability_simulation_use_case

router = APIRouter(prefix="/simulations", tags=["Simulations"])


@router.post(
    "/unavailability",
    response_model=UnavailabilitySimulationResponseDTO,
)
def simulate_unavailability(
    dto: UnavailabilitySimulationRequestDTO,
    use_case: SimulateUnavailabilityUseCase = Depends(
        get_unavailability_simulation_use_case
    ),
):
    """Simula el impacto de la indisponibilidad simultánea de varios elementos."""
    return use_case.execute(dto.element_ids)
