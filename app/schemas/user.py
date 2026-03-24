"""
User-related schemas.
"""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.base import EmailStr


class StudentBase(BaseModel):
    """Shared student fields."""

    student_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    grade_level: int = Field(..., ge=1, le=12)
    enrolled_date: date


class StudentCreate(StudentBase):
    """Student creation schema."""


class StudentUpdate(BaseModel):
    """Student update schema."""

    student_id: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    grade_level: int | None = Field(default=None, ge=1, le=12)
    enrolled_date: date | None = None


class StudentRead(StudentBase):
    """Student response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class TeacherBase(BaseModel):
    """Shared teacher fields."""

    teacher_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    department: str = Field(..., min_length=1, max_length=255)
    hired_date: date


class TeacherCreate(TeacherBase):
    """Teacher creation schema."""


class TeacherUpdate(BaseModel):
    """Teacher update schema."""

    teacher_id: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = None
    department: str | None = Field(default=None, min_length=1, max_length=255)
    hired_date: date | None = None


class TeacherRead(TeacherBase):
    """Teacher response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
