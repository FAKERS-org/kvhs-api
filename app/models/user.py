"""
User-related models (Student, Teacher, Admin).
"""

from datetime import date

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import UserRole
from app.models.base import Base, TimestampMixin


class Student(Base, TimestampMixin):
    """Student model."""

    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    grade_level: Mapped[int] = mapped_column(Integer)
    enrolled_date: Mapped[date] = mapped_column(Date)

    # Authentication fields
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.STUDENT.value, nullable=False
    )

    # Relationships
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Teacher(Base, TimestampMixin):
    """Teacher model."""

    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    teacher_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    department: Mapped[str] = mapped_column(String(255), index=True)
    hired_date: Mapped[date] = mapped_column(Date)

    # Authentication fields
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.TEACHER.value, nullable=False
    )

    # Relationships
    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")
    # CMS contents relationship now handled via MongoDB IDs


class Admin(Base, TimestampMixin):
    """Admin/Staff model for CMS management."""

    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    admin_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), default=UserRole.ADMIN.value, nullable=False
    )

    # CMS contents relationship now handled via MongoDB IDs
