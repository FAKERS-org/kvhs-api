"""Central API router registration."""

from fastapi import APIRouter

from app.core.constants import APIConfig
from app.routes import (
    auth,
    courses,
    enrollments,
    students,
    teachers,
    content,
    documents,
    calendar,
    cms_utils,
    search,
)


def _include_all_routes(router: APIRouter) -> APIRouter:
    """Register all application routers on the provided API router."""
    router.include_router(students.router)
    router.include_router(teachers.router)
    router.include_router(courses.router)
    router.include_router(enrollments.router)
    router.include_router(auth.router)
    router.include_router(content.router)
    router.include_router(documents.router)
    router.include_router(calendar.router)
    router.include_router(cms_utils.router)
    router.include_router(search.router)
    return router


api_router = _include_all_routes(APIRouter())
api_v1_router = _include_all_routes(APIRouter(prefix=APIConfig.API_V1_PREFIX))
