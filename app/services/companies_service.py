from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel
from app.models.user_model import UserModel
from app.schemas.company_schema import CompanyCreate


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


companies_service = CompaniesService()
