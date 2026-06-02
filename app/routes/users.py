from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy.exc import IntegrityError

from app.dependencies import AdminUser, CurrentUser, SessionDep
from app.schemas import (
    PasswordChangeModel,
    TokenPairResponse,
    UserPatchModel,
    UserResponseModel,
)
from app.utils.auth.service import AuthService
from app.utils.routes.user import UserService

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
    updated_user = await UserService.update_user(session, user, data)

    return UserResponseModel(
        id=updated_user.id,
        email=updated_user.email,
        first_name=updated_user.first_name,
        last_name=updated_user.last_name,
        mobile_number=updated_user.mobile_number,
        role=updated_user.role,
    )


@users_router.post("/me/password", response_model=TokenPairResponse)
async def change_password(
    data: PasswordChangeModel, user: CurrentUser, session: SessionDep
) -> TokenPairResponse:
    return await AuthService.change_password(
        session, user, data.current_password, data.new_password
    )


@users_router.get("", response_model=list[UserResponseModel])
async def list_users(
    admin: AdminUser,
    session: SessionDep,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> list[UserResponseModel]:
    users = await UserService.list_users(session, limit=limit, offset=offset)
    return [
        UserResponseModel(
            id=u.id,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            mobile_number=u.mobile_number,
            role=u.role,
        )
        for u in users
    ]


@users_router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int, admin: AdminUser, session: SessionDep
) -> Response:
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Cannot delete yourself"
        )
    target = await UserService.get_by_id(session, user_id)
    if target is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    await UserService.delete_user(session, target)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
