"""
Constants and enums used throughout the application.
"""

from enum import Enum


class UserRole(str, Enum):
    """User roles in the system."""

    ADMIN = "admin"
    TEACHER = "teacher"
    STAFF = "staff"
    STUDENT = "student"


class ContentType(str, Enum):
    """Types of content in the CMS."""

    PAGE = "page"
    ANNOUNCEMENT = "announcement"
    POLICY = "policy"
    LESSON_PLAN = "lesson_plan"
    SYLLABUS = "syllabus"
    ASSIGNMENT = "assignment"
    COURSE_MATERIAL = "course_material"


class PublishStatus(str, Enum):
    """Publishing status for content."""

    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"


class AttendanceStatus(str, Enum):
    """Attendance status options."""

    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    EXCUSED = "excused"


class EventType(str, Enum):
    """Calendar event types."""

    EXAM = "exam"
    HOLIDAY = "holiday"
    MEETING = "meeting"
    SCHOOL_EVENT = "school_event"
    SPORTS = "sports"
    CULTURAL = "cultural"
    PARENT_TEACHER = "parent_teacher"


# API Constants
class APIConfig:
    """API configuration constants."""

    API_V1_PREFIX = "/api/v1"
    PROJECT_NAME = "KVHS School Management & CMS API"
    VERSION = "2.0.0"
    DESCRIPTION = "Comprehensive API for managing students, teachers, courses, enrollments, and CMS content."


# Pagination
class PaginationConfig:
    """Pagination defaults."""

    DEFAULT_SKIP = 0
    DEFAULT_LIMIT = 100
    MAX_LIMIT = 1000


# File Upload
class FileConfig:
    """File upload configuration."""

    ALLOWED_EXTENSIONS = {
        "pdf",
        "doc",
        "docx",
        "xls",
        "xlsx",
        "ppt",
        "pptx",
        "txt",
        "csv",
        "jpg",
        "jpeg",
        "png",
        "gif",
        "zip",
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# Validation
class ValidationConfig:
    """Validation constraints."""

    MIN_PASSWORD_LENGTH = 6
    MAX_PASSWORD_LENGTH = 100
    MIN_NAME_LENGTH = 1
    MAX_NAME_LENGTH = 255
    MIN_EMAIL_LENGTH = 3
    MAX_EMAIL_LENGTH = 255
    MIN_GRADE_LEVEL = 1
    MAX_GRADE_LEVEL = 12
    MIN_CREDITS = 1
    MAX_CREDITS = 10


# Error Messages
class ErrorMessages:
    """Common error messages."""

    # Authentication
    INVALID_CREDENTIALS = "Incorrect email or password"
    INACTIVE_USER = "Inactive user account"
    UNAUTHORIZED = "Could not validate credentials"
    FORBIDDEN = "Not enough permissions"

    # Not Found
    USER_NOT_FOUND = "User not found"
    CONTENT_NOT_FOUND = "Content not found"
    DOCUMENT_NOT_FOUND = "Document not found"
    EVENT_NOT_FOUND = "Event not found"
    DEPARTMENT_NOT_FOUND = "Department not found"
    TAG_NOT_FOUND = "Tag not found"
    STUDENT_NOT_FOUND = "Student not found"
    TEACHER_NOT_FOUND = "Teacher not found"
    COURSE_NOT_FOUND = "Course not found"
    ENROLLMENT_NOT_FOUND = "Enrollment not found"

    # Conflict
    EMAIL_EXISTS = "Email already registered"
    SLUG_EXISTS = "Slug already exists"
    STUDENT_ID_EXISTS = "Student ID already exists"
    TEACHER_ID_EXISTS = "Teacher ID already exists"
    ADMIN_ID_EXISTS = "Admin ID already exists"
    COURSE_CODE_EXISTS = "Course code already exists"
    DEPARTMENT_EXISTS = "Department name already exists"
    TAG_EXISTS = "Tag name already exists"
    ENROLLMENT_EXISTS = "Student already enrolled in this course"

    # Validation
    INVALID_DATE_RANGE = "End date must be after start date"
    ACCESS_DENIED_UNPUBLISHED = "Access denied to unpublished content"
    NOT_CONTENT_OWNER = "Not authorized to modify this content"


# Success Messages
class SuccessMessages:
    """Common success messages."""

    REGISTERED_SUCCESS = "{} registered successfully"
    CREATED_SUCCESS = "{} created successfully"
    UPDATED_SUCCESS = "{} updated successfully"
    DELETED_SUCCESS = "{} deleted successfully"
    PUBLISHED_SUCCESS = "Content published successfully"
    UNPUBLISHED_SUCCESS = "Content unpublished successfully"
