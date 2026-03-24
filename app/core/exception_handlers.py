"""
Exception handlers for FastAPI.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppException
from app.core.logging_config import logger


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(
        f"Application error: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "details": exc.details,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url.path),
        },
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(
        f"Validation error: {errors}",
        extra={"path": request.url.path, "method": request.method},
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation error",
            "details": errors,
            "path": str(request.url.path),
        },
    )


async def sqlalchemy_exception_handler(
    request: Request, exc: SQLAlchemyError
) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    logger.error(
        f"Database error: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Database error occurred",
            "details": "An error occurred while processing your request. Please try again.",
            "path": str(request.url.path),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle any unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": "An unexpected error occurred. Please contact support.",
            "path": str(request.url.path),
        },
    )
