"""
Utility functions and helpers.
"""

import re
from datetime import datetime


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug.

    Args:
        text: Text to slugify

    Returns:
        Slugified text
    """
    # Convert to lowercase
    text = text.lower()

    # Replace spaces and underscores with hyphens
    text = re.sub(r"[\s_]+", "-", text)

    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r"[^\w\-]", "", text)

    # Remove multiple consecutive hyphens
    text = re.sub(r"\-+", "-", text)

    # Strip hyphens from start and end
    text = text.strip("-")

    return text


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size (e.g., "1.5 MB")
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def validate_file_extension(filename: str, allowed_extensions: set[str]) -> bool:
    """
    Validate file extension.

    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions

    Returns:
        True if extension is allowed, False otherwise
    """
    extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""
    return extension in allowed_extensions


def get_academic_year(date: datetime | None = None) -> str:
    """
    Get academic year from date.

    Args:
        date: Date to get academic year from (defaults to now)

    Returns:
        Academic year in format "2023-2024"
    """
    if date is None:
        date = datetime.now()

    year = date.year
    # Academic year typically starts in September
    if date.month >= 9:
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent security issues.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path traversal attempts
    filename = filename.replace("../", "").replace("..\\", "")

    # Remove non-alphanumeric characters except dots, hyphens, and underscores
    filename = re.sub(r"[^\w\-\.]", "_", filename)

    # Limit filename length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + ("." + ext if ext else "")

    return filename
