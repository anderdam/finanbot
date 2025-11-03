from typing import List
from src.api.v1.schemas import TransactionCreate, TransactionUpdate
from src.models.orm_models import Transaction
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.v1 import crud
from src.api.v1.schemas import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password


async def create_transaction_service(
    db: AsyncSession, payload: TransactionCreate
) -> Transaction:
    # business rules example: disallow zero-amount transactions
    if payload.amount == 0:
        raise ValueError("Transaction amount cannot be zero")
    return await crud.create_transaction(
        db,
        amount=payload.amount,
        description=payload.description,
        occurred_at=payload.occurred_at,
    )


async def get_transaction_service(
    db: AsyncSession, transaction_id: int
) -> Optional[Transaction]:
    return await crud.get_transaction(db, transaction_id)


async def list_transactions_service(
    db: AsyncSession, limit: int = 50, offset: int = 0
) -> List[Transaction]:
    return await crud.list_transactions(db, limit=limit, offset=offset)


async def update_transaction_service(
    db: AsyncSession, transaction_id: int, payload: TransactionUpdate
):
    fields = {k: v for k, v in payload.model_dump(exclude_unset=True).items()}
    if not fields:
        return await crud.get_transaction(db, transaction_id)
    return await crud.update_transaction(db, transaction_id, **fields)


async def delete_transaction_service(db: AsyncSession, transaction_id: int) -> bool:
    return await crud.delete_transaction(db, transaction_id)


async def register_user(
    db: AsyncSession, payload: UserCreate, is_superuser: bool = False
):
    existing = await crud.get_user_by_email(db, payload.email)
    if existing:
        raise ValueError("Email already registered")
    hashed = get_password_hash(payload.password)
    user = await crud.create_user(
        db,
        email=payload.email,
        hashed_password=hashed,
        full_name=payload.full_name,
        is_superuser=is_superuser,
    )
    return user


async def authenticate_user(
    db: AsyncSession, email: str, password: str
) -> Optional[int]:
    user = await crud.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user.id


async def get_or_404_user(db: AsyncSession, user_id: int):
    user = await crud.get_user_by_id(db, user_id)
    if not user:
        raise LookupError("User not found")
    return user


async def update_user_service(db: AsyncSession, user_id: int, payload: UserUpdate):
    fields = {}
    if payload.full_name is not None:
        fields["full_name"] = payload.full_name
    if payload.password:
        fields["hashed_password"] = get_password_hash(payload.password)
    if not fields:
        return await crud.get_user_by_id(db, user_id)
    return await crud.update_user(db, user_id, **fields)
