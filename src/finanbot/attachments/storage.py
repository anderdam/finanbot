import shutil
from pathlib import Path
from typing import BinaryIO, cast
from uuid import UUID

from fastapi import UploadFile

from app.core.config import get_settings

settings = get_settings()
ATTACHMENTS_DIR = Path(settings.ATTACHMENTS_DIR)


def get_attachment_path(tx_id: UUID) -> Path:
    return ATTACHMENTS_DIR / f"{tx_id}.pdf"


def save_attachment(file: UploadFile, tx_id: UUID) -> str:
    ATTACHMENTS_DIR.mkdir(parents=True, exist_ok=True)
    file_path = get_attachment_path(tx_id)

    with file_path.open("wb") as raw_buffer:
        buffer = cast(BinaryIO, raw_buffer)
        shutil.copyfileobj(file.file, buffer)

    return str(file_path)


def delete_attachment(tx_id: UUID) -> None:
    file_path = get_attachment_path(tx_id)
    if file_path.exists():
        file_path.unlink()
