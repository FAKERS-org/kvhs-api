"""
Logging configuration for the application.
"""

import logging
import sys
from pathlib import Path

from app.core.config import settings


# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)


# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging():
    """Setup logging configuration."""
    # Root logger
    root_logger = logging.getLogger()

    if getattr(root_logger, "_kvhs_logging_configured", False):
        return root_logger

    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    console_handler.setFormatter(console_formatter)

    # File handler
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    file_handler.setFormatter(file_formatter)

    # Error file handler
    error_handler = logging.FileHandler(log_dir / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    error_handler.setFormatter(error_formatter)

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)

    # Reduce noise from external libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    root_logger._kvhs_logging_configured = True

    return root_logger


# Initialize logger
logger = setup_logging()


def log_request(method: str, path: str, status_code: int, duration: float):
    """Log HTTP request."""
    logger.info(f"{method} {path} - {status_code} - {duration:.2f}ms")


def log_error(error: Exception, context: dict | None = None):
    """Log error with context."""
    logger.error(f"Error: {str(error)}", extra=context or {}, exc_info=True)


def log_auth_attempt(email: str, success: bool, reason: str | None = None):
    """Log authentication attempt."""
    if success:
        logger.info(f"Successful login: {email}")
    else:
        logger.warning(f"Failed login attempt: {email} - Reason: {reason}")


def log_db_query(query: str, duration: float):
    """Log database query performance."""
    if duration > 1000:  # Log slow queries (>1s)
        logger.warning(f"Slow query ({duration:.2f}ms): {query}")
