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
