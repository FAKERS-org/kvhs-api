"""
MinIO client for file storage.
Replaces GridFS for file uploads/downloads.
"""

import io
from typing import BinaryIO
from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error

from app.core.config import settings


# Initialize MinIO client
_minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)

BUCKET_NAME = settings.MINIO_BUCKET_NAME


def ensure_bucket_exists() -> None:
    """Ensure the MinIO bucket exists, create if not."""
    try:
        if not _minio_client.bucket_exists(BUCKET_NAME):
            _minio_client.make_bucket(BUCKET_NAME)
    except S3Error as e:
        raise RuntimeError(f"Failed to create MinIO bucket: {str(e)}")


async def upload_file_to_minio(file: UploadFile, object_name: str) -> tuple[str, int]:
    """
    Upload a file to MinIO.
    
    Args:
        file: The uploaded file from FastAPI
        object_name: The name to store the file as in MinIO (e.g., UUID or path)
    
    Returns:
        tuple: (object_name, file_size)
    """
    content = await file.read()
    file_size = len(content)
    
    # Upload to MinIO
    try:
        _minio_client.put_object(
            BUCKET_NAME,
            object_name,
            io.BytesIO(content),
            length=file_size,
            content_type=file.content_type or "application/octet-stream",
        )
    except S3Error as e:
        raise RuntimeError(f"Failed to upload to MinIO: {str(e)}")
    
    await file.seek(0)
    return object_name, file_size


async def download_file_from_minio(object_name: str) -> BinaryIO:
    """
    Download a file from MinIO.
    
    Args:
        object_name: The name of the file in MinIO
    
    Returns:
        BinaryIO: A bytes buffer containing the file content
    """
    try:
        response = _minio_client.get_object(BUCKET_NAME, object_name)
        buffer = io.BytesIO(response.read())
        response.close()
        response.release_conn()
        buffer.seek(0)
        return buffer
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise FileNotFoundError(f"File not found in MinIO: {object_name}")
        raise RuntimeError(f"Failed to download from MinIO: {str(e)}")


async def stream_file_from_minio(object_name: str):
    """
    Stream a file from MinIO (for large files).
    
    Args:
        object_name: The name of the file in MinIO
    
    Yields:
        bytes: Chunks of the file
    """
    try:
        response = _minio_client.get_object(BUCKET_NAME, object_name)
        for chunk in response.stream(32 * 1024):  # 32KB chunks
            yield chunk
        response.close()
        response.release_conn()
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise FileNotFoundError(f"File not found in MinIO: {object_name}")
        raise RuntimeError(f"Failed to stream from MinIO: {str(e)}")


async def delete_file_from_minio(object_name: str) -> None:
    """
    Delete a file from MinIO.
    
    Args:
        object_name: The name of the file in MinIO
    """
    try:
        _minio_client.remove_object(BUCKET_NAME, object_name)
    except S3Error as e:
        if e.code == "NoSuchKey":
            # File already doesn't exist, which is fine
            pass
        else:
            raise RuntimeError(f"Failed to delete from MinIO: {str(e)}")


async def get_file_info(object_name: str) -> dict:
    """
    Get file metadata from MinIO.
    
    Args:
        object_name: The name of the file in MinIO
    
    Returns:
        dict: File metadata including size, content_type, etc.
    """
    try:
        stat = _minio_client.stat_object(BUCKET_NAME, object_name)
        return {
            "size": stat.size,
            "content_type": stat.content_type,
            "last_modified": stat.last_modified,
            "etag": stat.etag,
        }
    except S3Error as e:
        if e.code == "NoSuchKey":
            raise FileNotFoundError(f"File not found in MinIO: {object_name}")
        raise RuntimeError(f"Failed to get file info from MinIO: {str(e)}")
