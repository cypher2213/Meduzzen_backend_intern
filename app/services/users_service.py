import json

from fastapi import HTTPException
from pwdlib import PasswordHash
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logger import logger
from app.db.users_repository import UserRepository
from app.schemas.user_schema import UserSchema

pwd_context = PasswordHash.recommended()


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_all_users(
        self, session: AsyncSession, redis: Redis, limit: int = 10, offset: int = 0
    ):
        cache_key = f"users:{limit}:{offset}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            logger.info("Users fetched from redis cache")
            return json.loads(cached_data)
        users = await self.repo.get_all(session, limit, offset)
        if users:
            user_list = [UserSchema.model_validate(user).model_dump() for user in users]
            await redis.set(cache_key, json.dumps(user_list), ex=300)
            logger.info("Users cached in redis")
        return users or []

    async def create_user(self, session: AsyncSession, user_data: dict, redis: Redis):
        if "password" in user_data:
            user_data["password"] = pwd_context.hash(user_data["password"])
        user = await self.repo.create(session, user_data)
        await redis.delete(f"user:{user.id}")
        async for key in redis.scan_iter("users:*"):
            await redis.delete(key)
        logger.info(f"User created: id={user.id}, name={user.name}")
        return user

    async def delete_user(self, session: AsyncSession, user_id: int, redis: Redis):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            logger.warning(f"Attempted delete — user not found: id={user_id}")
            raise HTTPException(status_code=404, detail="User not found")
        await self.repo.delete(session, user)
        await redis.delete(f"user:{user_id}")
        async for key in redis.scan_iter("users:*"):
            await redis.delete(key)
        logger.info(f"User deleted: id={user_id}, name={user.name}")
        return {"message": f"User with name {user.name} successfully deleted!"}

    async def get_user_by_id(self, session: AsyncSession, user_id: int, redis: Redis):
        cache_key = f"user:{user_id}"
        cached_data = await redis.get(cache_key)
        if cached_data:
            logger.info("User fetched from redis cache")
            return json.loads(cached_data)
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user_dict = UserSchema.model_validate(user).model_dump()
        await redis.set(cache_key, json.dumps(user_dict), ex=300)
        logger.info("User cached in redis")
        return {"message": "User Found", "user": user}

    async def update_user(
        self, user_id: int, updated_user: dict, session: AsyncSession, redis: Redis
    ):
        user = await self.repo.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        filtered_data = {k: v for k, v in updated_user.items() if v is not None}
        updated_user_obj = await self.repo.update(session, user, filtered_data)
        await redis.delete(f"user:{user_id}")
        async for key in redis.scan_iter("users:*"):
            await redis.delete(key)
        logger.info(f"User updated: id={user.id}")
        return {
            "message": "User updated successfully",
            "id": updated_user_obj.id,
            "name": updated_user_obj.name,
            "email": updated_user_obj.email,
        }


user_service = UserService(UserRepository())
