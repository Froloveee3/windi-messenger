from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship

from app.models.base import Base
from app.models.associations import group_members


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, ForeignKey('chats.id', ondelete='CASCADE'), primary_key=True)
    name = Column(String(255), nullable=True)
    creator_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    chat = relationship(
        'Chat',
        back_populates='group',
    )

    participants = relationship(
        'User',
        secondary=group_members,
        back_populates='groups',
    )
