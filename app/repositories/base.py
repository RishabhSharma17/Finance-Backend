import uuid
from typing import Any, Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: type[ModelType]

    async def get_by_id(self, db: AsyncSession, id: uuid.UUID) -> ModelType | None:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_all(self, db: AsyncSession, limit: int = 20, offset: int = 0) -> list[ModelType]:
        result = await db.execute(select(self.model).limit(limit).offset(offset))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, obj: ModelType) -> ModelType:
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(self, db: AsyncSession, obj: ModelType, data: dict[str, Any]) -> ModelType:
        for field, value in data.items():
            if value is not None:
                setattr(obj, field, value)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def delete(self, db: AsyncSession, obj: ModelType) -> None:
        await db.delete(obj)
        await db.flush()
