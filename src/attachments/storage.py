import shutil
import logging
from pathlib import Path
from typing import BinaryIO, cast
from uuid import UUID

from fastapi import UploadFile
from fastapi.responses import FileResponse

from src.core.config import get_settings

settings = get_settings()
ATTACHMENTS_DIR = Path(settings.attachments_dir)
logger = logging.getLogger(__name__)

# Allowed MIME types and their extensions
MIME_EXTENSION_MAP = {
    "application/pdf": ".pdf",
    "application/csv": ".csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}


def validate_attachment(file: UploadFile) -> str:
    """Validate file type and return appropriate extension."""
    if file.content_type not in MIME_EXTENSION_MAP:
        raise ValueError("Only PDF, JPEG, PNG, CSV, and XLSX files are allowed.")
    return MIME_EXTENSION_MAP[file.content_type]


def get_attachment_path(tx_id: UUID, extension: str = ".pdf") -> Path:
    """Resolve full path for attachment file."""
    return ATTACHMENTS_DIR / f"{tx_id}{extension}"


def save_attachment(file: UploadFile, tx_id: UUID) -> str:
    """Save uploaded file to disk."""
    extension = validate_attachment(file)
    file_path = get_attachment_path(tx_id, extension)

    try:
        ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
        with file_path.open("wb") as raw_buffer:
            buffer = cast(BinaryIO, raw_buffer)
            shutil.copyfileobj(file.file, buffer)
        return str(file_path)
    except Exception as e:
        logger.exception("Failed to save attachment for tx_id %s", tx_id)
        raise FileNotFoundError("Failed to save attachment.") from e


def delete_attachment(tx_id: UUID) -> None:
    """Delete attachment file if it exists."""
    for ext in MIME_EXTENSION_MAP.values():
        file_path = get_attachment_path(tx_id, ext)
        if file_path.exists():
            file_path.unlink()
            logger.info("Deleted attachment: %s", file_path)


def get_attachment(tx_id: UUID) -> FileResponse | None:
    """Serve attachment file if it exists."""
    for ext in MIME_EXTENSION_MAP.values():
        file_path = get_attachment_path(tx_id, ext)
        if file_path.exists():
            return FileResponse(
                file_path,
                media_type="application/octet-stream",
                filename=file_path.name,
            )
    return None
