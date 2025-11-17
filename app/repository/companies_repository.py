from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
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
