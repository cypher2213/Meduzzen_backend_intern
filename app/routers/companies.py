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
    QuestionUpdate,
    QuizCreate,
    QuizUpdate,
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


# =========================MANAGING INVITES AND REQUESTS=========


@router.get("/invites")
async def owner_list_invite(
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.invite_owner_list(current_user, session)


@router.get("/requests/pending")
async def owner_pending_requests(
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.pending_requests_list(current_user, session)


@router.get("/{company_id}/users")
async def get_company_users(
    company_id: UUID,
    limit: int = 20,
    offset: int = 0,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.list_company_users(
        company_id=company_id,
        limit=limit,
        offset=offset,
        current_user=current_user,
        session=session,
    )


# ==================================MANAGIN COMPANIES==============
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


@router.patch("/invite/{invite_id}")
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


@router.delete("/remove/{company_id}/{user_id}")
async def owner_remove_user(
    user_id: UUID,
    company_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.remove_user_by_owner(
        user_id, company_id, current_user, session
    )


# ==================================ADMIN ROLE==============================================


@router.get("/admins/{company_id}")
async def list_admin(
    company_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.admin_list(company_id, current_user, session)


@router.post("/admin/add/{company_id}/{user_id}")
async def add_admin(
    user_id: UUID,
    company_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.admin_add(user_id, company_id, current_user, session)


@router.post("/admin/remove/{company_id}/{user_id}")
async def remove_admin_role(
    user_id: UUID,
    company_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.admin_role_remove(
        user_id, company_id, current_user, session
    )


# ==========================================Quizzes MANAGEMENT=============================
@router.post("/quiz/{company_id}")
async def create_company_quiz(
    company_id: UUID,
    quiz_data: QuizCreate,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.company_create_quiz(
        company_id, quiz_data, current_user, session
    )


@router.delete("/quiz/{company_id}/{quiz_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_quiz(
    company_id: UUID,
    quiz_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.company_delete_quiz(
        company_id, quiz_id, current_user, session
    )


@router.delete(
    "/question/{company_id}/{quiz_id}/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_quiz_question(
    company_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.company_delete_question(
        company_id, quiz_id, question_id, current_user, session
    )


@router.patch("/quiz/{company_id}/{quiz_id}")
async def edit_company_quiz(
    company_id: UUID,
    quiz_id: UUID,
    quiz_data: QuizUpdate,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.company_edit_quiz(
        company_id, quiz_id, quiz_data, current_user, session
    )


@router.patch("/question/{company_id}/{quiz_id}/{question_id}")
async def edit_quiz_question(
    company_id: UUID,
    quiz_id: UUID,
    question_id: UUID,
    question_data: QuestionUpdate,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.quiz_edit_question(
        company_id, quiz_id, question_id, question_data, current_user, session
    )


@router.get("/quizzes/{company_id}")
async def company_all_quizzes(
    company_id: UUID,
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    return await companies_service.company_all_quizzes(
        company_id=company_id, session=session, limit=limit, offset=offset
    )
