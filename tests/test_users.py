import pytest
import uuid

from httpx import AsyncClient
from sqlalchemy import update

from app.db.session import engine
from app.models import User as DBUser


async def register(client: AsyncClient, name: str, email: str, password: str) -> str:
    res = await client.post(
        "/api/v1/users/",
        json={"name": name, "email": email, "password": password},
    )
    assert res.status_code == 201
    
    res = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200
    
    return res.json()["access_token"]


async def register_and_promote_admin(client: AsyncClient) -> str:
    email = f"{uuid.uuid4().hex}@example.com"
    password = "adminpass"
    token0 = await register(client, "SuperAdmin", email, password)

    me = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token0}"}
    )
    admin_id = me.json()["id"]

    async with engine.begin() as conn:
        await conn.execute(
            update(DBUser)
            .where(DBUser.id == admin_id)
            .values(is_admin=True)
        )

    res = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert res.status_code == 200
    
    return res.json()["access_token"]


@pytest.mark.asyncio
async def test_get_me_and_users(client: AsyncClient):
    email = f"{uuid.uuid4().hex}@example.com"
    token = await register(client, "User1", email, "testPassword")

    res = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 200
    assert res.json()["email"] == email

    res = await client.get("/api/v1/users/")
    assert res.status_code == 401

    res = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_create_user_and_duplicate(client: AsyncClient):
    email = f"{uuid.uuid4().hex}@example.com"
    
    res = await client.post(
        "/api/v1/users/",
        json={"name": "User1", "email": email, "password": "testPassword"},
    )
    assert res.status_code == 201
    
    data = res.json()
    assert data["email"] == email
    assert "password" not in data

    res = await client.post(
        "/api/v1/users/",
        json={"name": "User2", "email": email, "password": "testPassword"},
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_get_user_by_id_and_permissions(client: AsyncClient):
    token_admin = await register_and_promote_admin(client)

    email = f"{uuid.uuid4().hex}@example.com"
    token = await register(client, "User1", email, "testPassword")
    me = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    user_id = me.json()["id"]

    res = await client.get(
        f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert res.status_code == 200
    assert res.json()["email"] == email

    res = await client.get(
        f"/api/v1/users/{user_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert res.status_code == 403

    res = await client.get(
        "/api/v1/users/999999",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_promote_and_demote(client: AsyncClient):
    token_admin = await register_and_promote_admin(client)

    token = await register(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    me = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    carol_id = me.json()["id"]

    res = await client.post(
        f"/api/v1/users/{carol_id}/promote",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert res.status_code == 204

    res = await client.get(
        f"/api/v1/users/{carol_id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert res.json()["is_admin"] is True

    res = await client.post(
        f"/api/v1/users/{carol_id}/demote",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert res.status_code == 204

    res = await client.get(
        f"/api/v1/users/{carol_id}",
        headers={"Authorization": f"Bearer {token_admin}"},
    )
    assert res.json()["is_admin"] is False

    res = await client.post(
        f"/api/v1/users/{carol_id}/promote",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_list_all_users_as_admin(client: AsyncClient):
    token_admin = await register_and_promote_admin(client)

    email1 = f"{uuid.uuid4().hex}@example.com"
    await register(client, "User1", email1, "testPassword")
    
    email2 = f"{uuid.uuid4().hex}@example.com"
    await register(client, "User2", email2, "testPassword")

    res = await client.get(
        "/api/v1/users/", headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert res.status_code == 200

    users = res.json()
    assert isinstance(users, list)
    
    assert any(u["email"] == email1 for u in users)
    assert any(u["email"] == email2 for u in users)
