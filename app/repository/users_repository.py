from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.repository.base_repository import AsyncBaseRepository


class UserRepository(AsyncBaseRepository[UserModel]):
    def __init__(self):
        super().__init__(UserModel)

    async def get_by_email(self, session: AsyncSession, email: str) -> UserModel | None:
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        return res.scalar_one_or_none()
