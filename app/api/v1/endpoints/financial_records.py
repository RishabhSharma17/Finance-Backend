import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import RoleEnum, UserModel
from app.schemas.common import SuccessResponse
from app.schemas.financial_record import (
    FinancialRecordCreate,
    FinancialRecordFilter,
    FinancialRecordResponse,
    FinancialRecordUpdate,
)
from app.services import financial_record_service
from app.utils.pagination import PaginatedResponse

router = APIRouter()

_analyst_or_admin = Depends(require_role(RoleEnum.ANALYST, RoleEnum.ADMIN))
_admin_only = Depends(require_role(RoleEnum.ADMIN))


@router.post(
    "/",
    response_model=SuccessResponse[FinancialRecordResponse],
    status_code=201,
    summary="Create a financial record (Analyst, Admin)",
)
async def create_record(
    data: FinancialRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = _analyst_or_admin,
) -> SuccessResponse[FinancialRecordResponse]:
    record = await financial_record_service.create_record(db, data, current_user.id)
    return SuccessResponse(data=FinancialRecordResponse.model_validate(record))


@router.get(
    "/",
    response_model=SuccessResponse[PaginatedResponse[FinancialRecordResponse]],
    summary="List financial records with optional filters (Analyst, Admin)",
)
async def list_records(
    filters: FinancialRecordFilter = Depends(),
    db: AsyncSession = Depends(get_db),
    _: UserModel = _analyst_or_admin,
) -> SuccessResponse[PaginatedResponse[FinancialRecordResponse]]:
    records, total = await financial_record_service.list_records(db, filters)
    return SuccessResponse(
        data=PaginatedResponse(
            total=total,
            limit=filters.limit,
            offset=filters.offset,
            items=[FinancialRecordResponse.model_validate(r) for r in records],
        )
    )


@router.get(
    "/{record_id}",
    response_model=SuccessResponse[FinancialRecordResponse],
    summary="Get a financial record by ID (Analyst, Admin)",
)
async def get_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: UserModel = _analyst_or_admin,
) -> SuccessResponse[FinancialRecordResponse]:
    record = await financial_record_service.get_record(db, record_id)
    return SuccessResponse(data=FinancialRecordResponse.model_validate(record))


@router.patch(
    "/{record_id}",
    response_model=SuccessResponse[FinancialRecordResponse],
    summary="Update a financial record (Analyst: own records only; Admin: any)",
)
async def update_record(
    record_id: uuid.UUID,
    data: FinancialRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = _analyst_or_admin,
) -> SuccessResponse[FinancialRecordResponse]:
    record = await financial_record_service.update_record(db, record_id, data, current_user)
    return SuccessResponse(data=FinancialRecordResponse.model_validate(record))


@router.delete(
    "/{record_id}",
    response_model=SuccessResponse[dict],
    summary="Soft-delete a financial record (Admin only)",
)
async def delete_record(
    record_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = _admin_only,
) -> SuccessResponse[dict]:
    await financial_record_service.delete_record(db, record_id, current_user)
    return SuccessResponse(data={"message": "Record deleted successfully"})
