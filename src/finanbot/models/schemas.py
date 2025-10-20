from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TransactionCreate(BaseModel):
    account_id: UUID
    category_id: UUID
    occurred_at: datetime
    amount: float
    currency: str = "BRL"
    type: str
    notes: Optional[str] = None


class TransactionRead(BaseModel):
    id: UUID
    account_id: UUID
    category_id: Optional[UUID]
    occurred_at: datetime
    amount: float
    currency: str
    type: str
    notes: Optional[str]
    attachment_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    account_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    occurred_at: Optional[datetime] = None
    amount: Optional[float] = None
    currency: Optional[str] = None
    type: Optional[str] = None
    notes: Optional[str] = None
    attachment_path: Optional[str] = None
