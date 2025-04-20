from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.repositories import MessageRepository
from app.models import Message, chat_members


class MessageService:
    @staticmethod
    async def send_message(
        db: AsyncSession,
        chat_id: int,
        sender_id: int,
        text: str,
        client_msg_id: Optional[str],
    ) -> Message:
        created = True
        try:
            msg = await MessageRepository.create(
                db,
                chat_id=chat_id,
                sender_id=sender_id,
                text=text,
                client_msg_id=client_msg_id,
            )
            await db.commit()
            await db.refresh(msg)
        except IntegrityError:
            created = False
            await db.rollback()
            msg = await MessageRepository.get_by_client_id(db, chat_id, client_msg_id)
        return msg, created

    @staticmethod
    async def mark_read(
        db: AsyncSession,
        message_id: int,
    ) -> Optional[Message]:
        msg = await MessageRepository.get(db, message_id)
        if msg and not msg.read:
            msg.read = True
            await db.commit()
            await db.refresh(msg)
        return msg

    @staticmethod
    async def get_history(
        db: AsyncSession, 
        chat_id: int, 
        user_id: int, 
        skip=0, 
        limit=100
    ):
        rows = await db.execute(
            select(chat_members.c.user_id)
            .where(chat_members.c.chat_id == chat_id)
        )
        member_ids = {row[0] for row in rows.all()}
        if user_id not in member_ids:
            raise ValueError("Chat not found or access denied")

        res = await db.execute(
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp)
            .offset(skip)
            .limit(limit)
        )
        return res.scalars().all()
