import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserModel
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    model = UserModel

    async def get_by_email(self, db: AsyncSession, email: str) -> UserModel | None:
        result = await db.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalar_one_or_none()

    async def get_active_users(
        self, db: AsyncSession, limit: int = 20, offset: int = 0
    ) -> list[UserModel]:
        result = await db.execute(
            select(UserModel)
            .where(UserModel.is_active == True)  # noqa: E712
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def count_all(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count()).select_from(UserModel))
        return result.scalar_one()

    async def deactivate(self, db: AsyncSession, user_id: uuid.UUID) -> UserModel | None:
        user = await self.get_by_id(db, user_id)
        if user is None:
            return None
        user.is_active = False
        await db.flush()
        await db.refresh(user)
        return user


user_repository = UserRepository()
