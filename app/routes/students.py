from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Student
from app.schemas import StudentCreate, StudentRead, StudentUpdate

router = APIRouter(prefix="/students", tags=["students"])


@router.get("", response_model=list[StudentRead])
def list_students(db: Session = Depends(get_db)) -> list[Student]:
    return db.query(Student).order_by(Student.id).all()


@router.post("", response_model=StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(payload: StudentCreate, db: Session = Depends(get_db)) -> Student:
    duplicate = (
        db.query(Student)
        .filter((Student.student_id == payload.student_id) | (Student.email == payload.email))
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with the same student_id or email already exists.",
        )

    student = Student(**payload.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")
    return student


@router.put("/{student_id}", response_model=StudentRead)
def update_student(
    student_id: int, payload: StudentUpdate, db: Session = Depends(get_db)
) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return student

    if "student_id" in updates or "email" in updates:
        query = db.query(Student).filter(Student.id != student_id)
        if "student_id" in updates and "email" in updates:
            duplicate = query.filter(
                (Student.student_id == updates["student_id"]) | (Student.email == updates["email"])
            ).first()
        elif "student_id" in updates:
            duplicate = query.filter(Student.student_id == updates["student_id"]).first()
        else:
            duplicate = query.filter(Student.email == updates["email"]).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student with the same student_id or email already exists.",
            )

    for field, value in updates.items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)) -> Response:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found.")

    db.delete(student)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
