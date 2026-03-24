# Code Refactoring Documentation

## Overview

The KVHS API codebase has been refactored to follow industry best practices with clean architecture, proper separation of concerns, and modular design. This document explains the new structure and how to work with it.

## New Project Structure

```
kvhs-api/
├── app/
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (Pydantic Settings)
│   │   ├── constants.py           # Constants and Enums -> NEW
│   │   ├── dependencies.py        # Auth dependencies (refactored)
│   │   ├── exceptions.py          # Custom exceptions -> NEW
│   │   ├── exception_handlers.py  # Exception handlers -> NEW
│   │   ├── logging_config.py      # Logging setup -> NEW
│   │   ├── middleware.py          # Request logging middleware -> NEW
│   │   └── security.py            # JWT & password hashing
│   │
│   ├── models/                    # Database models (modular) -> REFACTORED
│   │   ├── __init__.py
│   │   ├── base.py                # Base model & TimestampMixin
│   │   ├── user.py                # Student, Teacher, Admin
│   │   ├── academic.py            # Course, Enrollment, Attendance, AssignmentScore
│   │   └── cms.py                 # Content, Document, Calendar, Department, Tag
│   │
│   ├── schemas/                   # Pydantic schemas (modular) -> REFACTORED
│   │   ├── __init__.py
│   │   ├── base.py                # Base schemas & EmailStr type
│   │   └── auth.py                # Auth schemas
│   │   └── (schemas_old.py)       # Temporary backward compatibility
│   │
│   ├── repositories/              # Data access layer -> NEW
│   │   ├── __init__.py
│   │   ├── base.py                # Base repository with CRUD
│   │   ├── user.py                # User repositories
│   │   └── content.py             # Content repository
│   │
│   ├── services/                  # Business logic layer -> NEW
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication service
│   │   └── content.py             # Content management service
│   │
│   ├── routes/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── content.py
│   │   ├── documents.py
│   │   ├── calendar.py
│   │   ├── cms_utils.py
│   │   ├── search.py
│   │   ├── students.py
│   │   ├── teachers.py
│   │   ├── courses.py
│   │   └── enrollments.py
│   │
│   ├── utils/                     # Utility functions -> NEW
│   │   ├── __init__.py
│   │   └── helpers.py             # Helper functions
│   │
│   ├── database.py                # Database config (enhanced)
│   ├── main.py                    # FastAPI app (refactored)
│   └── (models.py - DEPRECATED)   # Old monolithic models
│   └── (schemas.py - DEPRECATED)  # Old monolithic schemas
│
├── logs/                          # Log files -> NEW
│   ├── app.log
│   └── error.log
│
├── .env.example
├── pyproject.toml
└── README files...
```

## Architecture Layers

### 1. Core Layer (`app/core/`)

**Purpose**: Foundation components used throughout the application

#### Key Files:

- **constants.py**: All constants, enums, and error messages

  ```python
  from app.core.constants import UserRole, ContentType, ErrorMessages
  ```

- **exceptions.py**: Custom exception classes

  ```python
  from app.core.exceptions import NotFoundError, AuthorizationError

  raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)
  ```

- **exception_handlers.py**: Global exception handlers for FastAPI
  - Handles custom exceptions
  - Validation errors
  - Database errors
  - Generic exceptions

- **logging_config.py**: Centralized logging configuration

  ```python
  from app.core.logging_config import logger

  logger.info("Operation completed")
  logger.error("Error occurred", exc_info=True)
  ```

- **middleware.py**: Request logging middleware
  - Logs all HTTP requests
  - Adds process time header

### 2. Models Layer (`app/models/`)

**Purpose**: Database models split into logical modules

#### Structure:

- **base.py**: `Base` class and `TimestampMixin`
- **user.py**: Student, Teacher, Admin models
- **academic.py**: Course, Enrollment, Attendance, AssignmentScore
- **cms.py**: Content, Document, Calendar, Department, Tag

#### Usage:

```python
from app.models import Student, Content, Course
# All models imported from __init__.py
```

### 3. Schemas Layer (`app/schemas/`)

**Purpose**: Request/response validation with Pydantic

#### Structure:

- **base.py**: Base schemas, EmailStr type, pagination
- **auth.py**: Authentication schemas
- **schemas_old.py**: Backward compatibility (temporary)

#### Usage:

```python
from app.schemas import StudentCreate, ContentRead, EmailStr
```

### 4. Repository Layer (`app/repositories/`) -> NEW

**Purpose**: Data access layer - all database queries

#### Benefits:

- Centralized database access
- Reusable query methods
- Easier testing (can mock repositories)
- DRY principle

#### Base Repository:

```python
class BaseRepository(Generic[ModelType]):
    def get(self, id: int) -> ModelType | None
    def get_multi(self, skip: int, limit: int) -> list[ModelType]
    def create(self, obj_in: dict) -> ModelType
    def update(self, db_obj: ModelType, obj_in: dict) -> ModelType
    def delete(self, db_obj: ModelType) -> None
    # ... more methods
```

#### Custom Repositories:

```python
from app.repositories import StudentRepository, ContentRepository

# In your route/service:
student_repo = StudentRepository(db)
student = student_repo.get_by_email("student@example.com")
```

### 5. Service Layer (`app/services/`) -> NEW

**Purpose**: Business logic layer

#### Benefits:

- Separates business logic from routes
- Reusable across different routes
- Easier to test
- Better error handling

#### Usage Example:

```python
from app.services import AuthService, ContentService

# Authentication
auth_service = AuthService(db)
tokens = auth_service.login(email, password)

# Content management
content_service = ContentService(db)
content = content_service.create_content(data, user_id, user_role)
```

