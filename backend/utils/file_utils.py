"""
ForgeMinds — File Utility Functions.
Helpers for file upload, validation, and storage.
"""

import os
import re
import uuid
import aiofiles
from typing import Union
from fastapi import UploadFile

from shared.constants import ALLOWED_FILE_EXTENSIONS, MAX_FILE_SIZE_BYTES
from backend.utils.logger import get_logger

logger = get_logger(__name__)


async def save_uploaded_file(file: UploadFile, path: str) -> str:
    """
    Save an uploaded file to the given path.

    Args:
        file: FastAPI UploadFile object.
        path: Destination file path.

    Returns:
        The absolute path where the file was saved.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        async with aiofiles.open(path, "wb") as out:
            content = await file.read()
            await out.write(content)
        logger.info("File saved: %s (%d bytes)", path, len(content))
        return os.path.abspath(path)
    except Exception as e:
        logger.error("Failed to save file %s: %s", path, e)
        raise


def get_file_extension(filename: str) -> str:
    """
    Get lowercase extension from a filename, including the dot.

    Returns:
        e.g. '.pdf', '.docx', '.png'
    """
    _, ext = os.path.splitext(filename)
    return ext.lower()


def validate_file_type(filename: str) -> bool:
    """
    Check whether the file extension is in the allowed set.

    Returns:
        True if the file type is supported, False otherwise.
    """
    ext = get_file_extension(filename)
    return ext in ALLOWED_FILE_EXTENSIONS


def get_file_size(file_path: str) -> int:
    """
    Get the size of a file in bytes.

    Returns:
        File size in bytes, or 0 if the file does not exist.
    """
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0


def generate_filename(original_name: str) -> str:
    """
    Generate a unique filename preserving the original extension.

    Format: {uuid4}_{sanitized_original_name}
    Special characters and spaces are replaced with underscores.
    """
    ext = get_file_extension(original_name)
    base = os.path.splitext(original_name)[0]
    # Sanitize: keep only alphanumeric, hyphens, underscores
    sanitized = re.sub(r"[^\w\-]", "_", base)
    sanitized = re.sub(r"_+", "_", sanitized).strip("_")
    unique_name = f"{uuid.uuid4().hex[:12]}_{sanitized}{ext}"
    return unique_name
