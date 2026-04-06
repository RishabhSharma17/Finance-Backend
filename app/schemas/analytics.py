from decimal import Decimal

from pydantic import BaseModel

from app.schemas.financial_record import FinancialRecordResponse


class BalanceSummary(BaseModel):
    total_income: Decimal
    total_expenses: Decimal
    net_balance: Decimal


class CategoryTotal(BaseModel):
    category: str
    total: Decimal
    count: int


class CategorySummary(BaseModel):
    income: list[CategoryTotal]
    expense: list[CategoryTotal]


class MonthlyEntry(BaseModel):
    year: int
    month: int
    income: Decimal
    expense: Decimal
    net: Decimal


class MonthlySummary(BaseModel):
    entries: list[MonthlyEntry]


class DashboardResponse(BaseModel):
    balance: BalanceSummary
    categories: CategorySummary
    recent_transactions: list[FinancialRecordResponse]
    monthly_summary: MonthlySummary
