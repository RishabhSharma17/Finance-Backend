from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.exceptions.base import InvalidCredentialsException, InvalidTokenException
from app.models.user import UserModel
from app.repositories.user_repository import user_repository
from app.schemas.user import TokenResponse


async def authenticate_user(db: AsyncSession, email: str, password: str) -> UserModel:
    user = await user_repository.get_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        raise InvalidCredentialsException()
    if not user.is_active:
        raise InvalidCredentialsException("Account is deactivated")
    return user


async def login(db: AsyncSession, email: str, password: str) -> TokenResponse:
    user = await authenticate_user(db, email, password)
    payload = {"sub": str(user.id), "role": user.role.value}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> str:
    from jose import JWTError

    try:
        payload = decode_token(refresh_token)
    except JWTError:
        raise InvalidTokenException("Invalid refresh token")

    if payload.get("type") != "refresh":
        raise InvalidTokenException("Token is not a refresh token")

    user_id = payload.get("sub")
    if user_id is None:
        raise InvalidTokenException()

    import uuid
    user = await user_repository.get_by_id(db, uuid.UUID(user_id))
    if user is None or not user.is_active:
        raise InvalidTokenException("User not found or inactive")

    new_payload = {"sub": str(user.id), "role": user.role.value}
    return create_access_token(new_payload)
