import time
import jwt as pyjwt

from app.settings import settings


class InvalidTokenError(Exception):
    pass


_ALGORITHM = "HS256"


def encode_access_token(user_id: int) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + settings.jwt_access_ttl_minutes * 60,
        "type": "access",
    }
    return pyjwt.encode(payload, settings.jwt_secret, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> int:
    try:
        payload = pyjwt.decode(token, settings.jwt_secret, algorithms=[_ALGORITHM])
    except pyjwt.PyJWTError as e:
        raise InvalidTokenError(str(e))

    if payload.get("type") != "access":
        raise InvalidTokenError("wrong token type")

    sub = payload.get("sub")
    if not sub:
        raise InvalidTokenError("missing sub")

    try:
        return int(sub)
    except (TypeError, ValueError):
        raise InvalidTokenError("non-integer sub")
