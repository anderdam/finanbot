from typing import Optional, Sequence
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.orm_models import Transaction, User


async def create_transaction(
    db: AsyncSession, *, amount: float, description: Optional[str], occurred_at
):
    stmt = (
        insert(Transaction)
        .values(amount=amount, description=description, occurred_at=occurred_at)
        .returning(Transaction)
    )
    result = await db.execute(stmt)
    row = result.first()
    await db.commit()
    return row[0]


async def get_transaction(
    db: AsyncSession, transaction_id: int
) -> Optional[Transaction]:
    stmt = select(Transaction).where(Transaction.id == transaction_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def list_transactions(
    db: AsyncSession, limit: int = 50, offset: int = 0
) -> Sequence[Transaction]:
    stmt = (
        select(Transaction)
        .order_by(Transaction.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def update_transaction(db: AsyncSession, transaction_id: int, **fields):
    stmt = (
        update(Transaction)
        .where(Transaction.id == transaction_id)
        .values(**fields)
        .returning(Transaction)
    )
    result = await db.execute(stmt)
    row = result.first()
    await db.commit()
    return row[0] if row else None


async def delete_transaction(db: AsyncSession, transaction_id: int) -> bool:
    stmt = delete(Transaction).where(Transaction.id == transaction_id)
    await db.execute(stmt)
    await db.commit()
    return True


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    q = select(User).where(User.id == user_id)
    res = await db.execute(q)
    return res.scalars().first()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    q = select(User).where(User.email == email)
    res = await db.execute(q)
    return res.scalars().first()


async def create_user(
    db: AsyncSession,
    *,
    email: str,
    hashed_password: str,
    full_name: str | None = None,
    is_superuser: bool = False,
) -> User:
    stmt = (
        insert(User)
        .values(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            is_superuser=is_superuser,
        )
        .returning(User)
    )
    res = await db.execute(stmt)
    await db.commit()
    return res.first()[0]


async def update_user(db: AsyncSession, user_id: int, **fields) -> Optional[User]:
    stmt = update(User).where(User.id == user_id).values(**fields).returning(User)
    res = await db.execute(stmt)
    await db.commit()
    row = res.first()
    return row[0] if row else None


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    stmt = delete(User).where(User.id == user_id)
    await db.execute(stmt)
    await db.commit()
    return True
