from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_invites_model import (
    CompanyInvitesModel,
    InviteStatus,
    InviteType,
)
from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel
from app.models.user_model import UserModel
from app.repository.base_repository import AsyncBaseRepository


class UserRepository(AsyncBaseRepository[UserModel]):
    def __init__(self):
        super().__init__(UserModel)

    async def get_by_email(self, session: AsyncSession, email: str) -> UserModel | None:
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        return res.scalar_one_or_none()

    async def get_users_with_roles(
        self, db: AsyncSession, company_id, limit: int, offset: int
    ):
        result = await db.execute(
            select(UserModel, CompanyUserRoleModel.role)
            .join(CompanyUserRoleModel, CompanyUserRoleModel.user_id == UserModel.id)
            .where(CompanyUserRoleModel.company_id == company_id)
            .offset(offset)
            .limit(limit)
        )
        return result.all()

    async def get_user_role(self, db: AsyncSession, company_id: UUID, user_id: UUID):
        result = await db.execute(
            select(CompanyUserRoleModel).where(
                CompanyUserRoleModel.company_id == company_id,
                CompanyUserRoleModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete_user_role(self, db: AsyncSession, user_role: CompanyUserRoleModel):
        await db.delete(user_role)
        await db.commit()

    async def get_user_requests(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(
            select(CompanyInvitesModel).where(
                CompanyInvitesModel.invited_user_id == user_id,
                CompanyInvitesModel.type == InviteType.REQUEST,
            )
        )
        return result.scalars().all()

    async def get_user_invites(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(
            select(CompanyInvitesModel).where(
                CompanyInvitesModel.invited_user_id == user_id,
                CompanyInvitesModel.type == InviteType.INVITE,
            )
        )
        return result.scalars().all()

    async def get_company(self, session: AsyncSession, company_id: UUID):
        seek_company = await session.execute(
            select(CompanyModel).where(CompanyModel.id == company_id)
        )
        return seek_company.scalar_one_or_none()

    async def get_invite(self, session: AsyncSession, invite_id: UUID):
        result = await session.execute(
            select(CompanyInvitesModel).where(CompanyInvitesModel.id == invite_id)
        )
        return result.scalar_one_or_none()
