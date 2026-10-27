from enum import Enum


class ImpactMode(str, Enum):
    """Sentido en que se recorre el grafo al consultar un elemento."""

    # "Si este elemento falla, ¿qué se afecta?" -> quienes lo requieren, directa o indirectamente.
    IMPACT = "impact"
    # "Para producir este elemento, ¿qué necesito?" -> lo que requiere, directa o indirectamente.
    REQUIREMENTS = "requirements"


class ImpactOutcome(str, Enum):
    """Los tres resultados posibles de una consulta sobre un elemento que SÍ existe."""

    CHAIN = "chain"          # el recorrido alcanzó al menos un elemento
    NO_REACH = "no_reach"    # tiene relaciones, pero ninguna en el sentido consultado
    ISOLATED = "isolated"    # no tiene ninguna relación registrada