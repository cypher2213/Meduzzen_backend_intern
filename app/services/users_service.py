from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user_model import UserModel


class UserSerivce:
    async def get_all_users(
        self, session: AsyncSession, limit: int = 10, offset: int = 0
    ):
        res = await session.execute(select(UserModel).limit(limit).offset(offset))
        users = res.scalars().all()
        return users or []

    async def create_user(self, session: AsyncSession, user_data: dict):
        user = UserModel(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


user_serice = UserSerivce()
