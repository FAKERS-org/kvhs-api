"""
Academic-related schemas.
"""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class CourseBase(BaseModel):
    """Shared course fields."""

    course_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    credits: int = Field(..., ge=1, le=10)
    teacher_id: int


class CourseCreate(CourseBase):
    """Course creation schema."""


class CourseUpdate(BaseModel):
    """Course update schema."""

    course_code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    credits: int | None = Field(default=None, ge=1, le=10)
    teacher_id: int | None = None


class CourseRead(CourseBase):
    """Course response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class EnrollmentBase(BaseModel):
    """Shared enrollment fields."""

    student_id: int
    course_id: int
    enrolled_date: date
    grade: str | None = Field(default=None, max_length=10)


class EnrollmentCreate(EnrollmentBase):
    """Enrollment creation schema."""


class EnrollmentRead(EnrollmentBase):
    """Enrollment response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int


class AttendanceBase(BaseModel):
    """Shared attendance fields."""

    student_id: int
    course_id: int
    date: date
    status: str = Field(..., min_length=1, max_length=20)
    notes: str | None = None


class AttendanceCreate(AttendanceBase):
    """Attendance creation schema."""


class AttendanceUpdate(BaseModel):
    """Attendance update schema."""

    status: str | None = Field(default=None, min_length=1, max_length=20)
    notes: str | None = None


class AttendanceRead(AttendanceBase):
    """Attendance response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AssignmentScoreBase(BaseModel):
    """Shared assignment score fields."""

    student_id: int
    content_id: int
    score: float
    max_score: float
    feedback: str | None = None
    submitted_at: datetime | None = None
    graded_at: datetime | None = None


class AssignmentScoreCreate(AssignmentScoreBase):
    """Assignment score creation schema."""


class AssignmentScoreUpdate(BaseModel):
    """Assignment score update schema."""

    score: float | None = None
    max_score: float | None = None
    feedback: str | None = None
    submitted_at: datetime | None = None
    graded_at: datetime | None = None


class AssignmentScoreRead(AssignmentScoreBase):
    """Assignment score response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
