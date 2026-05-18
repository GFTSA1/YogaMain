from fastapi import status


async def test_register_returns_201_with_tokens(client):
    r = await client.post(
        "/auth/register",
        json={
            "email": "a@b.com",
            "password": "hunter22",
            "first_name": "A",
            "last_name": "B",
        },
    )
    assert r.status_code == status.HTTP_201_CREATED
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]


async def test_register_duplicate_email_returns_409(client):
    payload = {"email": "a@b.com", "password": "hunter22", "first_name": "A"}
    await client.post("/auth/register", json=payload)
    r = await client.post("/auth/register", json=payload)
    assert r.status_code == status.HTTP_409_CONFLICT


async def test_register_short_password_returns_422(client):
    r = await client.post(
        "/auth/register",
        json={"email": "a@b.com", "password": "short", "first_name": "A"},
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def test_register_invalid_email_returns_422(client):
    r = await client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "hunter22", "first_name": "A"},
    )
    assert r.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


async def _register(client, email="a@b.com", password="hunter22"):
    return await client.post(
        "/auth/register",
        json={"email": email, "password": password, "first_name": "A"},
    )


async def test_login_success(client):
    await _register(client)
    r = await client.post(
        "/auth/login", json={"email": "a@b.com", "password": "hunter22"}
    )
    assert r.status_code == 200
    assert r.json()["access_token"]
    assert r.json()["refresh_token"]


async def test_login_wrong_password_returns_401_generic(client):
    await _register(client)
    r = await client.post(
        "/auth/login", json={"email": "a@b.com", "password": "wrong-pass"}
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


async def test_login_unknown_email_returns_same_401_message(client):
    r = await client.post(
        "/auth/login", json={"email": "nope@b.com", "password": "anything"}
    )
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"
