import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.financial_record import FinancialRecordModel, TransactionTypeEnum
from app.repositories.base import BaseRepository
from app.schemas.financial_record import FinancialRecordFilter


class FinancialRecordRepository(BaseRepository[FinancialRecordModel]):
    model = FinancialRecordModel

    def _base_query(self):
        """Base query that always excludes soft-deleted records."""
        return select(FinancialRecordModel).where(
            FinancialRecordModel.is_deleted == False  # noqa: E712
        )

    async def get_filtered(
        self,
        db: AsyncSession,
        filters: FinancialRecordFilter,
    ) -> tuple[list[FinancialRecordModel], int]:
        query = self._base_query()

        if filters.date_from is not None:
            query = query.where(FinancialRecordModel.date >= filters.date_from)
        if filters.date_to is not None:
            query = query.where(FinancialRecordModel.date <= filters.date_to)
        if filters.category is not None:
            query = query.where(FinancialRecordModel.category == filters.category)
        if filters.type is not None:
            query = query.where(FinancialRecordModel.type == filters.type)

        # Count total matching records
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Apply pagination and ordering
        query = (
            query.order_by(FinancialRecordModel.date.desc())
            .limit(filters.limit)
            .offset(filters.offset)
        )
        result = await db.execute(query)
        records = list(result.scalars().all())

        return records, total

    async def soft_delete(
        self, db: AsyncSession, record_id: uuid.UUID
    ) -> FinancialRecordModel | None:
        record = await self.get_by_id(db, record_id)
        if record is None or record.is_deleted:
            return None
        record.is_deleted = True
        record.deleted_at = datetime.now(timezone.utc)
        await db.flush()
        await db.refresh(record)
        return record

    async def get_by_id_active(
        self, db: AsyncSession, record_id: uuid.UUID
    ) -> FinancialRecordModel | None:
        result = await db.execute(
            self._base_query().where(FinancialRecordModel.id == record_id)
        )
        return result.scalar_one_or_none()

    async def get_total_by_type(
        self, db: AsyncSession, record_type: TransactionTypeEnum
    ) -> Decimal:
        result = await db.execute(
            select(func.coalesce(func.sum(FinancialRecordModel.amount), 0)).where(
                FinancialRecordModel.is_deleted == False,  # noqa: E712
                FinancialRecordModel.type == record_type,
            )
        )
        return Decimal(str(result.scalar_one()))

    async def get_category_totals(
        self, db: AsyncSession, record_type: TransactionTypeEnum
    ) -> list[dict]:
        result = await db.execute(
            select(
                FinancialRecordModel.category,
                func.sum(FinancialRecordModel.amount).label("total"),
                func.count(FinancialRecordModel.id).label("count"),
            )
            .where(
                FinancialRecordModel.is_deleted == False,  # noqa: E712
                FinancialRecordModel.type == record_type,
            )
            .group_by(FinancialRecordModel.category)
            .order_by(func.sum(FinancialRecordModel.amount).desc())
        )
        return [
            {"category": row.category, "total": Decimal(str(row.total)), "count": row.count}
            for row in result.all()
        ]

    async def get_recent(
        self, db: AsyncSession, limit: int = 5
    ) -> list[FinancialRecordModel]:
        result = await db.execute(
            self._base_query()
            .order_by(FinancialRecordModel.date.desc(), FinancialRecordModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_monthly_summary(self, db: AsyncSession) -> list[dict]:
        year_col = func.extract("year", FinancialRecordModel.date).label("year")
        month_col = func.extract("month", FinancialRecordModel.date).label("month")

        income_sum = func.sum(
            case(
                (FinancialRecordModel.type == TransactionTypeEnum.INCOME, FinancialRecordModel.amount),
                else_=0,
            )
        ).label("income")

        expense_sum = func.sum(
            case(
                (FinancialRecordModel.type == TransactionTypeEnum.EXPENSE, FinancialRecordModel.amount),
                else_=0,
            )
        ).label("expense")

        result = await db.execute(
            select(year_col, month_col, income_sum, expense_sum)
            .where(FinancialRecordModel.is_deleted == False)  # noqa: E712
            .group_by(year_col, month_col)
            .order_by(year_col.desc(), month_col.desc())
        )
        return [
            {
                "year": int(row.year),
                "month": int(row.month),
                "income": Decimal(str(row.income)),
                "expense": Decimal(str(row.expense)),
            }
            for row in result.all()
        ]


financial_record_repository = FinancialRecordRepository()
