from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.user_model import UserModel

pwd_context = PasswordHash.recommended()


class UserSerivce:
    async def get_all_users(
        self, session: AsyncSession, limit: int = 10, offset: int = 0
    ):
        res = await session.execute(select(UserModel).limit(limit).offset(offset))
        users = res.scalars().all()
        return users or []

    async def create_user(self, session: AsyncSession, user_data: dict):
        if "password" in user_data:
            user_data["password"] = pwd_context.hash(user_data["password"])
        user = UserModel(**user_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(self, session: AsyncSession, user_id: int):
        res = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()

        return {f"message: User with name {user.name} successfully deleted!"}

    async def get_user_by_id(self, session: AsyncSession, user_id: int):
        res = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User Found", "user": {user}}

    async def update_user(
        self, user_id: int, updated_user: dict, session: AsyncSession
    ):
        res = await session.execute(select(UserModel).where(UserModel.id == user_id))
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if "password" in updated_user:
            new_pswrd = updated_user.pop("password")
            if new_pswrd is not None:
                updated_user["password"] = pwd_context.hash(str(new_pswrd))
        filtered_data = {k: v for k, v in updated_user.items() if v is not None}
        for key, value in filtered_data.items():
            setattr(user, key, value)

        await session.commit()
        await session.refresh(user)
        return user


user_service = UserSerivce()
