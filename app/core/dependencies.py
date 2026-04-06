from collections.abc import Callable

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.exceptions.base import ForbiddenException, InvalidTokenException, UnauthorizedException
from app.models.user import RoleEnum, UserModel
from app.repositories.user_repository import user_repository

import uuid

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> UserModel:
    try:
        payload = decode_token(token)
    except JWTError:
        raise InvalidTokenException()

    if payload.get("type") != "access":
        raise InvalidTokenException("Token is not an access token")

    user_id_str: str | None = payload.get("sub")
    if user_id_str is None:
        raise InvalidTokenException()

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        raise InvalidTokenException()

    user = await user_repository.get_by_id(db, user_id)
    if user is None:
        raise UnauthorizedException("User no longer exists")
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise ForbiddenException("Account is deactivated")
    return current_user


def require_role(*roles: RoleEnum) -> Callable:
    """Return a FastAPI dependency that enforces role-based access."""

    async def _guard(
        current_user: UserModel = Depends(get_current_active_user),
    ) -> UserModel:
        if current_user.role not in roles:
            raise ForbiddenException(
                f"Access denied. Required role(s): {', '.join(r.value for r in roles)}"
            )
        return current_user

    return _guard
