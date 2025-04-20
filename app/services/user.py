from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.core.security import hash_password
from app.repositories import UserRepository
from app.schemas import UserCreate
from app.models import User


class UserService:
    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        existing = await UserRepository.get_by_email(db, user_in.email)
        if existing:
            raise ValueError("Email already registered")

        hashed_pwd = hash_password(user_in.password)

        try:
            user = await UserRepository.create(db, name=user_in.name, email=user_in.email, hashed_password=hashed_pwd)
            await db.commit()
            await db.refresh(user)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Email already registered")

        return user

    @staticmethod
    async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        return await UserRepository.list_all(db, skip=skip, limit=limit)

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> User:
        user = await UserRepository.get(db, user_id)
        if not user:
            raise ValueError("User not found")
        return user
    
    @staticmethod
    async def set_admin(db: AsyncSession, user_id: int, is_admin: bool) -> None:
        user = await UserRepository.get(db, user_id)
        if not user:
            raise ValueError("User not found")
        user.is_admin = is_admin
        await db.commit()
