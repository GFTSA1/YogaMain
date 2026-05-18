from fastapi import status


async def _register_user(client, email="a@b.com", role=None):
    r = await client.post(
        "/auth/register",
        json={"email": email, "password": "hunter22", "first_name": "A"},
    )
    return r.json()


def _auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


async def test_get_me_returns_user(client):
    tokens = await _register_user(client)
    r = await client.get("/users/me", headers=_auth_headers(tokens["access_token"]))
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == "a@b.com"
    assert body["role"] == "user"


async def test_get_me_without_token_returns_401(client):
    r = await client.get("/users/me")
    assert r.status_code == 401


async def test_get_me_with_garbage_token_returns_401(client):
    r = await client.get("/users/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


async def test_patch_me_updates_name_and_mobile(client):
    tokens = await _register_user(client)
    r = await client.patch(
        "/users/me",
        json={"first_name": "New", "mobile_number": "+1234"},
        headers=_auth_headers(tokens["access_token"]),
    )
    assert r.status_code == 200
    body = r.json()
    assert body["first_name"] == "New"
    assert body["mobile_number"] == "+1234"


async def test_patch_me_email_conflict_returns_409(client):
    await _register_user(client, email="taken@b.com")
    tokens = await _register_user(client, email="me@b.com")
    r = await client.patch(
        "/users/me",
        json={"email": "taken@b.com"},
        headers=_auth_headers(tokens["access_token"]),
    )
    assert r.status_code == 409


async def test_patch_me_without_token_returns_401(client):
    r = await client.patch("/users/me", json={"first_name": "x"})
    assert r.status_code == 401


async def test_change_password_success_rotates_tokens(client):
    tokens = await _register_user(client)
    r = await client.post(
        "/users/me/password",
        json={"current_password": "hunter22", "new_password": "newpass11"},
        headers=_auth_headers(tokens["access_token"]),
    )
    assert r.status_code == 200
    new_pair = r.json()
    assert new_pair["access_token"]

    r_old = await client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert r_old.status_code == 401

    r_new = await client.post(
        "/auth/refresh", json={"refresh_token": new_pair["refresh_token"]}
    )
    assert r_new.status_code == 200


async def test_change_password_wrong_current_returns_401(client):
    tokens = await _register_user(client)
    r = await client.post(
        "/users/me/password",
        json={"current_password": "wrong", "new_password": "newpass11"},
        headers=_auth_headers(tokens["access_token"]),
    )
    assert r.status_code == 401


async def test_change_password_short_new_returns_422(client):
    tokens = await _register_user(client)
    r = await client.post(
        "/users/me/password",
        json={"current_password": "hunter22", "new_password": "short"},
        headers=_auth_headers(tokens["access_token"]),
    )
    assert r.status_code == 422
