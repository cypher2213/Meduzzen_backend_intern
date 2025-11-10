from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user_model import UserModel
from app.schemas.user_schema import (
    SignInSchema,
    SignUpSchema,
    UserSchema,
    UserUpdateSchema,
)
from app.services.users_service import user_service
from app.utils.user_util import user_connect

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def get_users(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    users = await user_service.get_all_users(session, limit, offset)
    return users


@router.post("/", response_model=UserSchema)
async def user_create(
    user: SignUpSchema,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.create_user(session, user)


@router.get("/me")
async def get_current_user(user: UserModel = Depends(user_connect)):
    return {"message": f"Hello,{user.email}.You are authenticated successfully!"}


@router.delete("/{user_id}")
async def user_delete(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.delete_user(session, user_id)


@router.get("/{user_id}")
async def user_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.get_user_by_id(session, user_id)


@router.patch("/{user_id}")
async def user_update(
    user_id: UUID,
    user: UserUpdateSchema,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.update_user(user_id, user, session)


@router.post("/login")
async def user_login(user: SignInSchema, session: AsyncSession = Depends(get_session)):
    return await user_service.login_user(user.model_dump(), session)
