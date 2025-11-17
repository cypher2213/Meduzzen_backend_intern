from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_user_role_model import RoleEnum
from app.models.user_model import UserModel
from app.repository.companies_repository import CompaniesRepository
from app.schemas.company_schema import CompanyCreate, CompanySchema, CompanyUpdate


class CompaniesService:
    def __init__(self, repo: CompaniesRepository):
        self.repo = repo

    async def get_all_companies(
        self, session: AsyncSession, limit: int = 10, offset: int = 0
    ):
        companies = await self.repo.get_all(session, limit, offset)
        if companies:
            company_list = [
                CompanySchema.model_validate(company).model_dump(mode="json")
                for company in companies
            ]
        return company_list or []

    async def get_company(self, company_id: UUID, session: AsyncSession):
        company = await self.repo.company_get(company_id, session)
        if not company:
            raise HTTPException(
                status_code=404,
                detail="Company not found",
            )
        return {"message": "Company successfully found!", "company": company}

    async def company_create(
        self, company_data: CompanyCreate, db: AsyncSession, user: UserModel
    ):
        new_company = await self.repo.create_company(
            db=db,
            name=company_data.name,
            description=company_data.description,
            is_public=company_data.is_public,
        )
        await self.repo.add_user_role(
            db=db, user_id=user.id, company_id=new_company.id, role=RoleEnum.OWNER
        )
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
        company = await self.repo.get_owner_company(db, company_id, user.id)
        if not company:
            raise HTTPException(
                status_code=403,
                detail="You are not the owner of this company or it does not exist.",
            )
        for field, value in company_data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)

        updated_company = await self.repo.update_company(db, company)

        return {
            "message": f"Company {updated_company.name} updated successfully.",
            "company": updated_company,
        }

    async def company_delete(self, company_id: UUID, db: AsyncSession, user: UserModel):
        company = await self.repo.delete_company(db, company_id, user)
        if not company:
            raise HTTPException(
                status_code=403,
                detail="You are not the owner of this company or it does not exist.",
            )


companies_service = CompaniesService(CompaniesRepository())
