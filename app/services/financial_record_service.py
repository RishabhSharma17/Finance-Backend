import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions.base import ForbiddenException, NotFoundException
from app.models.financial_record import FinancialRecordModel
from app.models.user import RoleEnum, UserModel
from app.repositories.financial_record_repository import financial_record_repository
from app.schemas.financial_record import (
    FinancialRecordCreate,
    FinancialRecordFilter,
    FinancialRecordUpdate,
)


async def create_record(
    db: AsyncSession, data: FinancialRecordCreate, created_by: uuid.UUID
) -> FinancialRecordModel:
    record = FinancialRecordModel(
        amount=data.amount,
        type=data.type,
        category=data.category,
        date=data.date,
        description=data.description,
        created_by=created_by,
    )
    return await financial_record_repository.create(db, record)


async def get_record(db: AsyncSession, record_id: uuid.UUID) -> FinancialRecordModel:
    record = await financial_record_repository.get_by_id_active(db, record_id)
    if record is None:
        raise NotFoundException(f"Financial record '{record_id}' not found")
    return record


async def update_record(
    db: AsyncSession,
    record_id: uuid.UUID,
    data: FinancialRecordUpdate,
    requester: UserModel,
) -> FinancialRecordModel:
    record = await get_record(db, record_id)

    # Analysts can only update their own records; Admins can update any
    if requester.role == RoleEnum.ANALYST and record.created_by != requester.id:
        raise ForbiddenException("You can only update your own records")

    update_data = data.model_dump(exclude_none=True)
    return await financial_record_repository.update(db, record, update_data)


async def delete_record(
    db: AsyncSession, record_id: uuid.UUID, requester: UserModel
) -> None:
    record = await get_record(db, record_id)

    # Only admins can delete (enforced at API layer too, but double-checked here)
    if requester.role != RoleEnum.ADMIN:
        raise ForbiddenException("Only admins can delete records")

    result = await financial_record_repository.soft_delete(db, record.id)
    if result is None:
        raise NotFoundException(f"Financial record '{record_id}' not found")


async def list_records(
    db: AsyncSession, filters: FinancialRecordFilter
) -> tuple[list[FinancialRecordModel], int]:
    return await financial_record_repository.get_filtered(db, filters)
