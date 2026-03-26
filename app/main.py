"""Main FastAPI application with all routes and middleware."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router, api_v1_router
from app.core.config import settings
from app.core.constants import APIConfig
from app.core.exception_handlers import (
    app_exception_handler,
    generic_exception_handler,
    sqlalchemy_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from app.core.logging_config import logger
from app.core.middleware import RequestLoggingMiddleware
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run application startup and shutdown tasks."""
    logger.info(f"Starting {APIConfig.PROJECT_NAME} v{APIConfig.VERSION}")
    init_db()
    yield
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=APIConfig.PROJECT_NAME,
    description=APIConfig.DESCRIPTION,
    version=APIConfig.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
# app.include_router(api_router)
app.include_router(api_v1_router)


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    logger.info("Health check endpoint called")
    return {
        "message": "KVHS School Management System & CMS API is running",
        "version": APIConfig.VERSION,
        "status": "healthy",
    }


@app.get("/health", tags=["Health"])
def health_check_alias() -> dict[str, str]:
    """Standard health check alias."""
    return health_check()
