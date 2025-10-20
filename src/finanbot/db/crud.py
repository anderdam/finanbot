from typing import Any, Sequence
from uuid import UUID

from sqlalchemy import delete, insert, select, update
from sqlalchemy.orm import Session

from app.models.orm_models import Transaction as TransactionModel
from app.models.schemas import TransactionCreate


def create_transaction(
    db: Session, user_id: UUID, transaction: TransactionCreate
) -> TransactionModel:
    stmt = (
        insert(TransactionModel)
        .values(
            user_id=user_id,
            account_id=transaction.account_id,
            category_id=transaction.category_id,
            occurred_at=transaction.occurred_at,
            amount=transaction.amount,
            currency=transaction.currency,
            type=transaction.type,
            notes=transaction.notes,
        )
        .returning(TransactionModel)
    )
    result = db.execute(stmt)
    db.commit()
    return result.scalar_one()


def get_transaction(db: Session, tx_id: UUID) -> TransactionModel | None:
    stmt = select(TransactionModel).where(TransactionModel.id == tx_id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()


def list_transactions(
    db: Session, user_id: UUID, limit: int = 100, offset: int = 0
) -> Sequence[TransactionModel]:
    stmt = (
        select(TransactionModel)
        .where(TransactionModel.user_id == user_id)
        .order_by(TransactionModel.occurred_at.desc())
        .limit(limit)
        .offset(offset)
    )
    return db.execute(stmt).scalars().all()


def update_transaction(
    db: Session, tx_id: UUID, patch: dict[str, Any]
) -> TransactionModel | None:
    stmt = (
        update(TransactionModel)
        .where(TransactionModel.id == tx_id)
        .values(**patch)
        .returning(TransactionModel)
    )
    result = db.execute(stmt)
    db.commit()
    return result.scalar_one_or_none()


def delete_transaction(db: Session, tx_id: UUID) -> TransactionModel | None:
    stmt = (
        delete(TransactionModel)
        .where(TransactionModel.id == tx_id)
        .returning(TransactionModel)
    )
    result = db.execute(stmt)
    db.commit()
    return result.scalar_one_or_none()
