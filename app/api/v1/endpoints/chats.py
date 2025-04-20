from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatCreate, ChatRead, MessageRead
from app.services import ChatService, MessageService
from app.models import User as AuthUser
from app.api.deps import get_current_user
from app.db.session import get_db

router = APIRouter(tags=["chats"])
history_router = APIRouter(tags=["history"])


@router.post(
    "/", 
    response_model=ChatRead, 
    status_code=status.HTTP_201_CREATED,
    summary="Create chat (personal/group)",
)
async def create_chat(
    data: ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(get_current_user, scopes=["chats:write"]),
):
    try:
        chat = await ChatService.create_chat(db, data, creator_id=current_user.id)
    except ValueError as e:
        detail = str(e)
        code = status.HTTP_404_NOT_FOUND if detail.startswith("Users not found") else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=code, detail=detail)
    return ChatRead.model_validate(chat)


@router.get(
    "/", 
    response_model=List[ChatRead],
    summary="List of current user's chats",
)
async def list_chats(
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(get_current_user, scopes=["chats:read"]),
):
    chats = await ChatService.list_chats(db, user_id=current_user.id)
    return [ChatRead.model_validate(c) for c in chats]


@router.get(
    "/{chat_id}", 
    response_model=ChatRead,
    summary="Get chat by ID",
)
async def get_chat(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(get_current_user, scopes=["chats:read"]),
):
    try:
        chat = await ChatService.get_chat(db, chat_id, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return ChatRead.model_validate(chat)


@history_router.get(
    "/{chat_id}", 
    response_model=List[MessageRead],
    summary="Message history for chat",
)
async def get_history(
    chat_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: AuthUser = Security(get_current_user, scopes=["messages:read"]),
):
    try:
        msgs = await MessageService.get_history(db, chat_id, user_id=current_user.id, skip=skip, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return msgs
