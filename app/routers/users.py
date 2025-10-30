from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.schemas.user_schema import SignUpSchema, UserSchema
from app.services.users_service import user_service

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def get_users(
    limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_session)
):
    users = await user_service.get_all_users(session, limit, offset)
    return users


@router.post("/", response_model=UserSchema)
async def user_create(user: SignUpSchema, session: AsyncSession = Depends(get_session)):
    return await user_service.create_user(session, user.model_dump())


@router.delete("/{user_id}")
async def user_delete(user_id: int, session: AsyncSession = Depends(get_session)):
    return await user_service.delete_user(session, user_id)
