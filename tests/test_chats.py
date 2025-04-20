import pytest
import uuid
from httpx import AsyncClient


async def register_user(client: AsyncClient, name, email, password):
    await client.post("/api/v1/users/", json={"name": name, "email": email, "password": password})
    token_res = await client.post("/api/v1/auth/token",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"})
    return token_res.json()["access_token"]


@pytest.mark.asyncio
async def test_create_group_and_get_chat(client: AsyncClient):
    token1 = await register_user(client, "GroupOwner", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_user(client, "Member1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token3 = await register_user(client, "Member2", f"{uuid.uuid4().hex}@example.com", "testPassword")

    headers = {"Authorization": f"Bearer {token1}"}
    me1 = await client.get("/api/v1/users/me", headers=headers)
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    me3 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token3}"})

    chat_payload = {
        "name": "My Group",
        "type": "group",
        "participant_ids": [me1.json()["id"], me2.json()["id"], me3.json()["id"]]
    }

    res = await client.post("/api/v1/chats/", json=chat_payload, headers=headers)
    assert res.status_code == 201
    chat_id = res.json()["id"]

    res = await client.get(f"/api/v1/chats/{chat_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["name"] == "My Group"


@pytest.mark.asyncio
async def test_list_chats_for_each_participant(client: AsyncClient):
    token1 = await register_user(client, "Owner", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_user(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token3 = await register_user(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")

    headers1 = {"Authorization": f"Bearer {token1}"}
    ids = []
    for t in (token1, token2, token3):
        me = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {t}"})
        ids.append(me.json()["id"])
    
    payload = {"name": "Party", "type": "group", "participant_ids": ids}
    res = await client.post("/api/v1/chats/", json=payload, headers=headers1)
    assert res.status_code == 201
    
    chat_id = res.json()["id"]
    for token in (token1, token2, token3):
        res = await client.get("/api/v1/chats/", headers={"Authorization": f"Bearer {token}"})
        assert res.status_code == 200
        
        chats = res.json()
        assert any(c["id"] == chat_id and c["name"] == "Party" for c in chats)


@pytest.mark.asyncio
async def test_create_and_list_personal_chat(client: AsyncClient):
    token1 = await register_user(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_user(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")

    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    user1_id, user2_id = me1.json()["id"], me2.json()["id"]

    headers1 = {"Authorization": f"Bearer {token1}"}
    res = await client.post(
        "/api/v1/chats/",
        json={"type": "personal", "participant_ids": [user1_id, user2_id]},
        headers=headers1
    )
    assert res.status_code == 201
    
    chat = res.json()
    assert chat["type"] == "personal"
    
    chat_id = chat["id"]
    for token in (token1, token2):
        res = await client.get("/api/v1/chats/", headers={"Authorization": f"Bearer {token}"})
        assert any(chat["id"] == chat_id and chat["type"] == "personal" for chat in res.json())


@pytest.mark.asyncio
async def test_get_chat_forbidden_if_not_participant(client: AsyncClient):
    token1 = await register_user(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_user(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token3 = await register_user(client, "User3", f"{uuid.uuid4().hex}@example.com", "testPassword")

    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    user1_id, user2_id = me1.json()["id"], me2.json()["id"]
    
    headers1 = {"Authorization": f"Bearer {token1}"}
    res = await client.post(
        "/api/v1/chats/",
        json={"name": "AB only", "type": "group", "participant_ids": [user1_id, user2_id]},
        headers=headers1
    )
    chat_id = res.json()["id"]

    res = await client.get(f"/api/v1/chats/{chat_id}", headers={"Authorization": f"Bearer {token3}"})
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_personal_chat_with_single_participant(client: AsyncClient):
    token1 = await register_user(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    
    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    user1_id = me1.json()["id"]

    headers1 = {"Authorization": f"Bearer {token1}"}
    res = await client.post(
        "/api/v1/chats/",
        json={"type": "personal", "participant_ids": [user1_id]},
        headers=headers1
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_personal_chat_without_creator_in_participants(client: AsyncClient):
    token1 = await register_user(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_user(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token3 = await register_user(client, "User3", f"{uuid.uuid4().hex}@example.com", "testPassword")
    
    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    me3 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token3}"})
    ids = [me2.json()["id"], me3.json()["id"]]

    headers1 = {"Authorization": f"Bearer {token1}"}
    res = await client.post(
        "/api/v1/chats/",
        json={"type": "personal", "participant_ids": ids},
        headers=headers1
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_personal_chat_more_than_two_participants(client: AsyncClient):
    token1 = await register_user(client, "User1", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token2 = await register_user(client, "User2", f"{uuid.uuid4().hex}@example.com", "testPassword")
    token3 = await register_user(client, "User3", f"{uuid.uuid4().hex}@example.com", "testPassword")

    me1 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token1}"})
    me2 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token2}"})
    me3 = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token3}"})
    ids = [me1.json()["id"], me2.json()["id"], me3.json()["id"]]

    headers1 = {"Authorization": f"Bearer {token1}"}
    res = await client.post(
        "/api/v1/chats/",
        json={"type": "personal", "participant_ids": ids},
        headers=headers1
    )
    assert res.status_code == 400
