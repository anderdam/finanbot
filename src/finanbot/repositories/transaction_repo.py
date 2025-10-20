"""
This file acts as a bridge between your API layer and the raw database operations in crud.py. It’s where you implement business logic, validation, and orchestration that goes beyond simple CRUD
"""

from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import UploadFile

from app.db import crud
from app.models.schemas import TransactionCreate, TransactionUpdate
from app.attachments import storage


def create_transaction_with_attachment(
    db: Session,
    user_id: UUID,
    transaction_data: TransactionCreate,
    attachment: UploadFile | None = None,
):
    transaction = crud.create_transaction(db, user_id, transaction_data)

    if attachment:
        path = storage.save_attachment(attachment, transaction.id)
        crud.update_transaction(db, transaction.id, {"attachment_path": path})

    return transaction


def update_transaction_with_attachment(
    db: Session,
    tx_id: UUID,
    patch_data: TransactionUpdate,
    attachment: UploadFile | None = None,
):
    patch_dict = patch_data.dict(exclude_unset=True)

    if attachment:
        path = storage.save_attachment(attachment, tx_id)
        patch_dict["attachment_path"] = path

    updated = crud.update_transaction(db, tx_id, patch_dict)
    return updated


def delete_transaction_and_attachment(db: Session, tx_id: UUID):
    deleted = crud.delete_transaction(db, tx_id)
    if deleted:
        storage.delete_attachment(tx_id)
    return deleted