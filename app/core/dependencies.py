"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.constants import ErrorMessages, UserRole
from app.core.exceptions import AuthenticationError, AuthorizationError
from app.core.security import decode_token
from app.db.session import get_db as db_generator
from app.services.auth import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency.
    Re-export from database module for convenience.
    """
    yield from db_generator()


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> dict:
    """Get the current authenticated user from JWT token."""
    payload = decode_token(token)
    if payload is None:
        raise AuthenticationError(ErrorMessages.UNAUTHORIZED)

    email: str | None = payload.get("sub")
    role: str | None = payload.get("role")

    if email is None or role is None:
        raise AuthenticationError(ErrorMessages.UNAUTHORIZED)

    user = AuthService(db).get_user_by_email(email=email, role=role)

    if user is None or not user.is_active:
        raise AuthenticationError(ErrorMessages.UNAUTHORIZED)

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "user_model": user,
    }


async def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Ensure the user is active."""
    return current_user


def require_role(allowed_roles: list[str]):
    """Dependency to check if user has required role."""

    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise AuthorizationError(ErrorMessages.FORBIDDEN)
        return current_user

    return role_checker


# Convenience dependencies
async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role."""
    if current_user["role"] != UserRole.ADMIN.value:
        raise AuthorizationError("Admin access required")
    return current_user


async def require_teacher_or_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Require teacher or admin role."""
    if current_user["role"] not in [UserRole.TEACHER.value, UserRole.ADMIN.value]:
        raise AuthorizationError("Teacher or admin access required")
    return current_user


async def require_staff_or_admin(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Require staff or admin role."""
    if current_user["role"] not in [UserRole.STAFF.value, UserRole.ADMIN.value]:
        raise AuthorizationError("Staff or admin access required")
    return current_user
