from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from app.models import Group, group_members


class GroupRepository:
    @staticmethod
    async def create(
        db: AsyncSession,
        chat_id: int,
        name: str,
        creator_id: int,
        user_ids: list[int],
    ) -> Group:
        grp = Group(id=chat_id, name=name, creator_id=creator_id)
        db.add(grp)
        await db.flush()

        stmt = insert(group_members).values([
            {"group_id": chat_id, "user_id": uid} for uid in user_ids
        ])
        await db.execute(stmt)
        return grp
