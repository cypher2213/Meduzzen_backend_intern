from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel
from app.models.user_model import UserModel


class CompaniesRepository:
    async def get_all(self, session: AsyncSession, limit: int = 10, offset: int = 0):
        res = await session.execute(select(CompanyModel).limit(limit).offset(offset))
        return res.scalars().all()

    async def company_get(self, company_id, session):
        res = await session.execute(
            select(CompanyModel).where(CompanyModel.id == company_id)
        )
        return res.scalar_one_or_none()

    async def get_owner_company(self, db, company_id, user_id):
        result = await db.execute(
            select(CompanyModel)
            .join(CompanyUserRoleModel)
            .where(
                CompanyModel.id == company_id,
                CompanyUserRoleModel.user_id == user_id,
                CompanyUserRoleModel.role == "owner",
            )
        )
        return result.scalar_one_or_none()

    async def update_company(self, db: AsyncSession, company: CompanyModel):
        db.add(company)
        await db.commit()
        await db.refresh(company)
        return company

    async def create_company(
        self, db: AsyncSession, name: str, description: str, is_public: bool
    ):
        new_company = CompanyModel(
            name=name,
            description=description,
            is_public=is_public,
        )
        db.add(new_company)
        await db.flush()
        return new_company

    async def add_user_role(
        self, db: AsyncSession, user_id: UUID, company_id: UUID, role: str
    ):
        owner_role = CompanyUserRoleModel(
            user_id=user_id, company_id=company_id, role=role
        )
        db.add(owner_role)
        await db.commit()

    async def delete_company(self, db: AsyncSession, company_id: UUID, user: UserModel):
        res = await db.execute(
            select(CompanyModel)
            .join(CompanyUserRoleModel)
            .where(
                CompanyModel.id == company_id,
                CompanyUserRoleModel.user_id == user.id,
                CompanyUserRoleModel.role == "owner",
            )
        )
        company = res.scalar_one_or_none()
        if not company:
            return None
        await db.delete(company)
        await db.commit()
        return company
