from typing import Dict, List
from uuid import UUID

from abastecepyme.application.dtos.element_dto import ElementResponseDTO
from abastecepyme.application.dtos.impact_dto import (
    ImpactLevelDTO,
    ImpactResponseDTO,
    ReachedElementDTO,
)
from abastecepyme.core.exceptions import ElementNotFoundException
from abastecepyme.domain.enums.impact import ImpactMode, ImpactOutcome
from abastecepyme.domain.graph.dependency_graph import DependencyGraph, Visit
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository


def _count(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


class AnalyzeImpactUseCase:
    """
    Consulta de alcance sobre un elemento.

    - IMPACT: "si este elemento no está disponible, ¿qué se afecta?" (recorrido inverso).
    - REQUIREMENTS: "para producir este elemento, ¿qué necesito?" (recorrido directo).
    """

    def __init__(self, element_repository: ElementRepository, dependency_repository: DependencyRepository):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self, element_id: UUID, mode: ImpactMode) -> ImpactResponseDTO:
        graph = DependencyGraph.build(
            self.element_repository.get_all(active_only=True),
            self.dependency_repository.get_all(),
        )

        # Caso 1: el elemento no existe (o está inactivo).
        if not graph.has_node(element_id):
            raise ElementNotFoundException(str(element_id))

        origin = graph.get_node(element_id)
        visits = graph.reach(element_id, reverse=(mode == ImpactMode.IMPACT))
        outcome = self._outcome(graph, element_id, visits)

        reached = self._describe(graph, element_id, visits, mode)
        max_level = max((v.level for v in visits), default=0)

        by_type: Dict[str, int] = {}
        for item in reached:
            by_type[item.element_type.value] = by_type.get(item.element_type.value, 0) + 1

        return ImpactResponseDTO(
            mode=mode,
            origin=ElementResponseDTO(
                id=origin.id, name=origin.name, element_type=origin.element_type, is_active=origin.is_active
            ),
            outcome=outcome,
            summary=self._summary(origin.name, mode, outcome, len(reached), max_level),
            affected_count=len(reached),
            max_level=max_level,
            affected_by_type=by_type,
            levels=self._group_by_level(reached, mode),
        )

    @staticmethod
    def _outcome(graph: DependencyGraph, element_id: UUID, visits: List[Visit]) -> ImpactOutcome:
        if visits:
            return ImpactOutcome.CHAIN
        if not graph.requirements_of(element_id) and not graph.dependents_of(element_id):
            return ImpactOutcome.ISOLATED  # Caso 2: sin ninguna dependencia registrada
        return ImpactOutcome.NO_REACH      # tiene relaciones, pero no en el sentido consultado

    @staticmethod
    def _describe(
        graph: DependencyGraph, origin_id: UUID, visits: List[Visit], mode: ImpactMode
    ) -> List[ReachedElementDTO]:
        via_of = {v.node_id: v.via_id for v in visits}

        def path_names(node_id: UUID) -> List[str]:
            chain = [node_id]
            while chain[-1] != origin_id:
                chain.append(via_of[chain[-1]])
            return [graph.get_node(i).name for i in reversed(chain)]

        items = []
        for v in visits:
            node = graph.get_node(v.node_id)
            via = graph.get_node(v.via_id)
            # Frase de la arista recorrida. IMPACT: node requiere a via. REQUIREMENTS: via requiere a node.
            reason = (
                f"Para producir {node.name} necesito {via.name}"
                if mode == ImpactMode.IMPACT
                else f"Para producir {via.name} necesito {node.name}"
            )
            items.append(
                ReachedElementDTO(
                    id=node.id,
                    name=node.name,
                    element_type=node.element_type,
                    level=v.level,
                    via_id=v.via_id,
                    reason=reason,
                    path=path_names(v.node_id),
                )
            )
        return items

    @staticmethod
    def _group_by_level(reached: List[ReachedElementDTO], mode: ImpactMode) -> List[ImpactLevelDTO]:
        # `reached` ya viene en orden BFS, es decir, ordenado por nivel.
        groups: Dict[int, List[ReachedElementDTO]] = {}
        for item in reached:
            groups.setdefault(item.level, []).append(item)

        def label(level: int) -> str:
            if mode == ImpactMode.IMPACT:
                return "Afectación directa" if level == 1 else f"Afectación en cadena · nivel {level}"
            return "Requisitos directos" if level == 1 else f"Requisitos indirectos · nivel {level}"

        return [ImpactLevelDTO(level=lv, label=label(lv), elements=els) for lv, els in groups.items()]

    @staticmethod
    def _summary(name: str, mode: ImpactMode, outcome: ImpactOutcome, count: int, levels: int) -> str:
        if outcome == ImpactOutcome.ISOLATED:
            return f"“{name}” no tiene dependencias registradas: no necesita nada y nadie lo necesita."
        if outcome == ImpactOutcome.NO_REACH:
            return (
                f"Nadie necesita “{name}”: su indisponibilidad no afecta a ningún otro elemento."
                if mode == ImpactMode.IMPACT
                else f"“{name}” no necesita ningún otro elemento para producirse."
            )
        elementos = _count(count, "elemento", "elementos")
        niveles = _count(levels, "nivel", "niveles")
        if mode == ImpactMode.IMPACT:
            return f"Si “{name}” no está disponible, se afectan {elementos} en {niveles} de la cadena."
        return f"Para producir “{name}” se necesitan, directa o indirectamente, {elementos} en {niveles}."