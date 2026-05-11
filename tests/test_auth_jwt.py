import time
from datetime import datetime, timezone, timedelta
import jwt as pyjwt
import pytest

from app.settings import settings
from app.utils.auth.jwt import (
    encode_access_token,
    decode_access_token,
    InvalidTokenError,
)


def test_encode_decode_round_trip():
    token = encode_access_token(42)
    assert decode_access_token(token) == 42


def test_decode_rejects_bad_signature():
    token = encode_access_token(42)
    tampered = token[:-4] + "AAAA"
    with pytest.raises(InvalidTokenError):
        decode_access_token(tampered)


def test_decode_rejects_expired():
    # Forge a token with exp in the past.
    payload = {
        "sub": "42",
        "iat": int(time.time()) - 7200,
        "exp": int(time.time()) - 3600,
        "type": "access",
    }
    token = pyjwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_rejects_wrong_type():
    payload = {
        "sub": "42",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "type": "refresh",  # wrong
    }
    token = pyjwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)


def test_decode_rejects_missing_sub():
    payload = {
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "type": "access",
    }
    token = pyjwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    with pytest.raises(InvalidTokenError):
        decode_access_token(token)
