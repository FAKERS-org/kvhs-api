from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Teacher
from app.schemas import TeacherCreate, TeacherRead, TeacherUpdate

router = APIRouter(prefix="/teachers", tags=["teachers"])


@router.get("", response_model=list[TeacherRead])
def list_teachers(db: Session = Depends(get_db)) -> list[Teacher]:
    return db.query(Teacher).order_by(Teacher.id).all()


@router.post("", response_model=TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(payload: TeacherCreate, db: Session = Depends(get_db)) -> Teacher:
    duplicate = (
        db.query(Teacher)
        .filter((Teacher.teacher_id == payload.teacher_id) | (Teacher.email == payload.email))
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher with the same teacher_id or email already exists.",
        )

    teacher = Teacher(**payload.model_dump())
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


@router.get("/{teacher_id}", response_model=TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)) -> Teacher:
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")
    return teacher


@router.put("/{teacher_id}", response_model=TeacherRead)
def update_teacher(
    teacher_id: int, payload: TeacherUpdate, db: Session = Depends(get_db)
) -> Teacher:
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return teacher

    if "teacher_id" in updates or "email" in updates:
        query = db.query(Teacher).filter(Teacher.id != teacher_id)
        if "teacher_id" in updates and "email" in updates:
            duplicate = query.filter(
                (Teacher.teacher_id == updates["teacher_id"]) | (Teacher.email == updates["email"])
            ).first()
        elif "teacher_id" in updates:
            duplicate = query.filter(Teacher.teacher_id == updates["teacher_id"]).first()
        else:
            duplicate = query.filter(Teacher.email == updates["email"]).first()

        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Teacher with the same teacher_id or email already exists.",
            )

    for field, value in updates.items():
        setattr(teacher, field, value)

    db.commit()
    db.refresh(teacher)
    return teacher


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)) -> Response:
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found.")

    db.delete(teacher)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
