from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel


class UserRepository:
    async def get_all(self, session: AsyncSession, limit: int = 10, offset: int = 0):
        res = await session.execute(select(UserModel).limit(limit).offset(offset))
        return res.scalars().all()

    async def get_by_id(self, session: AsyncSession, user_id: int):
        res = await session.execute(select(UserModel).where(UserModel.id == user_id))
        return res.scalar_one_or_none()

    async def create(self, session: AsyncSession, data: dict):
        user = UserModel(**data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete(self, session: AsyncSession, user: UserModel):
        await session.delete(user)
        await session.commit()

    async def update(self, session: AsyncSession, user: UserModel, data: dict):
        for key, value in data.items():
            setattr(user, key, value)
        await session.commit()
        await session.refresh(user)
        return user

    async def get_by_email(self, session: AsyncSession, email: str) -> UserModel | None:
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        return res.scalar_one_or_none()
