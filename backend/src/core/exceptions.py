class AppError(Exception):
    """Error de dominio; mapear a HTTP en capa API."""

    def __init__(self, message: str, code: str = "app_error") -> None:
        self.message = message
        self.code = code
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, resource: str = "resource") -> None:
        super().__init__(f"{resource} not found", code="not_found")


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message, code="forbidden")


class TenantIsolationError(ForbiddenError):
    def __init__(self) -> None:
        super().__init__("Cross-tenant access denied")
