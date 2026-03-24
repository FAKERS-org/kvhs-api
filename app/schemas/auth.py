"""
Authentication schemas.
"""

from datetime import date

from pydantic import BaseModel, Field

from app.schemas.base import EmailStr


# Token schemas
class Token(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data."""

    email: str | None = None
    role: str | None = None


# Login schema
class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(..., min_length=6)


# Registration schemas
class RegisterAdmin(BaseModel):
    """Admin registration schema."""

    admin_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field(default="admin")


class RegisterTeacher(BaseModel):
    """Teacher registration schema."""

    teacher_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=255)
    hired_date: date
    password: str = Field(..., min_length=6, max_length=100)


class RegisterStudent(BaseModel):
    """Student registration schema."""

    student_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    grade_level: int = Field(..., ge=1, le=12)
    enrolled_date: date
    password: str = Field(..., min_length=6, max_length=100)


# User info schema
class UserInfo(BaseModel):
    """User information response."""

    id: int
    email: str
    name: str
    role: str
    is_active: bool
