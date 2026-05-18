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
