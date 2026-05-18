from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.dependencies import GoogleVerifierDep, SessionDep
from app.schemas import GoogleLoginModel, LoginModel, RegisterModel, TokenPairResponse
from app.utils.auth.service import AuthService

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post(
    "/register",
    response_model=TokenPairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(data: RegisterModel, session: SessionDep) -> TokenPairResponse:
    return await AuthService.register(session, data)


@auth_router.post("/login", response_model=TokenPairResponse)
async def login(data: LoginModel, session: SessionDep) -> TokenPairResponse:
    return await AuthService.login_password(session, data.email, data.password)


@auth_router.post("/google", response_model=TokenPairResponse)
async def login_google(
    data: GoogleLoginModel,
    session: SessionDep,
    verifier: GoogleVerifierDep,
) -> TokenPairResponse:
    try:
        identity = verifier.verify(data.id_token)
    except Exception as e:
        logger.warning("bad google id_token: {}", e)
        raise HTTPException(status_code=401, detail="Invalid token")
    return await AuthService.login_google(session, identity)
