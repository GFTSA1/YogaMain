import hashlib
import secrets
from datetime import datetime, timezone, timedelta

from sqlmodel import select

from app.models import RefreshToken
from app.settings import settings


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    """Return current UTC time as a naive datetime (timezone-unaware).

    SQLite stores datetimes without timezone info, so we keep everything naive
    UTC to avoid offset-naive/offset-aware comparison errors in tests.
    PostgreSQL in production receives the same naive UTC values correctly.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RefreshTokenService:
    @staticmethod
    async def issue(session, user_id: int) -> str:
        raw = secrets.token_urlsafe(48)
        expires_at = _utcnow() + timedelta(days=settings.jwt_refresh_ttl_days)
        row = RefreshToken(
            user_id=user_id,
            token_hash=_hash_token(raw),
            expires_at=expires_at,
        )
        session.add(row)
        await session.commit()
        return raw

    @staticmethod
    async def validate(session, raw: str) -> int | None:
        result = await session.exec(
            select(RefreshToken).where(RefreshToken.token_hash == _hash_token(raw))
        )
        row = result.first()
        if row is None:
            return None
        if row.revoked_at is not None:
            return None
        if row.expires_at <= _utcnow():
            return None
        return row.user_id

    @staticmethod
    async def revoke(session, raw: str) -> None:
        result = await session.exec(
            select(RefreshToken).where(
                RefreshToken.token_hash == _hash_token(raw),
                RefreshToken.revoked_at.is_(None),
            )
        )
        row = result.first()
        if row is None:
            return
        row.revoked_at = _utcnow()
        session.add(row)
        await session.commit()

    @staticmethod
    async def revoke_all_for_user(session, user_id: int) -> None:
        result = await session.exec(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
        )
        rows = result.all()
        now = _utcnow()
        for row in rows:
            row.revoked_at = now
            session.add(row)
        await session.commit()
