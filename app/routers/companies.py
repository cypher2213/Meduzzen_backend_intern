from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user_model import UserModel
from app.schemas.company_schema import CompanyCreate, CompanyUpdate
from app.services.companies_service import companies_service
from app.utils.user_util import user_connect

router = APIRouter()


@router.post("/")
async def create_company(
    company: CompanyCreate,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    return await companies_service.company_create(company, session, current_user)


@router.patch("/{company_id}")
async def update_company(
    company_id: UUID,
    company: CompanyUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    return await companies_service.company_update(
        company_id, company, session, current_user
    )
