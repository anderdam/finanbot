from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.finanbot.db import crud
from src.finanbot.db.session import get_db
from src.finanbot.models.schemas import AlertSummary
from src.finanbot.models.orm_models import User  # Assuming you have a User schema

from src.finanbot.models.schemas import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
    TransactionSummary,
    PaginatedTransactions,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])
db = Depends(get_db)


def get_actual_user() -> User:
    return get_actual_user()


@router.post("/", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = db,
    current_user: User = Depends(get_actual_user),
):
    tx = crud.create_transaction(db, user_id=current_user.id, transaction=transaction)
    return tx


@router.get("/{tx_id}", response_model=TransactionRead)
def get_transaction(tx_id: UUID, db: Session = db):
    tx = crud.get_transaction(db, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@router.get("/", response_model=PaginatedTransactions)
def list_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_actual_user),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    start_date: str | None = Query(default=None),
    end_date: str | None = Query(default=None),
    category: str | None = Query(default=None),
    min_amount: float | None = Query(default=None),
    max_amount: float | None = Query(default=None),
):
    """
    List transactions for the current user with optional filters and pagination.
    """
    filters = {
        "start_date": start_date,
        "end_date": end_date,
        "category": category,
        "min_amount": min_amount,
        "max_amount": max_amount,
    }

    transactions, total = crud.list_transactions_with_count(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        filters=filters,
    )

    return PaginatedTransactions(
        total=total,
        limit=limit,
        offset=offset,
        items=transactions,
    )


@router.patch("/{tx_id}", response_model=TransactionRead)
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


@router.get("/summary", response_model=TransactionSummary)
def get_transaction_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_actual_user),
    year: int = date.today().year,
    month: int = date.today().month,
):
    summary = crud.get_monthly_summary(db, current_user.id, year, month)
    if not summary:
        raise HTTPException(
            status_code=404, detail="No transactions found for this period"
        )
    return summary


@router.get("/alerts", response_model=AlertSummary)
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_actual_user),
):
    alerts = crud.generate_alerts(db, current_user.id)
    return alerts
