"""
Academic models (Course, Enrollment, Attendance, AssignmentScore).
"""

from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Course(Base, TimestampMixin):
    """Course model."""

    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    credits: Mapped[int] = mapped_column(Integer)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), index=True)

    # Relationships
    teacher: Mapped["Teacher"] = relationship(back_populates="courses")
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    contents: Mapped[list["Content"]] = relationship(back_populates="course")
    documents: Mapped[list["Document"]] = relationship(back_populates="course")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        back_populates="course"
    )


class Enrollment(Base, TimestampMixin):
    """Enrollment model (Student-Course relationship)."""

    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    enrolled_date: Mapped[date] = mapped_column(Date)
    grade: Mapped[str | None] = mapped_column(String(10), nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")


class Attendance(Base, TimestampMixin):
    """Attendance tracking model."""

    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20))  # present, absent, late, excused
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship()
    course: Mapped["Course"] = relationship()


class AssignmentScore(Base, TimestampMixin):
    """Assignment score tracking model."""

    __tablename__ = "assignment_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), index=True)
    score: Mapped[float] = mapped_column()
    max_score: Mapped[float] = mapped_column()
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    graded_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    student: Mapped["Student"] = relationship()
    assignment: Mapped["Content"] = relationship()
