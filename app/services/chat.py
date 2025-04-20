from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.repositories import ChatRepository, UserRepository, GroupRepository
from app.schemas import ChatCreate
from app.models import Chat


class ChatService:
    @staticmethod
    async def create_chat(
        db: AsyncSession,
        data: ChatCreate,
        creator_id: int
    ) -> Chat:
        users = await UserRepository.get_many(db, data.participant_ids)
        if len(users) != len(data.participant_ids):
            missing = set(data.participant_ids) - {u.id for u in users}
            raise ValueError(f"Users not found: {missing}")

        if data.type == "personal" and len(users) != 2:
            raise ValueError("Personal chat must have exactly 2 participants")

        if creator_id not in {u.id for u in users}:
            me = await UserRepository.get(db, creator_id)
            users.append(me)
            
        if data.type == "personal" and len(users) != 2:
            raise ValueError("Personal chat must have creator in participants")

        chat = await ChatRepository.create(db, data.name, data.type)
        user_ids = [u.id for u in users]
        await ChatRepository.add_participants(db, chat.id, user_ids)

        if data.type == "group":
            await GroupRepository.create(
                db,
                chat_id=chat.id,
                name=data.name or "",
                creator_id=creator_id,
                user_ids=user_ids,
            )

        await db.commit()

        result = await db.execute(
            select(Chat)
            .where(Chat.id == chat.id)
            .options(selectinload(Chat.participants))
        )
        return result.scalar_one()

    @staticmethod
    async def list_chats(db: AsyncSession, user_id: int) -> List[Chat]:
        from app.models import chat_members

        result = await db.execute(
            select(Chat)
            .join(chat_members, Chat.id == chat_members.c.chat_id)
            .where(chat_members.c.user_id == user_id)
            .options(selectinload(Chat.participants))
        )
        return result.scalars().all()

    @staticmethod
    async def get_chat(db: AsyncSession, chat_id: int, user_id: int) -> Chat:
        from app.models import chat_members

        result = await db.execute(
            select(Chat)
            .where(Chat.id == chat_id)
            .join(chat_members, Chat.id == chat_members.c.chat_id)
            .where(chat_members.c.user_id == user_id)
            .options(selectinload(Chat.participants))
        )
        chat = result.scalar_one_or_none()
        if not chat:
            raise ValueError("Chat not found or access denied")
        return chat
