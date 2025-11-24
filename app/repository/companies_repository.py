from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_invite_request_model import (
    CompanyInviteRequestModel,
    InviteStatus,
    InviteType,
)
from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
from app.models.user_model import UserModel
from app.repository.base_repository import AsyncBaseRepository


class CompaniesRepository(AsyncBaseRepository[CompanyModel]):
    def __init__(self):
        super().__init__(CompanyModel)

    async def get_owner_company(self, db, company_id, user_id):
        result = await db.execute(
            select(CompanyModel)
            .join(CompanyUserRoleModel)
            .where(
                CompanyModel.id == company_id,
                CompanyUserRoleModel.user_id == user_id,
                CompanyUserRoleModel.role == RoleEnum.OWNER,
            )
        )
        return result.scalar_one_or_none()

    async def add_user_role(
        self, db: AsyncSession, user_id: UUID, company_id: UUID, role: RoleEnum
    ):
        owner_role = CompanyUserRoleModel(
            user_id=user_id, company_id=company_id, role=role.value
        )
        db.add(owner_role)
        await db.commit()

    async def get_owner_company_ids(self, db: AsyncSession, user_id):
        result = await db.execute(
            select(CompanyUserRoleModel.company_id).where(
                CompanyUserRoleModel.user_id == user_id,
                CompanyUserRoleModel.role == RoleEnum.OWNER,
            )
        )
        return result.scalars().all()

    async def get_invited_user_ids(self, db: AsyncSession, company_ids: list[int]):
        if not company_ids:
            return []
        result = await db.execute(
            select(CompanyInviteRequestModel.invited_user_id).where(
                CompanyInviteRequestModel.company_id.in_(company_ids),
                CompanyInviteRequestModel.type == InviteType.INVITE,
            )
        )
        return result.scalars().all()

    async def get_pending_requests(self, db: AsyncSession, company_ids: list[int]):
        if not company_ids:
            return []
        result = await db.execute(
            select(CompanyInviteRequestModel).where(
                CompanyInviteRequestModel.company_id.in_(company_ids),
                CompanyInviteRequestModel.status == InviteStatus.PENDING,
                CompanyInviteRequestModel.type == InviteType.REQUEST,
            )
        )
        return result.scalars().all()

    async def get_membership(self, db: AsyncSession, company_id, user_id):
        result = await db.execute(
            select(CompanyUserRoleModel).where(
                CompanyUserRoleModel.company_id == company_id,
                CompanyUserRoleModel.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_users(self, db: AsyncSession, company_id):
        result = await db.execute(
            select(func.count(CompanyUserRoleModel.user_id)).where(
                CompanyUserRoleModel.company_id == company_id
            )
        )
        return result.scalar()

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

    async def get_invite(self, session: AsyncSession, invite_id: UUID):
        result = await session.execute(
            select(CompanyInviteRequestModel).where(
                CompanyInviteRequestModel.id == invite_id
            )
        )
        return result.scalar_one_or_none()

    async def cancel_invite(
        self, session: AsyncSession, invite: CompanyInviteRequestModel
    ):
        invite.status = InviteStatus.CANCELED
        await self.update(session, invite)
        return invite

    async def send_invite(
        self,
        session: AsyncSession,
        company_id: UUID,
        invited_user_id: UUID,
        invited_by_id: UUID,
    ):
        invite = CompanyInviteRequestModel(
            company_id=company_id,
            invited_user_id=invited_user_id,
            invited_by_id=invited_by_id,
            type=InviteType.INVITE,
            status=InviteStatus.PENDING,
        )
        session.add(invite)
        await session.commit()
        await session.refresh(invite)
        return invite

    async def get_users_by_ids(self, db: AsyncSession, user_ids: list[UUID]):
        if not user_ids:
            return []
        result = await db.execute(select(UserModel).where(UserModel.id.in_(user_ids)))
        return result.scalars().all()

    async def get_by_id(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(select(UserModel).where(UserModel.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, session: AsyncSession, user_id: UUID):
        return await session.get(UserModel, user_id)

    async def get_company_by_id(self, session: AsyncSession, company_id: UUID):
        return await session.get(CompanyModel, company_id)
