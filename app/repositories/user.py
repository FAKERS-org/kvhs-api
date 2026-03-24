"""
User repositories (Student, Teacher, Admin).
"""

from sqlalchemy.orm import Session

from app.models import Admin, Student, Teacher
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    """Repository for Student model."""

    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_email(self, email: str) -> Student | None:
        """Get student by email."""
        return self.get_by_field("email", email)

    def get_by_student_id(self, student_id: str) -> Student | None:
        """Get student by student_id."""
        return self.get_by_field("student_id", student_id)

    def get_by_grade(
        self, grade_level: int, skip: int = 0, limit: int = 100
    ) -> list[Student]:
        """Get students by grade level."""
        return self.get_multi_by_field("grade_level", grade_level, skip, limit)


class TeacherRepository(BaseRepository[Teacher]):
    """Repository for Teacher model."""

    def __init__(self, db: Session):
        super().__init__(Teacher, db)

    def get_by_email(self, email: str) -> Teacher | None:
        """Get teacher by email."""
        return self.get_by_field("email", email)

    def get_by_teacher_id(self, teacher_id: str) -> Teacher | None:
        """Get teacher by teacher_id."""
        return self.get_by_field("teacher_id", teacher_id)

    def get_by_department(
        self, department: str, skip: int = 0, limit: int = 100
    ) -> list[Teacher]:
        """Get teachers by department."""
        return self.get_multi_by_field("department", department, skip, limit)


class AdminRepository(BaseRepository[Admin]):
    """Repository for Admin model."""

    def __init__(self, db: Session):
        super().__init__(Admin, db)

    def get_by_email(self, email: str) -> Admin | None:
        """Get admin by email."""
        return self.get_by_field("email", email)

    def get_by_admin_id(self, admin_id: str) -> Admin | None:
        """Get admin by admin_id."""
        return self.get_by_field("admin_id", admin_id)
