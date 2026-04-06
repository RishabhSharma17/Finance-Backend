import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from fastapi import Query
from pydantic import BaseModel, ConfigDict, field_validator

from app.models.financial_record import TransactionTypeEnum


class FinancialRecordBase(BaseModel):
    amount: Decimal
    type: TransactionTypeEnum
    category: str
    date: date
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("category")
    @classmethod
    def category_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category cannot be empty")
        return v


class FinancialRecordCreate(FinancialRecordBase):
    pass


class FinancialRecordUpdate(BaseModel):
    amount: Optional[Decimal] = None
    type: Optional[TransactionTypeEnum] = None
    category: Optional[str] = None
    date: Optional[date] = None
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        if v is not None and v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v


class FinancialRecordResponse(FinancialRecordBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime


class FinancialRecordFilter:
    def __init__(
        self,
        date_from: Optional[date] = Query(default=None, description="Filter from this date (inclusive)"),
        date_to: Optional[date] = Query(default=None, description="Filter to this date (inclusive)"),
        category: Optional[str] = Query(default=None, description="Filter by category"),
        type: Optional[TransactionTypeEnum] = Query(default=None, description="Filter by type"),
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
    ) -> None:
        self.date_from = date_from
        self.date_to = date_to
        self.category = category
        self.type = type
        self.limit = limit
        self.offset = offset
