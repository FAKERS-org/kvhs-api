"""Authentication service with business logic."""

from sqlalchemy.orm import Session

from app.core.constants import ErrorMessages, UserRole
from app.core.exceptions import AuthenticationError, ConflictError
from app.core.logging_config import log_auth_attempt
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
)
from app.models import Admin, Student, Teacher
from app.repositories.user import AdminRepository, StudentRepository, TeacherRepository
from app.schemas import RegisterAdmin, RegisterStudent, RegisterTeacher, Token


class AuthService:
    """Authentication service."""

    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.teacher_repo = TeacherRepository(db)
        self.admin_repo = AdminRepository(db)

    def register_admin(self, data: RegisterAdmin) -> dict:
        """Register a new admin user."""
        # Check if email exists
        if self.admin_repo.get_by_email(data.email):
            raise ConflictError(ErrorMessages.EMAIL_EXISTS)

        # Check if admin_id exists
        if self.admin_repo.get_by_admin_id(data.admin_id):
            raise ConflictError(ErrorMessages.ADMIN_ID_EXISTS)

        # Create admin
        admin_data = {
            "admin_id": data.admin_id,
            "name": data.name,
            "email": data.email,
            "hashed_password": get_password_hash(data.password),
            "role": data.role
            if data.role in [UserRole.ADMIN.value, UserRole.STAFF.value]
            else UserRole.ADMIN.value,
            "is_active": True,
        }

        admin = self.admin_repo.create(admin_data)

        return {
            "message": f"Admin {admin.name} registered successfully",
            "admin_id": admin.admin_id,
            "email": admin.email,
        }

    def register_teacher(self, data: RegisterTeacher) -> dict:
        """Register a new teacher user."""
        # Check if email exists
        if self.teacher_repo.get_by_email(data.email):
            raise ConflictError(ErrorMessages.EMAIL_EXISTS)

        # Check if teacher_id exists
        if self.teacher_repo.get_by_teacher_id(data.teacher_id):
            raise ConflictError(ErrorMessages.TEACHER_ID_EXISTS)

        # Create teacher
        teacher_data = {
            "teacher_id": data.teacher_id,
            "name": data.name,
            "email": data.email,
            "department": data.department,
            "hired_date": data.hired_date,
            "hashed_password": get_password_hash(data.password),
            "role": UserRole.TEACHER.value,
            "is_active": True,
        }

        teacher = self.teacher_repo.create(teacher_data)

        return {
            "message": f"Teacher {teacher.name} registered successfully",
            "teacher_id": teacher.teacher_id,
            "email": teacher.email,
        }

    def register_student(self, data: RegisterStudent) -> dict:
        """Register a new student user."""
        # Check if email exists
        if self.student_repo.get_by_email(data.email):
            raise ConflictError(ErrorMessages.EMAIL_EXISTS)

        # Check if student_id exists
        if self.student_repo.get_by_student_id(data.student_id):
            raise ConflictError(ErrorMessages.STUDENT_ID_EXISTS)

        # Create student
        student_data = {
            "student_id": data.student_id,
            "name": data.name,
            "email": data.email,
            "grade_level": data.grade_level,
            "enrolled_date": data.enrolled_date,
            "hashed_password": get_password_hash(data.password),
            "role": UserRole.STUDENT.value,
            "is_active": True,
        }

        student = self.student_repo.create(student_data)

        return {
            "message": f"Student {student.name} registered successfully",
            "student_id": student.student_id,
            "email": student.email,
        }

    def login(self, email: str, password: str) -> Token:
        """Login user and return tokens."""
        user = self.get_user_by_email(email)

        # Verify credentials
        if not user or not user.hashed_password or not verify_password(
            password, user.hashed_password
        ):
            log_auth_attempt(email, False, "Invalid credentials")
            raise AuthenticationError(ErrorMessages.INVALID_CREDENTIALS)

        if not user.is_active:
            log_auth_attempt(email, False, "Inactive account")
            raise AuthenticationError(ErrorMessages.INACTIVE_USER)

        # Create tokens
        access_token = create_access_token(data={"sub": user.email, "role": user.role})
        refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role})

        log_auth_attempt(email, True)

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )

    def get_user_by_email(
        self, email: str, role: str | None = None
    ) -> Student | Teacher | Admin | None:
        """Get user by email, optionally constrained to a specific role."""
        if role is None:
            for repository in (
                self.admin_repo,
                self.teacher_repo,
                self.student_repo,
            ):
                user = repository.get_by_email(email)
                if user:
                    return user
            return None

        if role == UserRole.STUDENT.value:
            return self.student_repo.get_by_email(email)
        if role == UserRole.TEACHER.value:
            return self.teacher_repo.get_by_email(email)
        if role in [UserRole.ADMIN.value, UserRole.STAFF.value]:
            return self.admin_repo.get_by_email(email)
        return None
