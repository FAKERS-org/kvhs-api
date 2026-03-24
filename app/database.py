"""
Database configuration and session management.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging_config import logger

connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    echo=False,  # Set to True for SQL query logging
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    Automatically closes session after use.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    from app.models import Base

    if not settings.AUTO_CREATE_TABLES:
        logger.info("Skipping automatic database table creation")
        return

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
