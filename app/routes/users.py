from fastapi import APIRouter

from app.dependencies import CurrentUser
from app.schemas import UserResponseModel

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserResponseModel)
async def get_me(user: CurrentUser) -> UserResponseModel:
    return UserResponseModel(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        mobile_number=user.mobile_number,
        role=user.role,
    )
