"""
MongoDB and Beanie initialization.
"""

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.core.config import settings
from app.core.logging_config import logger


async def init_mongodb() -> None:
    """Initialize MongoDB with Beanie."""
    try:
        # Create Motor client
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Select database
        db = client[settings.MONGODB_DB_NAME]
        
        # Initialize Beanie with all models
        # We will import models here to avoid circular imports
        from app.models.cms import Content, ContentTag, CMSDocument, CalendarEvent, Department
        
        await init_beanie(
            database=db,
            document_models=[
                Content,
                ContentTag,
                CMSDocument,
                CalendarEvent,
                Department,
            ],
        )
        logger.info("MongoDB and Beanie initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {str(e)}")
        raise
