from fastapi import HTTPException, status
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from app.models import User
from app.schemas import (
    RegisterModel,
    TokenPairResponse,
    AccessTokenResponse,
)
from app.utils.auth.google import GoogleIdentity
from app.utils.auth.jwt import encode_access_token
from app.utils.auth.passwords import hash_password, verify_password
from app.utils.auth.refresh_tokens import RefreshTokenService


class AuthService:
    @staticmethod
    async def issue_token_pair(session, user_id: int) -> TokenPairResponse:
        access = encode_access_token(user_id)
        refresh = await RefreshTokenService.issue(session, user_id)
        return TokenPairResponse(access_token=access, refresh_token=refresh)

    @staticmethod
    async def register(session, data: RegisterModel) -> TokenPairResponse:
        user = User(
            email=data.email,
            first_name=data.first_name,
            last_name=data.last_name,
            mobile_number=data.mobile_number,
            password_hash=hash_password(data.password),
            role="user",
        )
        session.add(user)
        try:
            await session.commit()
            await session.refresh(user)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already in use",
            )
        logger.info("user registered: user_id={}", user.id)
        return await AuthService.issue_token_pair(session, user.id)

    @staticmethod
    async def login_password(session, email: str, password: str) -> TokenPairResponse:
        result = await session.exec(select(User).where(User.email == email))
        user = result.first()
        if user is None or not verify_password(password, user.password_hash):
            logger.warning(
                "login failed: email={} reason={}",
                email,
                "unknown_user" if user is None else "bad_password",
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        logger.info("user logged in: user_id={}", user.id)
        return await AuthService.issue_token_pair(session, user.id)

    @staticmethod
    async def login_google(session, identity: GoogleIdentity) -> TokenPairResponse:
        # 1. match by sub
        result = await session.exec(select(User).where(User.google_sub == identity.sub))
        user = result.first()

        if user is None:
            # 2. match by email -> auto-link
            result = await session.exec(
                select(User).where(User.email == identity.email)
            )
            user = result.first()
            if user is not None:
                user.google_sub = identity.sub
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info("google login auto-linked: user_id={}", user.id)

        if user is None:
            # 3. create new
            user = User(
                email=identity.email,
                first_name=identity.first_name,
                last_name=identity.last_name,
                google_sub=identity.sub,
                role="user",
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            logger.info("google login created user: user_id={}", user.id)
        else:
            logger.info("google login: user_id={}", user.id)

        return await AuthService.issue_token_pair(session, user.id)

    @staticmethod
    async def refresh(session, refresh_token: str) -> AccessTokenResponse:
        user_id = await RefreshTokenService.validate(session, refresh_token)
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        access = encode_access_token(user_id)
        return AccessTokenResponse(access_token=access)

    @staticmethod
    async def logout(session, refresh_token: str) -> None:
        await RefreshTokenService.revoke(session, refresh_token)

    @staticmethod
    async def change_password(
        session, user: User, current_password: str, new_password: str
    ) -> TokenPairResponse:
        if user.password_hash is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No password set for this account",
            )
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        user.password_hash = hash_password(new_password)
        session.add(user)
        await session.commit()
        await RefreshTokenService.revoke_all_for_user(session, user.id)
        logger.info("password changed: user_id={}", user.id)
        return await AuthService.issue_token_pair(session, user.id)
