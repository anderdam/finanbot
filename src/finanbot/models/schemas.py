from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime


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


class PaginatedTransactions(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[TransactionRead]


class TransactionSummary(BaseModel):
    year: int
    month: int
    total_income: float
    total_expense: float
    net_balance: float
    top_categories: dict[str, float]  # e.g., {"Food": 120.50, "Transport": 80.00}


class AlertSummary(BaseModel):
    risk_score: float  # 0.0 to 1.0
    messages: List[str]


class AttachmentRead(BaseModel):
    id: UUID
    tx_id: UUID
    filename: str
    content_type: str
    uploaded_at: datetime
