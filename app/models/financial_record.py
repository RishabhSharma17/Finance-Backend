import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import UserModel


class TransactionTypeEnum(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class FinancialRecordModel(TimestampMixin, Base):
    __tablename__ = "financial_records"

    __table_args__ = (
        Index("ix_financial_records_date_type_category", "date", "type", "category"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    type: Mapped[TransactionTypeEnum] = mapped_column(
        Enum(TransactionTypeEnum, name="transaction_type_enum"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_by_user: Mapped["UserModel"] = relationship(
        back_populates="financial_records",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<FinancialRecordModel id={self.id} type={self.type} amount={self.amount}>"
