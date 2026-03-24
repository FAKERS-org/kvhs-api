"""Central API router registration."""

from fastapi import APIRouter

from app.core.constants import APIConfig
from app.routes import (
    auth,
    calendar,
    cms_utils,
    content,
    courses,
    documents,
    enrollments,
    search,
    students,
    teachers,
)


def _include_all_routes(router: APIRouter) -> APIRouter:
    """Register all application routers on the provided API router."""
    router.include_router(students.router, tags=["Students"])
    router.include_router(teachers.router, tags=["Teachers"])
    router.include_router(courses.router, tags=["Courses"])
    router.include_router(enrollments.router, tags=["Enrollments"])
    router.include_router(auth.router, tags=["Authentication"])
    router.include_router(content.router, tags=["Content Management"])
    router.include_router(documents.router, tags=["Documents"])
    router.include_router(calendar.router, tags=["Calendar"])
    router.include_router(cms_utils.router, tags=["CMS Utilities"])
    router.include_router(search.router, tags=["Search"])
    return router


api_router = _include_all_routes(APIRouter())
api_v1_router = _include_all_routes(APIRouter(prefix=APIConfig.API_V1_PREFIX))
