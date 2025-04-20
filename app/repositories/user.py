from typing import List, Optional
from sqlalchemy import desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User


class UserRepository:
    @staticmethod
    async def get(db: AsyncSession, user_id: int) -> Optional[User]:
        q = select(User).where(User.id == user_id)
        res = await db.execute(q)
        return res.scalar_one_or_none()

    @staticmethod
    async def get_many(db: AsyncSession, ids: List[int]) -> List[User]:
        q = select(User).where(User.id.in_(ids))
        res = await db.execute(q)
        return res.scalars().all()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        q = select(User).where(User.email == email)
        res = await db.execute(q)
        return res.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        name: str,
        email: str,
        hashed_password: str
    ) -> User:
        user = User(name=name, email=email, hashed_password=hashed_password)
        db.add(user)
        await db.flush()
        return user

    @staticmethod
    async def list_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        q = select(User).order_by(desc(User.id)).offset(skip).limit(limit)
        res = await db.execute(q)
        return res.scalars().all()
