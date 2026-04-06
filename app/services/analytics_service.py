from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import TransactionTypeEnum
from app.repositories.financial_record_repository import financial_record_repository
from app.schemas.analytics import (
    BalanceSummary,
    CategorySummary,
    CategoryTotal,
    DashboardResponse,
    MonthlyEntry,
    MonthlySummary,
)
from app.schemas.financial_record import FinancialRecordResponse


async def get_balance_summary(db: AsyncSession) -> BalanceSummary:
    total_income = await financial_record_repository.get_total_by_type(
        db, TransactionTypeEnum.INCOME
    )
    total_expenses = await financial_record_repository.get_total_by_type(
        db, TransactionTypeEnum.EXPENSE
    )
    return BalanceSummary(
        total_income=total_income,
        total_expenses=total_expenses,
        net_balance=total_income - total_expenses,
    )


async def get_category_summary(db: AsyncSession) -> CategorySummary:
    income_rows = await financial_record_repository.get_category_totals(
        db, TransactionTypeEnum.INCOME
    )
    expense_rows = await financial_record_repository.get_category_totals(
        db, TransactionTypeEnum.EXPENSE
    )
    return CategorySummary(
        income=[CategoryTotal(**row) for row in income_rows],
        expense=[CategoryTotal(**row) for row in expense_rows],
    )


async def get_recent_transactions(
    db: AsyncSession, limit: int = 5
) -> list[FinancialRecordResponse]:
    records = await financial_record_repository.get_recent(db, limit=limit)
    return [FinancialRecordResponse.model_validate(r) for r in records]


async def get_monthly_summary(db: AsyncSession) -> MonthlySummary:
    rows = await financial_record_repository.get_monthly_summary(db)
    entries = [
        MonthlyEntry(
            year=row["year"],
            month=row["month"],
            income=row["income"],
            expense=row["expense"],
            net=row["income"] - row["expense"],
        )
        for row in rows
    ]
    return MonthlySummary(entries=entries)


async def get_full_dashboard(db: AsyncSession) -> DashboardResponse:
    balance, categories, recent, monthly = (
        await get_balance_summary(db),
        await get_category_summary(db),
        await get_recent_transactions(db),
        await get_monthly_summary(db),
    )
    return DashboardResponse(
        balance=balance,
        categories=categories,
        recent_transactions=recent,
        monthly_summary=monthly,
    )
