"""
Schemas package - exports all Pydantic schemas.
"""

from app.schemas.base import (
    BaseResponse,
    EmailStr,
    PaginatedResponse,
    PaginationParams,
    TimestampSchema,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterAdmin,
    RegisterStudent,
    RegisterTeacher,
    Token,
    TokenData,
    UserInfo,
)
from app.schemas.academic import (
    AssignmentScoreBase,
    AssignmentScoreCreate,
    AssignmentScoreRead,
    AssignmentScoreUpdate,
    AttendanceBase,
    AttendanceCreate,
    AttendanceRead,
    AttendanceUpdate,
    CourseBase,
    CourseCreate,
    CourseRead,
    CourseUpdate,
    EnrollmentBase,
    EnrollmentCreate,
    EnrollmentRead,
)
from app.schemas.cms import (
    CalendarEventBase,
    CalendarEventCreate,
    CalendarEventRead,
    CalendarEventUpdate,
    ContentBase,
    ContentCreate,
    ContentRead,
    ContentTagBase,
    ContentTagCreate,
    ContentTagRead,
    ContentUpdate,
    DepartmentBase,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    DocumentBase,
    DocumentCreate,
    DocumentRead,
    DocumentUpdate,
)
from app.schemas.search import SearchRequest
from app.schemas.user import (
    StudentBase,
    StudentCreate,
    StudentRead,
    StudentUpdate,
    TeacherBase,
    TeacherCreate,
    TeacherRead,
    TeacherUpdate,
)

__all__ = [
    # Base
    "BaseResponse",
    "EmailStr",
    "TimestampSchema",
    "PaginationParams",
    "PaginatedResponse",
    # Auth
    "Token",
    "TokenData",
    "LoginRequest",
    "RegisterAdmin",
    "RegisterTeacher",
    "RegisterStudent",
    "UserInfo",
    # Student
    "StudentBase",
    "StudentCreate",
    "StudentUpdate",
    "StudentRead",
    # Teacher
    "TeacherBase",
    "TeacherCreate",
    "TeacherUpdate",
    "TeacherRead",
    # Course
    "CourseBase",
    "CourseCreate",
    "CourseUpdate",
    "CourseRead",
    # Enrollment
    "EnrollmentBase",
    "EnrollmentCreate",
    "EnrollmentRead",
    # Content
    "ContentBase",
    "ContentCreate",
    "ContentUpdate",
    "ContentRead",
    # Document
    "DocumentBase",
    "DocumentCreate",
    "DocumentUpdate",
    "DocumentRead",
    # Calendar
    "CalendarEventBase",
    "CalendarEventCreate",
    "CalendarEventUpdate",
    "CalendarEventRead",
    # Department
    "DepartmentBase",
    "DepartmentCreate",
    "DepartmentUpdate",
    "DepartmentRead",
    # Tag
    "ContentTagBase",
    "ContentTagCreate",
    "ContentTagRead",
    # Attendance
    "AttendanceBase",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceRead",
    # Assignment Score
    "AssignmentScoreBase",
    "AssignmentScoreCreate",
    "AssignmentScoreUpdate",
    "AssignmentScoreRead",
    # Search
    "SearchRequest",
]
