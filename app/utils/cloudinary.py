"""
Cloudinary integration for file uploads.
"""

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core.config import settings
from app.core.logging_config import logger

# Configure Cloudinary
if settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )
    logger.info("Cloudinary configured successfully")
else:
    logger.warning("Cloudinary configuration missing. File uploads will fail.")


async def upload_file_to_cloudinary(
    file: UploadFile, folder: str = "kvhs/documents"
) -> dict | None:
    """
    Upload a file to Cloudinary.
    Returns the Cloudinary response with secure_url, public_id, etc.
    """
    if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
        logger.error("Cannot upload to Cloudinary: configuration missing")
        return None

    try:
        # Read file content
        content = await file.read()
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            content,
            folder=folder,
            resource_type="auto",  # Automatically detect image, video, raw file
            public_id=file.filename.split(".")[0],
            overwrite=True,
        )
        
        logger.info(f"File {file.filename} uploaded to Cloudinary: {result.get('secure_url')}")
        return result
    except Exception as e:
        logger.error(f"Error uploading file to Cloudinary: {str(e)}")
        return None
    finally:
        # Reset file pointer for potential re-reads
        await file.seek(0)


def delete_file_from_cloudinary(public_id: str) -> bool:
    """
    Delete a file from Cloudinary using its public_id.
    """
    if not (settings.CLOUDINARY_CLOUD_NAME and settings.CLOUDINARY_API_KEY and settings.CLOUDINARY_API_SECRET):
        return False

    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception as e:
        logger.error(f"Error deleting file from Cloudinary: {str(e)}")
        return False
