"""
Custom exceptions for the application.
"""

from typing import Any


class AppException(Exception):
    """Base exception for all application exceptions."""

    def __init__(self, message: str, status_code: int = 400, details: Any = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(AppException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: Any = None):
        super().__init__(message, status_code=401, details=details)


class AuthorizationError(AppException):
    """Raised when user doesn't have permission."""

    def __init__(self, message: str = "Not authorized", details: Any = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(AppException):
    """Raised when a resource is not found."""

    def __init__(self, message: str = "Resource not found", details: Any = None):
        super().__init__(message, status_code=404, details=details)


class ConflictError(AppException):
    """Raised when there's a conflict (e.g., duplicate)."""

    def __init__(self, message: str = "Resource conflict", details: Any = None):
        super().__init__(message, status_code=409, details=details)


class ValidationError(AppException):
    """Raised when validation fails."""

    def __init__(self, message: str = "Validation error", details: Any = None):
        super().__init__(message, status_code=422, details=details)


class DatabaseError(AppException):
    """Raised when database operation fails."""

    def __init__(self, message: str = "Database error", details: Any = None):
        super().__init__(message, status_code=500, details=details)
