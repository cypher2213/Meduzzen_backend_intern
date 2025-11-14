from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel
from app.models.user_model import UserModel
from app.schemas.company_schema import CompanyCreate, CompanyUpdate


class CompaniesService:
    async def company_create(
        self, company: CompanyCreate, db: AsyncSession, user: UserModel
    ):
        new_company = CompanyModel(
            name=company.name,
            description=company.description,
            is_public=company.is_public,
        )
        db.add(new_company)
        await db.flush()

        owner_role = CompanyUserRoleModel(
            user_id=user.id, company_id=new_company.id, role="owner"
        )
        db.add(owner_role)
        await db.commit()
        await db.refresh(new_company)
        return {
            "message": f"Company created successfully by {user.name}.",
            "company": new_company,
        }

    async def company_update(
        self,
        company_id: UUID,
        company_data: CompanyUpdate,
        db: AsyncSession,
        user: UserModel,
    ):
        result = await db.execute(
            select(CompanyModel)
            .join(CompanyUserRoleModel)
            .where(
                CompanyModel.id == company_id,
                CompanyUserRoleModel.user_id == user.id,
                CompanyUserRoleModel.role == "owner",
            )
        )
        company = result.scalar_one_or_none()

        if not company:
            raise HTTPException(
                status_code=403,
                detail="You are not the owner of this company or it does not exist.",
            )
        for field, value in company_data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)

        db.add(company)
        await db.commit()
        await db.refresh(company)

        return {
            "message": f"Company {company.name} updated successfully.",
            "company": company,
        }


companies_service = CompaniesService()
