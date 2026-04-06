class AppException(Exception):
    """Base exception for all application-level errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class ConflictException(AppException):
    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message, status_code=409, error_code="CONFLICT")


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class InvalidCredentialsException(AppException):
    def __init__(self, message: str = "Invalid email or password") -> None:
        super().__init__(message, status_code=401, error_code="INVALID_CREDENTIALS")


class InvalidTokenException(AppException):
    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(message, status_code=401, error_code="INVALID_TOKEN")


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message, status_code=422, error_code="VALIDATION_ERROR")
