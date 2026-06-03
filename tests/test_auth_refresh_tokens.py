import hashlib
from datetime import datetime, timezone, timedelta

from sqlmodel import select

from app.models import User, RefreshToken
from app.utils.auth.refresh_tokens import RefreshTokenService


async def _make_user(db_session) -> User:
    user = User(email="a@b.com", first_name="A", role="user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


def test_issued_at_default_is_naive_utc():
    row = RefreshToken(user_id=1, token_hash="x", expires_at=datetime(2030, 1, 1))

    assert row.issued_at.tzinfo is None


async def test_issue_stores_hashed_token(db_session):
    user = await _make_user(db_session)
    raw = await RefreshTokenService.issue(db_session, user.id)

    assert isinstance(raw, str) and len(raw) > 32
    expected_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    rows = (await db_session.exec(select(RefreshToken))).all()
    assert len(rows) == 1
    assert rows[0].token_hash == expected_hash
    assert rows[0].user_id == user.id
    assert rows[0].revoked_at is None
    assert rows[0].expires_at > datetime.now(timezone.utc).replace(tzinfo=None)


async def test_validate_returns_user_id_for_valid_token(db_session):
    user = await _make_user(db_session)
    raw = await RefreshTokenService.issue(db_session, user.id)

    assert await RefreshTokenService.validate(db_session, raw) == user.id


async def test_validate_returns_none_for_unknown_token(db_session):
    assert await RefreshTokenService.validate(db_session, "not-a-real-token") is None


async def test_validate_returns_none_for_revoked_token(db_session):
    user = await _make_user(db_session)
    raw = await RefreshTokenService.issue(db_session, user.id)
    await RefreshTokenService.revoke(db_session, raw)

    assert await RefreshTokenService.validate(db_session, raw) is None


async def test_validate_returns_none_for_expired_token(db_session):
    user = await _make_user(db_session)
    raw = await RefreshTokenService.issue(db_session, user.id)
    # Backdate expiry
    row = (await db_session.exec(select(RefreshToken))).one()
    row.expires_at = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=1)
    db_session.add(row)
    await db_session.commit()

    assert await RefreshTokenService.validate(db_session, raw) is None


async def test_revoke_unknown_token_is_a_noop(db_session):
    # Should not raise.
    await RefreshTokenService.revoke(db_session, "ghost")


async def test_revoke_all_for_user_kills_every_active_token(db_session):
    user = await _make_user(db_session)
    raw1 = await RefreshTokenService.issue(db_session, user.id)
    raw2 = await RefreshTokenService.issue(db_session, user.id)

    await RefreshTokenService.revoke_all_for_user(db_session, user.id)

    assert await RefreshTokenService.validate(db_session, raw1) is None
    assert await RefreshTokenService.validate(db_session, raw2) is None
