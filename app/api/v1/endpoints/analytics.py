from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import RoleEnum, UserModel
from app.schemas.analytics import (
    BalanceSummary,
    CategorySummary,
    DashboardResponse,
    MonthlySummary,
)
from app.schemas.common import SuccessResponse
from app.schemas.financial_record import FinancialRecordResponse
from app.services import analytics_service

router = APIRouter()

_any_role = Depends(require_role(RoleEnum.VIEWER, RoleEnum.ANALYST, RoleEnum.ADMIN))


@router.get(
    "/summary",
    response_model=SuccessResponse[BalanceSummary],
    summary="Get total income, expenses, and net balance (All roles)",
)
async def get_balance_summary(
    db: AsyncSession = Depends(get_db),
    _: UserModel = _any_role,
) -> SuccessResponse[BalanceSummary]:
    summary = await analytics_service.get_balance_summary(db)
    return SuccessResponse(data=summary)


@router.get(
    "/categories",
    response_model=SuccessResponse[CategorySummary],
    summary="Get category-wise totals for income and expenses (All roles)",
)
async def get_category_summary(
    db: AsyncSession = Depends(get_db),
    _: UserModel = _any_role,
) -> SuccessResponse[CategorySummary]:
    summary = await analytics_service.get_category_summary(db)
    return SuccessResponse(data=summary)


@router.get(
    "/recent",
    response_model=SuccessResponse[list[FinancialRecordResponse]],
    summary="Get last 5 transactions (All roles)",
)
async def get_recent_transactions(
    db: AsyncSession = Depends(get_db),
    _: UserModel = _any_role,
) -> SuccessResponse[list[FinancialRecordResponse]]:
    transactions = await analytics_service.get_recent_transactions(db)
    return SuccessResponse(data=transactions)


@router.get(
    "/monthly",
    response_model=SuccessResponse[MonthlySummary],
    summary="Get monthly income/expense summary (All roles)",
)
async def get_monthly_summary(
    db: AsyncSession = Depends(get_db),
    _: UserModel = _any_role,
) -> SuccessResponse[MonthlySummary]:
    summary = await analytics_service.get_monthly_summary(db)
    return SuccessResponse(data=summary)


@router.get(
    "/dashboard",
    response_model=SuccessResponse[DashboardResponse],
    summary="Get full dashboard — all analytics in one call (All roles)",
)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _: UserModel = _any_role,
) -> SuccessResponse[DashboardResponse]:
    dashboard = await analytics_service.get_full_dashboard(db)
    return SuccessResponse(data=dashboard)
