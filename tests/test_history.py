import pytest
import uuid
from httpx import AsyncClient

from app.models import user


async def register_and_login(client: AsyncClient, name: str, email: str, password: str) -> str:
    await client.post("/api/v1/users/", json={"name": name, "email": email, "password": password})
    token_response = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return token_response.json()["access_token"]


async def create_personal_chat(client: AsyncClient, token: str, user_ids: list[int]) -> int:
    headers = {"Authorization": f"Bearer {token}"}
    resp = await client.post(
        "/api/v1/chats/",
        json={"type": "personal", "participant_ids": user_ids},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


@pytest.mark.asyncio
async def test_history_empty(client: AsyncClient):
    token1 = await register_and_login(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_and_login(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")

    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    user1_id, user2_id = me1.json()["id"], me2.json()["id"]

    chat_id = await create_personal_chat(client, token1, [user1_id, user2_id])

    res = await client.get(
        f"/api/v1/history/{chat_id}",
        headers={"Authorization": f"Bearer {token1}"},
    )
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_history_not_participant(client: AsyncClient):
    token1 = await register_and_login(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_and_login(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token3 = await register_and_login(client, "User3", f"{uuid.uuid4().hex}@example.com", "testPassword")

    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    me3 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token3}"})
    user1_id, user2_id, user3_id = me1.json()["id"], me2.json()["id"], me3.json()["id"]

    chat_id = await create_personal_chat(client, token1, [user1_id, user3_id])

    res = await client.get(
        f"/api/v1/history/{chat_id}",
        headers={"Authorization": f"Bearer {token2}"},
    )
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_history_invalid_chat_id(client: AsyncClient):
    token = await register_and_login(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")

    resp = await client.get(
        "/api/v1/history/9999999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 404
