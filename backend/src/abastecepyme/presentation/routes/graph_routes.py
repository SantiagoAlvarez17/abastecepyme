from fastapi import APIRouter, Depends
from abastecepyme.application.dtos.graph_dto import GraphResponseDTO
from abastecepyme.application.use_cases.get_graph import GetGraphUseCase
from abastecepyme.presentation.dependencies import get_graph_use_case

router = APIRouter(prefix="/graph", tags=["Graph"])

@router.get("", response_model=GraphResponseDTO)
def get_graph(
    use_case: GetGraphUseCase = Depends(get_graph_use_case)
):
    return use_case.execute()
