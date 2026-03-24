"""
Request logging middleware.
"""

import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging_config import log_request


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            duration = (time.perf_counter() - start_time) * 1000
            log_request(
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration=duration,
            )
            raise

        duration = (time.perf_counter() - start_time) * 1000
        log_request(
            method=request.method,
            path=request.url.path,
            status_code=status_code,
            duration=duration,
        )
        response.headers["X-Process-Time"] = f"{duration:.2f}ms"
        return response
