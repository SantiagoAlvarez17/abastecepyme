from fastapi import APIRouter, Depends, Query

from abastecepyme.application.dtos.dashboard_dto import DashboardSummaryDTO
from abastecepyme.application.use_cases.get_dashboard_summary import GetDashboardSummaryUseCase
from abastecepyme.presentation.dependencies import get_dashboard_summary_use_case

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryDTO)
def get_dashboard_summary(
    limit: int = Query(5, ge=1, le=50, description="Maximum number of critical points to return"),
    use_case: GetDashboardSummaryUseCase = Depends(get_dashboard_summary_use_case),
):
    """
    Supply dashboard overview: catalog totals, isolated elements, production order status
    (valid order or exact cycle) and the suppliers/inputs whose failure stops the most products.
    Always answers 200: a cycle is reported as `production.status = "cycle"`, not as an error,
    because the dashboard must keep working precisely when the catalog is contradictory.
    """
    return use_case.execute(limit)
