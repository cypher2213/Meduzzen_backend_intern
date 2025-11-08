from uuid import UUID

from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.models.user_model import UserModel
from app.repository.users_repository import UserRepository
from app.schemas.user_schema import SignUpSchema, UserSchema, UserUpdateSchema
from app.utils.jwt_util import create_access_token

pwd_context = PasswordHash.recommended()


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_all_users(
        self, session: AsyncSession, limit: int = 10, offset: int = 0
    ):
        users = await self.repo.get_all(session, limit, offset)
        if users:
            user_list = [
                UserSchema.model_validate(user).model_dump(mode="json")
                for user in users
            ]
        return user_list or []

    async def create_user(self, session: AsyncSession, user_data: SignUpSchema):
        if "password" in user_data:
            user_data["password"] = pwd_context.hash(user_data["password"])
        user = await self.repo.create(session, user_data.model_dump())
        logger.info(f"User created: id={user.id}, name={user.name}")
        return user

    async def delete_user(self, session: AsyncSession, user_id: UUID):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            logger.warning(f"Attempted delete — user not found: id={user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        await self.repo.delete(session, user)
        logger.info(f"User deleted: id={user_id}, name={user.name}")
        return {"message": f"User with name {user.name} successfully deleted!"}

    async def get_user_by_id(self, session: AsyncSession, user_id: UUID):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User Found", "user": user}

    async def update_user(
        self, user_id: UUID, updated_user: UserUpdateSchema, session: AsyncSession
    ):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        filtered_data = updated_user.model_dump(exclude_none=True)
        updated_user_obj = await self.repo.update(session, user, filtered_data)
        logger.info(f"User updated: id={user.id}")
        return {
            "message": "User updated successfully",
            "id": updated_user_obj.id,
            "name": updated_user_obj.name,
            "email": updated_user_obj.email,
        }

    async def login_user(self, user_data: dict, session: AsyncSession):
        email = user_data.get("email")
        password = user_data.get("password")
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        user = res.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not pwd_context.verify(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": user.email})
        return {"access_token": token, "token_type": "bearer"}


user_service = UserService(UserRepository())
