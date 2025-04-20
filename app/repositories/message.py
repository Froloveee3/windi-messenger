from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Message

class MessageRepository:
    @staticmethod
    async def get_by_client_id(db: AsyncSession, chat_id: int, client_msg_id: str) -> Message | None:
        q = select(Message).where(
            Message.chat_id == chat_id,
            Message.client_msg_id == client_msg_id
        )
        res = await db.execute(q)
        return res.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> Message:
        msg = Message(**kwargs)
        db.add(msg)
        return msg

    @staticmethod
    async def get(db: AsyncSession, message_id: int) -> Message | None:
        q = select(Message).where(Message.id == message_id)
        res = await db.execute(q)
        return res.scalar_one_or_none()
