from fastapi import APIRouter

from app.api.v1.endpoints.analytics import router as analytics_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.financial_records import router as records_router
from app.api.v1.endpoints.users import router as users_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(users_router, prefix="/users", tags=["Users"])
api_v1_router.include_router(records_router, prefix="/records", tags=["Financial Records"])
api_v1_router.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])
