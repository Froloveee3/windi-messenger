from datetime import datetime, timezone

from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime, Boolean, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import Base


class Message(Base):
    __tablename__ = 'messages'
    __table_args__ = (
        UniqueConstraint('chat_id', 'client_msg_id', name='unique_chat_client_msg'),
    )

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    client_msg_id = Column(String(36), nullable=True, index=True)
    read = Column(Boolean, default=False, nullable=False)

    chat = relationship('Chat', back_populates='messages')
    sender = relationship('User', back_populates='messages')
