from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Enums for CMS
class UserRole(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STAFF = "staff"
    STUDENT = "student"


class ContentType(str, Enum):
    PAGE = "page"
    ANNOUNCEMENT = "announcement"
    POLICY = "policy"
    LESSON_PLAN = "lesson_plan"
    SYLLABUS = "syllabus"
    ASSIGNMENT = "assignment"
    COURSE_MATERIAL = "course_material"


class PublishStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"


class Student(Base):
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="student", cascade="all, delete-orphan"
    )


class Teacher(Base):
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    courses: Mapped[list["Course"]] = relationship(back_populates="teacher")
    contents: Mapped[list["Content"]] = relationship(back_populates="author")


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    course_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    credits: Mapped[int] = mapped_column(Integer)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="courses")
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )
    contents: Mapped[list["Content"]] = relationship(back_populates="course")
    documents: Mapped[list["Document"]] = relationship(back_populates="course")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        back_populates="course"
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    enrolled_date: Mapped[date] = mapped_column(Date)
    grade: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped["Student"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")


# Admin/Staff model for CMS management
class Admin(Base):
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contents: Mapped[list["Content"]] = relationship(back_populates="admin_author")


# Department model for content organization
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    contents: Mapped[list["Content"]] = relationship(back_populates="department")
    calendar_events: Mapped[list["CalendarEvent"]] = relationship(
        back_populates="department"
    )


# Content Tag model
class ContentTag(Base):
    __tablename__ = "content_tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


# Association table for Content and Tags (many-to-many)
class ContentTagAssociation(Base):
    __tablename__ = "content_tag_associations"

    content_id: Mapped[int] = mapped_column(ForeignKey("contents.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("content_tags.id"), primary_key=True)


# Main Content model for CMS
class Content(Base):
    __tablename__ = "contents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    slug: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    content_type: Mapped[str] = mapped_column(String(50), index=True)
    body: Mapped[str] = mapped_column(Text)
    template: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Publishing
    status: Mapped[str] = mapped_column(
        String(20), default=PublishStatus.DRAFT.value, index=True
    )
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Organization
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True, index=True
    )
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id"), nullable=True, index=True
    )

    # Author tracking (can be teacher or admin)
    author_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    author_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    department: Mapped["Department | None"] = relationship(back_populates="contents")
    course: Mapped["Course | None"] = relationship(back_populates="contents")
    author: Mapped["Teacher | None"] = relationship(back_populates="contents")
    admin_author: Mapped["Admin | None"] = relationship(back_populates="contents")

    # Hierarchical relationship
    parent: Mapped["Content | None"] = relationship(
        "Content", remote_side=[id], back_populates="children"
    )
    children: Mapped[list["Content"]] = relationship("Content", back_populates="parent")

    # Tags (many-to-many)
    tags: Mapped[list["ContentTag"]] = relationship(
        secondary="content_tag_associations", lazy="selectin"
    )

    # Documents
    documents: Mapped[list["Document"]] = relationship(
        back_populates="content", cascade="all, delete-orphan"
    )


# Document model for file attachments
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    filename: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(1000))
    file_size: Mapped[int] = mapped_column(Integer)
    mime_type: Mapped[str] = mapped_column(String(100))

    # Organization
    content_id: Mapped[int | None] = mapped_column(
        ForeignKey("contents.id"), nullable=True, index=True
    )
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )

    # Upload tracking
    uploaded_by_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    uploaded_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    content: Mapped["Content | None"] = relationship(back_populates="documents")
    course: Mapped["Course | None"] = relationship(back_populates="documents")


# Calendar Event model
class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(500), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[str] = mapped_column(
        String(50), index=True
    )  # exam, holiday, meeting, etc.

    # Date/Time
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)

    # Organization
    course_id: Mapped[int | None] = mapped_column(
        ForeignKey("courses.id"), nullable=True, index=True
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"), nullable=True, index=True
    )

    # Author tracking
    created_by_teacher_id: Mapped[int | None] = mapped_column(
        ForeignKey("teachers.id"), nullable=True, index=True
    )
    created_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admins.id"), nullable=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    course: Mapped["Course | None"] = relationship(back_populates="calendar_events")
    department: Mapped["Department | None"] = relationship(
        back_populates="calendar_events"
    )


# Attendance model for academic performance
class Attendance(Base):
    __tablename__ = "attendances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    status: Mapped[str] = mapped_column(String(20))  # present, absent, late, excused
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped["Student"] = relationship()
    course: Mapped["Course"] = relationship()


# Assignment Score model
class AssignmentScore(Base):
    __tablename__ = "assignment_scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    content_id: Mapped[int] = mapped_column(
        ForeignKey("contents.id"), index=True
    )  # Link to assignment content
    score: Mapped[float] = mapped_column()
    max_score: Mapped[float] = mapped_column()
    feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    graded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    student: Mapped["Student"] = relationship()
    assignment: Mapped["Content"] = relationship()
