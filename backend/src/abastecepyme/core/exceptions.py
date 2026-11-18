class BusinessException(Exception):
    def __init__(
        self,
        error_code: str,
        message: str,
        status_code: int = 400,
        extra: dict | None = None,
    ):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
        # Campos adicionales que se agregan tal cual al cuerpo de la respuesta de error
        self.extra = extra or {}
        super().__init__(self.message)

class ElementNotFoundException(BusinessException):
    def __init__(self, element_id: str):
        super().__init__(
            error_code="ERR_ELEMENT_NOT_FOUND",
            message=f"El elemento con ID {element_id} no existe o está inactivo.",
            status_code=404
        )

class InvalidDependencyException(BusinessException):
    def __init__(self, message: str):
        super().__init__(
            error_code="ERR_INVALID_DEPENDENCY_TYPE",
            message=message,
            status_code=400
        )

class SelfDependencyException(BusinessException):
    def __init__(self, name: str):
        super().__init__(
            error_code="ERR_SELF_DEPENDENCY",
            message=f"'{name}' no puede depender de sí mismo.",
            status_code=400
        )

class DuplicateDependencyException(BusinessException):
    def __init__(self, requiring_name: str, required_name: str):
        super().__init__(
            error_code="ERR_DUPLICATE_DEPENDENCY",
            message=f"La dependencia 'Para producir {requiring_name} necesito {required_name}' ya existe.",
            status_code=409
        )

class DuplicateElementException(BusinessException):
    def __init__(self, name: str):
        super().__init__(
            error_code="ERR_DUPLICATE_ELEMENT",
            message=f"Ya existe un elemento con el nombre '{name}'.",
            status_code=409
        )


class CyclicDependenciesException(BusinessException):
    """Las dependencias se contradicen: no existe un orden de preparación válido."""

    def __init__(self, cycles: list[dict], blocked_by_cycle: list[dict]):
        """
        `cycles`: un ciclo por grupo, como {"elements": [{id, name, element_type}, ...], "text": "A → B → A"}.
                  `elements` es un camino cerrado: el primer elemento se repite al final.
        `blocked_by_cycle`: elementos que no forman parte del ciclo pero dependen de él.
        """
        self.cycles = cycles
        self.blocked_by_cycle = blocked_by_cycle
        super().__init__(
            error_code="ERR_CYCLE_DETECTED",
            message=self._build_message(cycles, [e["name"] for e in blocked_by_cycle]),
            status_code=409,
            extra={"cycles": cycles, "blocked_by_cycle": blocked_by_cycle},
        )

    @staticmethod
    def _build_message(cycles: list[dict], blocked_names: list[str]) -> str:
        if len(cycles) == 1:
            intro = f"Ciclo detectado: {cycles[0]['text']}."
            why = "cada elemento del ciclo necesita al siguiente y el último vuelve a necesitar al primero"
            of_what = "del ciclo"
        else:
            listed = " ".join(f"{i}) {c['text']}." for i, c in enumerate(cycles, start=1))
            intro = f"Ciclos detectados ({len(cycles)}): {listed}"
            why = "en cada ciclo, cada elemento necesita al siguiente y el último vuelve a necesitar al primero"
            of_what = "de los ciclos"
        parts = [
            intro,
            "Las dependencias se contradicen, por lo que no existe un orden de preparación válido: "
            f"{why}, así que ninguno puede prepararse primero.",
        ]
        if blocked_names:
            parts.append(f"También quedan sin orden porque dependen {of_what}: {', '.join(blocked_names)}.")
        return " ".join(parts)
