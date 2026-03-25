from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.dependencies import (
    check_admin_registration_allowed,
    get_current_active_user,
    get_db,
    require_staff_or_admin,
)
from app.schemas import (
    LoginRequest,
    RegisterAdmin,
    RegisterStudent,
    RegisterTeacher,
    Token,
    UserInfo,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register/admin", response_model=dict, status_code=status.HTTP_201_CREATED
)
def register_admin(
    admin_data: RegisterAdmin,
    db: Session = Depends(get_db),
    current_user: dict | None = Depends(check_admin_registration_allowed),
):
    """Register a new admin user. Only allowed if no admins exist or if current user is admin."""
    return AuthService(db).register_admin(admin_data)


@router.post(
    "/register/teacher", response_model=dict, status_code=status.HTTP_201_CREATED
)
def register_teacher(
    teacher_data: RegisterTeacher,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_staff_or_admin),
):
    """Register a new teacher user. Only allowed for admins or staff."""
    return AuthService(db).register_teacher(teacher_data)


@router.post(
    "/register/student", response_model=dict, status_code=status.HTTP_201_CREATED
)
def register_student(
    student_data: RegisterStudent,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_staff_or_admin),
):
    """Register a new student user. Only allowed for admins or staff."""
    return AuthService(db).register_student(student_data)


@router.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint for all users."""
    return AuthService(db).login(login_data.email, login_data.password)


@router.post("/token", response_model=Token)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """OAuth2 compatible token login (for Swagger UI)."""
    return AuthService(db).login(form_data.username, form_data.password)


@router.get("/me", response_model=UserInfo)
def get_me(current_user: dict = Depends(get_current_active_user)):
    """Get the authenticated user's profile."""
    return UserInfo(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        is_active=current_user["user_model"].is_active,
    )
