from typing import Any, Sequence
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import func, delete, insert, select, update
from sqlalchemy.orm import Session

from src.finanbot.models.orm_models import Transaction as TransactionModel, Attachment
from src.finanbot.models.schemas import TransactionCreate
from fastapi import UploadFile


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


def list_transactions_with_count(
    db: Session,
    user_id: UUID,
    limit: int,
    offset: int,
    filters: dict[str, Any],
) -> tuple[Sequence[TransactionModel], int]:
    query = db.query(TransactionModel).filter(TransactionModel.user_id == user_id)

    if filters.get("start_date"):
        query = query.filter(TransactionModel.occurred_at >= filters["start_date"])
    if filters.get("end_date"):
        query = query.filter(TransactionModel.occurred_at <= filters["end_date"])
    if filters.get("category"):
        query = query.filter(TransactionModel.category_id == filters["category"])
    if filters.get("min_amount"):
        query = query.filter(TransactionModel.amount >= filters["min_amount"])
    if filters.get("max_amount"):
        query = query.filter(TransactionModel.amount <= filters["max_amount"])

    total = query.count()
    transactions = (
        query.order_by(TransactionModel.occurred_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return transactions, total


def get_monthly_summary(
    db: Session, user_id: UUID, year: int, month: int
) -> dict[str, Any]:
    base_query = db.query(TransactionModel).filter(
        TransactionModel.user_id == user_id,
        func.extract("year", TransactionModel.occurred_at) == year,
        func.extract("month", TransactionModel.occurred_at) == month,
    )

    income = (
        base_query.filter(TransactionModel.amount > 0)
        .with_entities(func.sum(TransactionModel.amount))
        .scalar()
        or 0
    )

    expense = (
        base_query.filter(TransactionModel.amount < 0)
        .with_entities(func.sum(TransactionModel.amount))
        .scalar()
        or 0
    )

    category_totals = (
        base_query.with_entities(
            TransactionModel.category_id, func.sum(TransactionModel.amount)
        )
        .group_by(TransactionModel.category_id)
        .all()
    )

    top_categories = {
        str(category_id): float(total) for category_id, total in category_totals
    }

    return {
        "year": year,
        "month": month,
        "total_income": float(income),
        "total_expense": abs(float(expense)),
        "net_balance": float(income + expense),
        "top_categories": top_categories,
    }


def generate_alerts(db: Session, user_id: UUID) -> dict:
    today = datetime.today()
    start_date = today - timedelta(days=30)

    txs = (
        db.query(TransactionModel)
        .filter(
            TransactionModel.user_id == user_id,
            TransactionModel.occurred_at >= start_date,
        )
        .all()
    )

    income = sum(tx.amount for tx in txs if tx.amount > 0)
    expense = sum(tx.amount for tx in txs if tx.amount < 0)
    net = income + expense

    messages = []
    risk_score = 0.0

    if income == 0:
        messages.append("No income recorded in the last 30 days.")
        risk_score += 0.5

    if abs(expense) > income:
        messages.append("You’re spending more than you earn.")
        risk_score += 0.4

    if net < 0:
        messages.append("Your net balance is negative this month.")
        risk_score += 0.3

    if len(txs) > 20:
        messages.append(
            "High transaction volume — consider reviewing discretionary expenses."
        )
        risk_score += 0.2

    risk_score = min(risk_score, 1.0)

    return {
        "risk_score": round(risk_score, 2),
        "messages": messages or ["No alerts. You're on track!"],
    }


def record_attachment_metadata(db, tx_id, file: UploadFile):
    attachment = Attachment(
        tx_id=tx_id,
        filename=file.filename,
        content_type=file.content_type,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment
