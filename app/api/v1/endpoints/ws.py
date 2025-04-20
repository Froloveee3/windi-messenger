from typing import Dict, List, Optional
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, Security
from fastapi.encoders import jsonable_encoder

from sqlalchemy.ext.asyncio import AsyncSession

from app.services import ChatService, MessageService
from app.models import User as AuthUser
from app.schemas import MessageRead
from app.api.deps import get_current_user_ws
from app.db.session import get_db

router = APIRouter(tags=["ws"])


class ConnectionManager:
    def __init__(self):
        self.active: Dict[int, List[WebSocket]] = {}

    async def connect(self, chat_id: int, ws: WebSocket):
        await ws.accept()
        self.active.setdefault(chat_id, []).append(ws)

    def disconnect(self, chat_id: int, ws: WebSocket):
        conns = self.active.get(chat_id, [])
        if ws in conns:
            conns.remove(ws)
            if not conns:
                del self.active[chat_id]

    async def broadcast(self, chat_id: int, data: dict):
        payload = jsonable_encoder(data)
        for ws in list(self.active.get(chat_id, [])):
            await ws.send_json(payload)


manager = ConnectionManager()


@router.websocket("/{chat_id}")
async def websocket_chat(
    chat_id: int,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(
        get_current_user_ws,
        scopes=["chats:read", "messages:write"]
    ),
):
    user_id = current_user.id
    
    if current_user is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        await ChatService.get_chat(db, chat_id, user_id)
    except ValueError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect(chat_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            try:
                evt = json.loads(raw)
            except json.JSONDecodeError:
                continue

            typ = evt.get("type")

            if typ == "message":
                msg, created = await MessageService.send_message(
                    db,
                    chat_id=chat_id,
                    sender_id=user_id,
                    text=evt["text"],
                    client_msg_id=evt.get("client_msg_id"),
                )
                out = MessageRead.model_validate(msg).model_dump()
                out["type"] = "message"
                
                if created:
                    await manager.broadcast(chat_id, out)
                else:
                    payload = jsonable_encoder(out)
                    await websocket.send_json(payload)

            elif typ == "read":
                notification = await MessageService.mark_read(db, evt.get("message_id"))
                if notification:
                    await manager.broadcast(chat_id, {
                        "type": "read",
                        "message_id": notification.id,
                    })

            else:
                await websocket.send_json({"error": "unknown event type"})

    except WebSocketDisconnect:
        manager.disconnect(chat_id, websocket)
