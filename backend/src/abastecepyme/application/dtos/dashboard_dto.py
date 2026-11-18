from typing import Dict, List, Literal

from pydantic import BaseModel

from abastecepyme.application.dtos.element_dto import ElementRefDTO
from abastecepyme.application.dtos.production_order_dto import CycleDTO


class CriticalPointDTO(ElementRefDTO):
    """A supplier or input whose unavailability stops production further down the chain."""

    affected_products: int  # products that can no longer be produced if this element fails
    affected_total: int     # every element reached by the failure (inputs and products)
    products: List[str]     # names of the affected products, alphabetically


class ProductionStatusDTO(BaseModel):
    status: Literal["empty", "valid", "cycle"]
    message: str
    stage_count: int    # stages of the valid order (0 when empty or cyclic)
    blocked_count: int  # elements left without order because of a cycle
    cycles: List[CycleDTO]


class DashboardSummaryDTO(BaseModel):
    total_elements: int
    total_dependencies: int
    by_type: Dict[str, int]          # every element type is present, even with 0
    isolated: List[ElementRefDTO]    # elements with no dependency in either direction
    production: ProductionStatusDTO
    critical_points: List[CriticalPointDTO]  # most critical first, at most `limit`
