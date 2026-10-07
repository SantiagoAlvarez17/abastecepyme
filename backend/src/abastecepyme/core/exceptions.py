class BusinessException(Exception):
    def __init__(self, error_code: str, message: str, status_code: int = 400):
        self.error_code = error_code
        self.message = message
        self.status_code = status_code
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
    def __init__(self):
        super().__init__(
            error_code="ERR_SELF_DEPENDENCY",
            message="Un elemento no puede depender de sí mismo.",
            status_code=400
        )

class DuplicateDependencyException(BusinessException):
    def __init__(self, requiring: str, required: str):
        super().__init__(
            error_code="ERR_DEPENDENCY_ALREADY_EXISTS",
            message=f"La dependencia ya existe: '{requiring}' ya requiere a '{required}'.",
            status_code=409
        )

class CycleDependencyException(BusinessException):
    def __init__(self, requiring: str, required: str):
        super().__init__(
            error_code="ERR_DEPENDENCY_CYCLE",
            message=(
                f"No se puede registrar: '{requiring}' requiere a '{required}', pero "
                f"'{required}' ya depende (directa o indirectamente) de '{requiring}'. "
                "Se formaría un ciclo."
            ),
            status_code=409
        )