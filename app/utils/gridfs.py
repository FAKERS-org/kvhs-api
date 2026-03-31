from bson import ObjectId
from fastapi import UploadFile
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from app.core.config import settings

_client = AsyncIOMotorClient(settings.MONGODB_URL)
_db = _client[settings.MONGODB_DB_NAME]
_bucket = AsyncIOMotorGridFSBucket(_db)


async def upload_file_to_gridfs(file: UploadFile) -> tuple[str, int]:
    content = await file.read()
    gridfs_id = await _bucket.upload_from_stream(
        file.filename,
        content,
        metadata={"content_type": file.content_type},
    )
    await file.seek(0)
    return str(gridfs_id), len(content)


async def open_download_stream(gridfs_id: str):
    return await _bucket.open_download_stream(ObjectId(gridfs_id))


async def delete_file_from_gridfs(gridfs_id: str) -> None:
    await _bucket.delete(ObjectId(gridfs_id))
