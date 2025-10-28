from uuid import UUID
from fastapi import APIRouter, UploadFile, HTTPException, status

from finanbot.attachments.storage import (
    save_attachment,
    get_attachment,
    delete_attachment,
)
from finanbot.db.crud import record_attachment_metadata
from sqlalchemy.orm import Session
from finanbot.db.session import get_db
from fastapi import Depends

router = APIRouter(prefix="/attachments", tags=["attachments"])


@router.post("/{tx_id}", status_code=status.HTTP_201_CREATED)
def upload_attachment(tx_id: UUID, file: UploadFile, db: Session = Depends(get_db)):
    try:
        save_attachment(file, tx_id)
        metadata = record_attachment_metadata(db, tx_id, file)
        return metadata
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve)) from ve
    except FileNotFoundError as err:
        raise HTTPException(
            status_code=500, detail="Failed to save attachment"
        ) from err


@router.get("/{tx_id}")
def download_attachment(tx_id: UUID):
    response = get_attachment(tx_id)
    if response:
        return response
    raise HTTPException(status_code=404, detail="Attachment not found")


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_attachment(tx_id: UUID):
    delete_attachment(tx_id)
    return
