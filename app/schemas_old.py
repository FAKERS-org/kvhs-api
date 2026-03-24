from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

EmailValue = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=255,
        pattern=r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$",
    ),
]


class StudentBase(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailValue
    grade_level: int = Field(..., ge=1, le=12)
    enrolled_date: date


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    student_id: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailValue | None = None
    grade_level: int | None = Field(default=None, ge=1, le=12)
    enrolled_date: date | None = None


class StudentRead(StudentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class TeacherBase(BaseModel):
    teacher_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailValue
    department: str = Field(..., min_length=1, max_length=255)
    hired_date: date


class TeacherCreate(TeacherBase):
    pass


class TeacherUpdate(BaseModel):
    teacher_id: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailValue | None = None
    department: str | None = Field(default=None, min_length=1, max_length=255)
    hired_date: date | None = None


class TeacherRead(TeacherBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CourseBase(BaseModel):
    course_code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    credits: int = Field(..., ge=1, le=10)
    teacher_id: int


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    course_code: str | None = Field(default=None, min_length=1, max_length=50)
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    credits: int | None = Field(default=None, ge=1, le=10)
    teacher_id: int | None = None


class CourseRead(CourseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    enrolled_date: date
    grade: str | None = Field(default=None, max_length=10)


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentRead(EnrollmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


# ==================== Authentication Schemas ====================


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: str | None = None
    role: str | None = None


class LoginRequest(BaseModel):
    email: EmailValue
    password: str = Field(..., min_length=6)


class RegisterAdmin(BaseModel):
    admin_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailValue
    password: str = Field(..., min_length=6)
    role: str = Field(default="admin")


class RegisterTeacher(BaseModel):
    teacher_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailValue
    department: str = Field(..., min_length=1, max_length=255)
    hired_date: date
    password: str = Field(..., min_length=6)


class RegisterStudent(BaseModel):
    student_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailValue
    grade_level: int = Field(..., ge=1, le=12)
    enrolled_date: date
    password: str = Field(..., min_length=6)


# ==================== CMS Schemas ====================


# Department Schemas
class DepartmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None


class DepartmentRead(DepartmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Content Tag Schemas
class ContentTagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class ContentTagCreate(ContentTagBase):
    pass


class ContentTagRead(ContentTagBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime


# Content Schemas
class ContentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    slug: str = Field(..., min_length=1, max_length=500)
    content_type: str = Field(..., min_length=1, max_length=50)
    body: str
    template: str | None = Field(default=None, max_length=100)
    status: str = Field(default="draft")
    department_id: int | None = None
    course_id: int | None = None
    parent_id: int | None = None


class ContentCreate(ContentBase):
    tag_ids: list[int] = Field(default_factory=list)


class ContentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    slug: str | None = Field(default=None, min_length=1, max_length=500)
    content_type: str | None = Field(default=None, min_length=1, max_length=50)
    body: str | None = None
    template: str | None = None
    status: str | None = None
    department_id: int | None = None
    course_id: int | None = None
    parent_id: int | None = None
    tag_ids: list[int] | None = None


class ContentRead(ContentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    author_teacher_id: int | None
    author_admin_id: int | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime
    tags: list[ContentTagRead] = []


# Document Schemas
class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    filename: str = Field(..., min_length=1, max_length=500)
    file_path: str = Field(..., min_length=1, max_length=1000)
    file_size: int
    mime_type: str = Field(..., min_length=1, max_length=100)
    content_id: int | None = None
    course_id: int | None = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    content_id: int | None = None
    course_id: int | None = None


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uploaded_by_teacher_id: int | None
    uploaded_by_admin_id: int | None
    created_at: datetime
    updated_at: datetime


# Calendar Event Schemas
class CalendarEventBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    description: str | None = None
    event_type: str = Field(..., min_length=1, max_length=50)
    start_date: datetime
    end_date: datetime
    all_day: bool = False
    course_id: int | None = None
    department_id: int | None = None


class CalendarEventCreate(CalendarEventBase):
    pass


class CalendarEventUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    event_type: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: datetime | None = None
    end_date: datetime | None = None
    all_day: bool | None = None
    course_id: int | None = None
    department_id: int | None = None


class CalendarEventRead(CalendarEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_by_teacher_id: int | None
    created_by_admin_id: int | None
    created_at: datetime
    updated_at: datetime


# Attendance Schemas
class AttendanceBase(BaseModel):
    student_id: int
    course_id: int
    date: date
    status: str = Field(..., min_length=1, max_length=20)
    notes: str | None = None


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: str | None = Field(default=None, min_length=1, max_length=20)
    notes: str | None = None


class AttendanceRead(AttendanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Assignment Score Schemas
class AssignmentScoreBase(BaseModel):
    student_id: int
    content_id: int
    score: float
    max_score: float
    feedback: str | None = None
    submitted_at: datetime | None = None
    graded_at: datetime | None = None


class AssignmentScoreCreate(AssignmentScoreBase):
    pass


class AssignmentScoreUpdate(BaseModel):
    score: float | None = None
    max_score: float | None = None
    feedback: str | None = None
    submitted_at: datetime | None = None
    graded_at: datetime | None = None


class AssignmentScoreRead(AssignmentScoreBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# Search Schema
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    content_type: str | None = None
    department_id: int | None = None
    tags: list[str] = Field(default_factory=list)
    status: str | None = None
