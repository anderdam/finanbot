from datetime import datetime
from enum import Enum
from uuid import UUID

from sqlalchemy import (
    JSON,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import CHAR
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


class Base(DeclarativeBase):
    pass


class TransactionType(str, Enum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column("users_id", primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(150), nullable=True, unique=True)
    display_name: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    accounts: Mapped[list["Account"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    categories: Mapped[list["Category"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    settings: Mapped[list["Setting"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Account(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "acc_name", name="uq_user_account_name"),
    )

    id: Mapped[UUID] = mapped_column("accounts_id", primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("finances.users.users_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column("acc_name", String(50), nullable=False)
    type: Mapped[str] = mapped_column("acc_type", String(50), nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="BRL")
    balance: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    details: Mapped[dict[str, object]] = mapped_column(
        JSON, nullable=False, default=dict
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="accounts")
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="account")


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column("categories_id", primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("finances.users.users_id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column("cat_name", String(50), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)  # expense or income
    parent_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("finances.categories.categories_id", ondelete="SET NULL"),
        nullable=True,
    )
    color: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="categories")
    parent: Mapped["Category | None"] = relationship(
        "Category", remote_side=[id], backref="children"
    )
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="category")


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column("transactions_id", primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("finances.users.users_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    account_id: Mapped[UUID] = mapped_column(
        ForeignKey("finances.accounts.accounts_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    category_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("finances.categories.categories_id", ondelete="SET NULL"),
        nullable=True,
    )
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    amount: Mapped[float] = mapped_column(Numeric(18, 2), nullable=False)
    currency: Mapped[str] = mapped_column(CHAR(3), nullable=False, default="USD")
    type: Mapped[TransactionType] = mapped_column("tra_type", Text, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    attachment_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
    account: Mapped["Account"] = relationship(back_populates="transactions")
    category: Mapped["Category | None"] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction {self.id} {self.amount} {self.currency}>"


class Setting(Base):
    __tablename__ = "settings"

    id: Mapped[UUID] = mapped_column("settings_id", primary_key=True)
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("finances.users.users_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    key: Mapped[str] = mapped_column("set_key", Text, nullable=False)
    value: Mapped[dict[str, object]] = mapped_column("set_value", JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="settings")
