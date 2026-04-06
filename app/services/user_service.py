import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.exceptions.base import ConflictException, NotFoundException
from app.models.user import RoleEnum, UserModel
from app.repositories.user_repository import user_repository
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, data: UserCreate) -> UserModel:
    existing = await user_repository.get_by_email(db, data.email)
    if existing is not None:
        raise ConflictException(f"Email '{data.email}' is already registered")

    user = UserModel(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
    )
    return await user_repository.create(db, user)


async def get_user(db: AsyncSession, user_id: uuid.UUID) -> UserModel:
    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise NotFoundException(f"User with id '{user_id}' not found")
    return user


async def update_user(db: AsyncSession, user_id: uuid.UUID, data: UserUpdate) -> UserModel:
    user = await get_user(db, user_id)

    if data.email is not None and data.email != user.email:
        existing = await user_repository.get_by_email(db, data.email)
        if existing is not None:
            raise ConflictException(f"Email '{data.email}' is already in use")

    update_data = data.model_dump(exclude_none=True)
    return await user_repository.update(db, user, update_data)


async def deactivate_user(db: AsyncSession, user_id: uuid.UUID) -> UserModel:
    user = await user_repository.deactivate(db, user_id)
    if user is None:
        raise NotFoundException(f"User with id '{user_id}' not found")
    return user


async def assign_role(db: AsyncSession, user_id: uuid.UUID, role: RoleEnum) -> UserModel:
    user = await get_user(db, user_id)
    return await user_repository.update(db, user, {"role": role})


async def list_users(
    db: AsyncSession, limit: int = 20, offset: int = 0
) -> tuple[list[UserModel], int]:
    users = await user_repository.get_all(db, limit=limit, offset=offset)
    total = await user_repository.count_all(db)
    return users, total
