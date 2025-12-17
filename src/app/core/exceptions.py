"""
Application exceptions.
Custom exception classes for consistent error handling.
"""


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message=message, status_code=404)


class BadRequestException(AppException):
    """Bad request exception."""

    def __init__(self, message: str = "Bad request"):
        super().__init__(message=message, status_code=400)