### 6. Routes Layer (`app/routes/`)

**Purpose**: API endpoints - thin controllers

Routes should be thin and delegate to services:

```python
@router.post("/content/", response_model=ContentRead)
def create_content(
    data: ContentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_teacher_or_admin)
):
    service = ContentService(db)
    return service.create_content(data, current_user["id"], current_user["role"])
```

### 7. Utils Layer (`app/utils/`) -> NEW

**Purpose**: Helper functions and utilities

```python
from app.utils import slugify, format_file_size, sanitize_filename

slug = slugify("My Content Title")  # "my-content-title"
size = format_file_size(1536)       # "1.5 KB"
```

## Key Improvements

### 1. Exception Handling

**Before**:

```python
if not user:
    raise HTTPException(status_code=404, detail="User not found")
```

**After**:

```python
from app.core.exceptions import NotFoundError
from app.core.constants import ErrorMessages

if not user:
    raise NotFoundError(ErrorMessages.USER_NOT_FOUND)
```

### 2. Logging

**Before**: No structured logging

**After**:

```python
from app.core.logging_config import logger

logger.info("User logged in", extra={"email": user.email})
logger.error("Failed to create content", exc_info=True)
```

### 3. Constants

**Before**: Magic strings everywhere

```python
if user.role == "admin":  # What if typo?
```

**After**:

```python
from app.core.constants import UserRole

if user.role == UserRole.ADMIN.value:  # Type-safe!
```

### 4. Repository Pattern

**Before**: Direct database queries in routes

```python
@router.get("/students/")
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()
```

**After**: Repository abstraction

```python
@router.get("/students/")
def get_students(db: Session = Depends(get_db)):
    repo = StudentRepository(db)
    return repo.get_multi()
```

### 5. Service Layer

**Before**: Business logic in routes

```python
@router.post("/content/")
def create_content(data: ContentCreate, db: Session = Depends(get_db)):
    # 50 lines of business logic here
    if self.content_repo.get_by_slug(data.slug):
        raise HTTPException(...)
    # More logic...
```

**After**: Clean routes with service layer

```python
@router.post("/content/")
def create_content(data: ContentCreate, db: Session = Depends(get_db)):
    service = ContentService(db)
    return service.create_content(data, user_id, user_role)
```

## Migration Guide

### For Existing Routes

1. **Import from new locations**:

   ```python
   # Old
   from app.models import Student, UserRole

   # New
   from app.models import Student
   from app.core.constants import UserRole
   ```

2. **Use custom exceptions**:

   ```python
   # Old
   raise HTTPException(status_code=404, detail="Not found")

   # New
   from app.core.exceptions import NotFoundError
   raise NotFoundError("Resource not found")
   ```

3. **Use services** (gradually):

   ```python
   # Instead of direct DB queries, use services
   from app.services import ContentService

   service = ContentService(db)
   content = service.get_content(content_id, user_role)
   ```

### Creating New Features

1. **Define constants** in `app/core/constants.py`
2. **Create model** in appropriate file in `app/models/`
3. **Create schemas** in `app/schemas/`
4. **Create repository** in `app/repositories/`
5. **Create service** in `app/services/`
6. **Create routes** in `app/routes/`

## Benefits of Refactoring

1. **Separation of Concerns**: Each layer has a single responsibility
2. **Testability**: Easy to unit test services and repositories
3. **Maintainability**: Changes in one layer don't affect others
4. **Reusability**: Services and repositories can be reused
5. **Error Handling**: Consistent error handling across the app
6. **Logging**: Centralized logging for debugging
7. **Type Safety**: Using enums instead of strings
8. **Documentation**: Self-documenting code structure

## Best Practices

### 1. Always use constants

```python
# Bad
if status == "published":

# Good
from app.core.constants import PublishStatus
if status == PublishStatus.PUBLISHED.value:
```

### 2. Use custom exceptions

```python
# Bad
raise HTTPException(status_code=404, detail="Not found")

# Good
from app.core.exceptions import NotFoundError
from app.core.constants import ErrorMessages
raise NotFoundError(ErrorMessages.CONTENT_NOT_FOUND)
```

### 3. Log important operations

```python
from app.core.logging_config import logger

logger.info(f"Content created: {content.id}")
logger.error(f"Failed to process: {error}", exc_info=True)
```

### 4. Keep routes thin

```python
# Routes should just validate, call service, return response
@router.post("/")
def create(data: CreateSchema, db: Session = Depends(get_db)):
    service = MyService(db)
    return service.create(data)
```

### 5. Put business logic in services

```python
# Services handle:
# - Validation
# - Business rules
# - Calling repositories
# - Error handling
class MyService:
    def create(self, data):
        # Validate
        # Apply business rules
        # Call repository
        # Return result
```

## Testing

The new structure makes testing much easier:

```python
# Test repository
def test_student_repository():
    repo = StudentRepository(db)
    student = repo.create({"name": "Test"})
    assert student.name == "Test"

# Test service (can mock repository)
def test_auth_service():
    service = AuthService(db)
    result = service.login("test@example.com", "password")
    assert result.access_token
```

## Next Steps

1. OK Core infrastructure (constants, exceptions, logging)
2. OK Modular models and schemas
3. OK Repository pattern implementation
4. OK Service layer for auth and content
5. 🔄 Migrate remaining routes to use services
6. 🔄 Add database migrations (Alembic)
7. 🔄 Add comprehensive unit tests
8. 🔄 Add integration tests
9. 🔄 Add API documentation
10. 🔄 Performance optimization

## Questions?

Refer to the code examples in each layer for implementation details.
