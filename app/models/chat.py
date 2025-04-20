from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models import chat_members


class Chat(Base):
    __tablename__ = 'chats'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True)
    type = Column(String(50), nullable=False)

    participants = relationship(
        "User",
        secondary=chat_members,
        back_populates="chats",
    )
    
    group = relationship(
        'Group',
        back_populates='chat',
        uselist=False,
    )

    messages = relationship(
        'Message',
        back_populates='chat',
        cascade='all, delete-orphan',
    )
