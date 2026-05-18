from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.models import User
from app.utils.auth.jwt import decode_access_token, InvalidTokenError
from app.utils.auth.google import GoogleVerifier, get_google_verifier
from app.dependencies.session import SessionDep

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    session: SessionDep,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
) -> User:
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    try:
        user_id = decode_access_token(creds.credentials)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    return user


async def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
AdminUser = Annotated[User, Depends(require_admin)]
GoogleVerifierDep = Annotated[GoogleVerifier, Depends(get_google_verifier)]