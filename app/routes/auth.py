from fastapi import APIRouter, status

from app.dependencies import SessionDep
from app.schemas import RegisterModel, TokenPairResponse
from app.utils.auth.service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(data: RegisterModel, session: SessionDep) -> TokenPairResponse:
    return await AuthService.register(session, data)
