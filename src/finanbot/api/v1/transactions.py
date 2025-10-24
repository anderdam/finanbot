from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db import crud
from db.session import get_db
from models.schemas import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])
db = Depends(get_db)


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(transaction: TransactionCreate, db: Session = db):
    tx = crud.create_transaction(
        db,
        user_id=UUID("00000000-0000-0000-0000-000000000000"),
        transaction=transaction,
    )
    return tx


@router.get("/{tx_id}", response_model=TransactionRead)
def get_transaction(tx_id: UUID, db: Session = db):
    tx = crud.get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.get("/", response_model=list[TransactionRead])
def list_transactions(
    db: Session = db,
    user_id_arg=None,
    limit: int = 100,
    offset: int = 0,
):
    user_id = (
        user_id_arg if user_id_arg else UUID("00000000-0000-0000-0000-000000000000")
    )
    return crud.list_transactions(db, user_id=user_id, limit=limit, offset=offset)


@router.patch("/{tx_id}", response_model=TransactionUpdate)
def update_transaction(tx_id: UUID, patch: TransactionUpdate, db: Session = db):
    updated = crud.update_transaction(db, tx_id, patch.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated


@router.delete("/{tx_id}", response_model=TransactionRead)
def delete_transaction(tx_id: UUID, db: Session = db):
    deleted = crud.delete_transaction(db, tx_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return deleted
