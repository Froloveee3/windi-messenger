from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models import chat_members, group_members


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)

    chats = relationship(
        "Chat",
        secondary=chat_members,
        back_populates="participants",
    )
    
    groups = relationship(
        'Group',
        secondary=group_members,
        back_populates='participants',
    )

    messages = relationship(
        'Message',
        back_populates='sender',
        cascade='all, delete-orphan',
    )
