from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert

from app.models import Chat, chat_members


class ChatRepository:
    @staticmethod
    async def get(db: AsyncSession, chat_id: int) -> Chat | None:
        q = select(Chat).where(Chat.id == chat_id)
        res = await db.execute(q)
        return res.scalar_one_or_none()

    @staticmethod
    async def list_all(db: AsyncSession) -> list[Chat]:
        res = await db.execute(select(Chat))
        return res.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, name: str | None, type_: str) -> Chat:
        chat = Chat(name=name, type=type_)
        db.add(chat)
        await db.flush()
        return chat

    @staticmethod
    async def add_participants(db: AsyncSession, chat_id: int, user_ids: list[int]):
        stmt = insert(chat_members).values([
            {"chat_id": chat_id, "user_id": uid} for uid in user_ids
        ])
        await db.execute(stmt)
