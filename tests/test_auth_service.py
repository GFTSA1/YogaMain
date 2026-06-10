import pytest
from fastapi import HTTPException
from sqlmodel import select

from app.models import User, RefreshToken
from app.schemas import RegisterModel
from app.utils.auth.google import GoogleIdentity
from app.utils.auth.service import AuthService
from app.utils.auth.refresh_tokens import RefreshTokenService


async def test_register_creates_user_and_returns_token_pair(db_session):
    pair = await AuthService.register(
        db_session,
        RegisterModel(
            email="a@b.com",
            password="hunter22",
            first_name="A",
            last_name="B",
        ),
    )
    assert pair.access_token and pair.refresh_token
    user = (await db_session.exec(select(User))).one()
    assert user.email == "a@b.com"
    assert user.password_hash is not None
    assert user.role == "user"


async def test_register_duplicate_email_raises_409(db_session):
    payload = RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    await AuthService.register(db_session, payload)
    with pytest.raises(HTTPException) as exc:
        await AuthService.register(db_session, payload)
    assert exc.value.status_code == 409


async def test_login_password_success(db_session):
    await AuthService.register(
        db_session, RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    )
    pair = await AuthService.login_password(db_session, "a@b.com", "hunter22")
    assert pair.access_token and pair.refresh_token


async def test_login_password_wrong_password_401(db_session):
    await AuthService.register(
        db_session, RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    )
    with pytest.raises(HTTPException) as exc:
        await AuthService.login_password(db_session, "a@b.com", "wrong-pass")
    assert exc.value.status_code == 401


async def test_login_password_unknown_email_401_with_same_message(db_session):
    with pytest.raises(HTTPException) as exc:
        await AuthService.login_password(db_session, "nope@b.com", "anything")
    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"


async def test_login_password_for_google_only_user_401(db_session):
    user = User(email="g@b.com", first_name="G", google_sub="sub-1", role="user")
    db_session.add(user)
    await db_session.commit()
    with pytest.raises(HTTPException) as exc:
        await AuthService.login_password(db_session, "g@b.com", "anything")
    assert exc.value.status_code == 401


async def test_login_google_creates_new_user(db_session):
    identity = GoogleIdentity(
        sub="sub-1", email="g@b.com", first_name="G", last_name="X"
    )
    pair = await AuthService.login_google(db_session, identity)
    assert pair.access_token and pair.refresh_token
    user = (await db_session.exec(select(User))).one()
    assert user.google_sub == "sub-1"
    assert user.password_hash is None


async def test_login_google_auto_links_by_email(db_session):
    await AuthService.register(
        db_session, RegisterModel(email="g@b.com", password="hunter22", first_name="G")
    )
    identity = GoogleIdentity(
        sub="sub-1", email="g@b.com", first_name="G", last_name=None
    )
    await AuthService.login_google(db_session, identity)
    user = (await db_session.exec(select(User))).one()
    assert user.google_sub == "sub-1"
    assert user.password_hash is not None  # still has password


async def test_login_google_matches_by_sub_even_if_email_changed(db_session):
    identity1 = GoogleIdentity(
        sub="sub-1", email="old@b.com", first_name="G", last_name=None
    )
    await AuthService.login_google(db_session, identity1)
    identity2 = GoogleIdentity(
        sub="sub-1", email="new@b.com", first_name="G", last_name=None
    )
    await AuthService.login_google(db_session, identity2)
    users = (await db_session.exec(select(User))).all()
    assert len(users) == 1
    assert users[0].google_sub == "sub-1"


async def test_refresh_returns_new_access_token(db_session):
    pair = await AuthService.register(
        db_session, RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    )
    fresh = await AuthService.refresh(db_session, pair.refresh_token)
    assert fresh.access_token


async def test_refresh_with_bad_token_401(db_session):
    with pytest.raises(HTTPException) as exc:
        await AuthService.refresh(db_session, "ghost-token")
    assert exc.value.status_code == 401


async def test_logout_revokes_refresh_token(db_session):
    pair = await AuthService.register(
        db_session, RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    )
    await AuthService.logout(db_session, pair.refresh_token)
    with pytest.raises(HTTPException) as exc:
        await AuthService.refresh(db_session, pair.refresh_token)
    assert exc.value.status_code == 401


async def test_change_password_revokes_all_tokens_and_issues_new_pair(db_session):
    pair = await AuthService.register(
        db_session, RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    )
    user = (await db_session.exec(select(User))).one()
    new_pair = await AuthService.change_password(
        db_session, user, current_password="hunter22", new_password="newpass11"
    )
    # Old refresh dies
    with pytest.raises(HTTPException):
        await AuthService.refresh(db_session, pair.refresh_token)
    # New refresh works
    fresh = await AuthService.refresh(db_session, new_pair.refresh_token)
    assert fresh.access_token


async def test_change_password_wrong_current_401(db_session):
    pair = await AuthService.register(
        db_session, RegisterModel(email="a@b.com", password="hunter22", first_name="A")
    )
    user = (await db_session.exec(select(User))).one()
    with pytest.raises(HTTPException) as exc:
        await AuthService.change_password(db_session, user, "wrong", "newpass11")
    assert exc.value.status_code == 401


async def test_change_password_for_google_only_user_409(db_session):
    user = User(email="g@b.com", first_name="G", google_sub="sub-1", role="user")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    with pytest.raises(HTTPException) as exc:
        await AuthService.change_password(db_session, user, "anything", "newpass11")
    assert exc.value.status_code == 409
