import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.user import RoleEnum, UserModel
from app.schemas.common import SuccessResponse
from app.schemas.user import RoleUpdate, UserCreate, UserResponse, UserUpdate
from app.services import user_service
from app.utils.pagination import PaginatedResponse, PaginationParams

router = APIRouter()

_admin = Depends(require_role(RoleEnum.ADMIN))


@router.post(
    "/",
    response_model=SuccessResponse[UserResponse],
    status_code=201,
    summary="Create a new user (Admin only)",
)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = _admin,
) -> SuccessResponse[UserResponse]:
    user = await user_service.create_user(db, data)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.get(
    "/",
    response_model=SuccessResponse[PaginatedResponse[UserResponse]],
    summary="List all users (Admin only)",
)
async def list_users(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    _: UserModel = _admin,
) -> SuccessResponse[PaginatedResponse[UserResponse]]:
    users, total = await user_service.list_users(db, pagination.limit, pagination.offset)
    return SuccessResponse(
        data=PaginatedResponse(
            total=total,
            limit=pagination.limit,
            offset=pagination.offset,
            items=[UserResponse.model_validate(u) for u in users],
        )
    )


@router.get(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Get a user by ID (Admin only)",
)
async def get_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: UserModel = _admin,
) -> SuccessResponse[UserResponse]:
    user = await user_service.get_user(db, user_id)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.patch(
    "/{user_id}",
    response_model=SuccessResponse[UserResponse],
    summary="Update user details (Admin only)",
)
async def update_user(
    user_id: uuid.UUID,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = _admin,
) -> SuccessResponse[UserResponse]:
    user = await user_service.update_user(db, user_id, data)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.post(
    "/{user_id}/deactivate",
    response_model=SuccessResponse[UserResponse],
    summary="Deactivate a user (Admin only)",
)
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: UserModel = _admin,
) -> SuccessResponse[UserResponse]:
    user = await user_service.deactivate_user(db, user_id)
    return SuccessResponse(data=UserResponse.model_validate(user))


@router.patch(
    "/{user_id}/role",
    response_model=SuccessResponse[UserResponse],
    summary="Assign a role to a user (Admin only)",
)
async def assign_role(
    user_id: uuid.UUID,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: UserModel = _admin,
) -> SuccessResponse[UserResponse]:
    user = await user_service.assign_role(db, user_id, data.role)
    return SuccessResponse(data=UserResponse.model_validate(user))
