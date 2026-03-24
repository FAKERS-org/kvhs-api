"""
Base repository with common CRUD operations.
"""

from typing import Any, Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository with common CRUD operations."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: int) -> ModelType | None:
        """Get a single record by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_multi(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get multiple records with pagination."""
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def get_by_field(self, field: str, value: Any) -> ModelType | None:
        """Get a single record by a specific field."""
        return (
            self.db.query(self.model)
            .filter(getattr(self.model, field) == value)
            .first()
        )

    def get_multi_by_field(
        self, field: str, value: Any, skip: int = 0, limit: int = 100
    ) -> list[ModelType]:
        """Get multiple records by a specific field."""
        return (
            self.db.query(self.model)
            .filter(getattr(self.model, field) == value)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, obj_in: dict[str, Any]) -> ModelType:
        """Create a new record."""
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: dict[str, Any]) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, db_obj: ModelType) -> None:
        """Delete a record."""
        self.db.delete(db_obj)
        self.db.commit()

    def exists(self, id: int) -> bool:
        """Check if a record exists by ID."""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None

    def count(self) -> int:
        """Count total records."""
        return self.db.query(self.model).count()
