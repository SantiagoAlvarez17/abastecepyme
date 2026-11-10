from abastecepyme.application.dtos.production_order_dto import (
    ProductionOrderResponseDTO,
    ProductionStepDTO,
)
from abastecepyme.core.exceptions import CyclicDependenciesException
from abastecepyme.domain.graph.dependency_graph import DependencyGraph
from abastecepyme.domain.interfaces.dependency_repository import DependencyRepository
from abastecepyme.domain.interfaces.element_repository import ElementRepository


def _count(n: int, singular: str, plural: str) -> str:
    return f"{n} {singular if n == 1 else plural}"


class GetProductionOrderUseCase:
    """
    Orden de trabajo para preparar todo el catálogo: cada elemento aparece después de
    todo lo que necesita. Si las dependencias se contradicen (ciclo), no hay orden válido
    y se lanza `CyclicDependenciesException`: nunca se devuelve un orden falso.
    """

    def __init__(
        self,
        element_repository: ElementRepository,
        dependency_repository: DependencyRepository,
    ):
        self.element_repository = element_repository
        self.dependency_repository = dependency_repository

    def execute(self) -> ProductionOrderResponseDTO:
        graph = DependencyGraph.build(
            self.element_repository.get_all(active_only=True),
            self.dependency_repository.get_all(),
        )

        ordering = graph.preparation_order()
        if not ordering.is_valid:
            raise CyclicDependenciesException(
                [graph.get_node(node_id).name for node_id in ordering.cycle]
            )

        steps: list[ProductionStepDTO] = []
        for stage_number, stage in enumerate(ordering.stages, start=1):
            for node_id in stage:
                node = graph.get_node(node_id)
                requires = sorted(
                    (graph.get_node(r).name for r in graph.requirements_of(node_id)),
                    key=str.casefold,
                )
                steps.append(
                    ProductionStepDTO(
                        position=len(steps) + 1,
                        stage=stage_number,
                        id=node.id,
                        name=node.name,
                        element_type=node.element_type,
                        requires=requires,
                    )
                )

        return ProductionOrderResponseDTO(
            total_elements=len(steps),
            stage_count=len(ordering.stages),
            summary=self._summary(len(steps), len(ordering.stages)),
            steps=steps,
        )

    @staticmethod
    def _summary(elements: int, stages: int) -> str:
        if elements == 0:
            return "El catálogo está vacío: no hay nada que ordenar."
        return (
            f"Orden de preparación válido: {_count(elements, 'elemento', 'elementos')} "
            f"en {_count(stages, 'etapa', 'etapas')}. "
            "Los elementos de una misma etapa no dependen entre sí y pueden prepararse en paralelo."
        )