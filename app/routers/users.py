from typing import List

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_redis, get_session
from app.schemas.user_schema import SignUpSchema, UserSchema, UserUpdateSchema
from app.services.users_service import user_service

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def get_users(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    users = await user_service.get_all_users(session, redis, limit, offset)
    return users


@router.post("/", response_model=UserSchema)
async def user_create(
    user: SignUpSchema,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    return await user_service.create_user(session, user.model_dump(), redis)


@router.delete("/{user_id}")
async def user_delete(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    return await user_service.delete_user(session, user_id, redis)


@router.get("/{user_id}")
async def user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    return await user_service.get_user_by_id(session, user_id, redis)


@router.patch("/{user_id}")
async def user_update(
    user_id: int,
    user: UserUpdateSchema,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    return await user_service.update_user(user_id, user.model_dump(), session, redis)
