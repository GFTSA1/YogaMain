from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import CurrentUser, SessionDep
from app.schemas import (
    PasswordChangeModel,
    TokenPairResponse,
    UserPatchModel,
    UserResponseModel,
)
from app.utils.auth.service import AuthService

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


@users_router.patch("/me", response_model=UserResponseModel)
async def patch_me(
    data: UserPatchModel, user: CurrentUser, session: SessionDep
) -> UserResponseModel:
    user.sqlmodel_update(data.model_dump(exclude_unset=True))
    session.add(user)
    try:
        await session.commit()
        await session.refresh(user)
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already in use"
        )

    return UserResponseModel(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        mobile_number=user.mobile_number,
        role=user.role,
    )


@users_router.post("/me/password", response_model=TokenPairResponse)
async def change_password(
    data: PasswordChangeModel, user: CurrentUser, session: SessionDep
) -> TokenPairResponse:
    return await AuthService.change_password(
        session, user, data.current_password, data.new_password
    )
