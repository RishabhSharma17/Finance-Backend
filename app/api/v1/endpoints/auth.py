from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import UserModel
from app.schemas.common import SuccessResponse
from app.schemas.user import AccessTokenResponse, RefreshTokenRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter()


@router.post("/login", response_model=TokenResponse, summary="Login with email and password")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await auth_service.login(db, form_data.username, form_data.password)


@router.post("/refresh", response_model=AccessTokenResponse, summary="Refresh access token")
async def refresh_token(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> AccessTokenResponse:
    new_token = await auth_service.refresh_access_token(db, body.refresh_token)
    return AccessTokenResponse(access_token=new_token)


@router.get("/me", response_model=SuccessResponse[UserResponse], summary="Get current user profile")
async def me(
    current_user: UserModel = Depends(get_current_active_user),
) -> SuccessResponse[UserResponse]:
    return SuccessResponse(data=UserResponse.model_validate(current_user))
