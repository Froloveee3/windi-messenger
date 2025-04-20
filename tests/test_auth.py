import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login_success(client: AsyncClient):
    email = f"{uuid.uuid4().hex}@example.com"
    password = "testPassword"

    res = await client.post("/api/v1/users/", json={
        "name": "Auth User", "email": email, "password": password
    })
    assert res.status_code == 201

    res = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res.status_code == 200
    assert "access_token" in res.json()


@pytest.mark.asyncio
async def test_register_missing_fields(client: AsyncClient):
    res = await client.post("/api/v1/users/", json={})
    assert res.status_code == 422

    for payload in [
        {"email": f"{uuid.uuid4().hex}@example.com", "password": "testPassword"},
        {"name": "name", "password": "testPassword"},
        {"name": "name", "email": f"{uuid.uuid4().hex}@example.com"},
    ]:
        res = await client.post("/api/v1/users/", json=payload)
        assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_missing_fields_and_content_type(client: AsyncClient):
    email = f"{uuid.uuid4().hex}@example.com"
    password = "testPassword"

    res = await client.post("/api/v1/users/", json={
        "name": "Auth User", "email": email, "password": password
    })
    assert res.status_code == 201

    res = await client.post(
        "/api/v1/auth/token",
        data={"password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res.status_code == 422

    res = await client.post(
        "/api/v1/auth/token",
        data={"username": email},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res.status_code == 422


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    res = await client.post(
        "/api/v1/auth/token",
        data={"username": "noone@example.com", "password": "whatever"},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert res.status_code == 401
