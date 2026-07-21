from dataclasses import dataclass
from functools import lru_cache

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from app.settings import settings


@dataclass(frozen=True)
class GoogleIdentity:
    sub: str
    email: str
    first_name: str
    last_name: str | None


class GoogleVerifier:
    def __init__(self):
        self._request = google_requests.Request()

    def _verify_raw(self, id_token: str) -> dict:
        return google_id_token.verify_oauth2_token(
            id_token, self._request, settings.google_client_id
        )

    def verify(self, id_token: str) -> GoogleIdentity:
        claims = self._verify_raw(id_token)
        if not claims.get("email_verified"):
            raise ValueError("email_not_verified")

        given = claims.get("given_name") or ""
        if not given:
            raise ValueError("missing_given_name")

        return GoogleIdentity(
            sub=claims["sub"],
            email=claims["email"],
            first_name=given,
            last_name=claims.get("family_name") or None,
        )


@lru_cache
def get_google_verifier() -> GoogleVerifier:
    return GoogleVerifier()
