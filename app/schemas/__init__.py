"""
Schemas package - exports all Pydantic schemas.
"""

# Re-export from base
from app.schemas.base import (
    BaseResponse,
    EmailStr,
    PaginatedResponse,
    PaginationParams,
    TimestampSchema,
)

# Re-export from auth
from app.schemas.auth import (
    LoginRequest,
    RegisterAdmin,
    RegisterStudent,
    RegisterTeacher,
    Token,
    TokenData,
    UserInfo,
)

# Import all schemas from old schemas.py temporarily
# This allows gradual migration
from app.schemas_old import (
    AssignmentScoreBase,
    AssignmentScoreCreate,
    AssignmentScoreRead,
    AssignmentScoreUpdate,
    AttendanceBase,
    AttendanceCreate,
    AttendanceRead,
    AttendanceUpdate,
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
    CourseBase,
    CourseCreate,
    CourseRead,
    CourseUpdate,
    DepartmentBase,
    DepartmentCreate,
    DepartmentRead,
    DepartmentUpdate,
    DocumentBase,
    DocumentCreate,
    DocumentRead,
    DocumentUpdate,
    EnrollmentBase,
    EnrollmentCreate,
    EnrollmentRead,
    SearchRequest,
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
