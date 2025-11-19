from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user_model import UserModel
from app.schemas.company_schema import (
    CompanyCreate,
    CompanySchema,
    CompanyUpdate,
    InviteSentSchema,
)
from app.services.companies_service import companies_service
from app.utils.user_util import user_connect

router = APIRouter()


@router.get("/", response_model=List[CompanySchema])
async def show_all_companies(
    limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_session)
):
    companies = await companies_service.get_all_companies(session, limit, offset)
    return companies


@router.get("/{company_id}")
async def show_company(company_id: UUID, session: AsyncSession = Depends(get_session)):
    return await companies_service.get_company(company_id, session)


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


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    return await companies_service.company_delete(company_id, session, current_user)


# ===============================INVITES=======================================


@router.post("/invite")
async def send_invite(
    invite: InviteSentSchema,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.invite_send(invite, current_user, session)


@router.delete("/invite/{invite_id}")
async def cancel_invite(
    invite_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.invite_cancel(invite_id, current_user, session)


# ===============================REQUESTS=======================================


@router.post("/request/{option}/{request_id}")
async def owner_request_switcher(
    request_id: UUID,
    option: str,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.request_owner_switcher(
        request_id, option, current_user, session
    )
