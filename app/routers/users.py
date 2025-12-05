from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.user_model import UserModel
from app.schemas.company_schema import RequestSentSchema
from app.schemas.user_schema import (
    AnswerUserSchema,
    LoginResponseSchema,
    RefreshResponseSchema,
    SignInSchema,
    SignUpSchema,
    UpdateUserResponseSchema,
    UserAverageScoreResponse,
    UserSchema,
    UserUpdateSchema,
)
from app.services.users_service import user_service
from app.utils.user_util import user_connect

router = APIRouter()


@router.get("/", response_model=List[UserSchema])
async def get_users(
    limit: int = 10,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    users = await user_service.get_all_users(session, limit, offset)
    return users


@router.post("/", response_model=UserSchema)
async def user_create(
    user: SignUpSchema,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.create_user(session, user)


@router.get("/me", response_model=UserSchema)
async def get_current_user(user: UserModel = Depends(user_connect)):
    return {
        "id": user.id,
        "name": user.email.split("@")[0].capitalize(),
        "email": user.email,
        "age": user.age,
    }


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def user_delete(
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    return await user_service.delete_user(session, current_user)


@router.get("/{user_id}")
async def user_by_id(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.get_user_by_id(session, user_id)


@router.patch("/me", response_model=UpdateUserResponseSchema)
async def user_update(
    user: UserUpdateSchema,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    return await user_service.update_user(user, session, current_user)


@router.post("/login", response_model=LoginResponseSchema)
async def user_login(user: SignInSchema, session: AsyncSession = Depends(get_session)):
    return await user_service.login_user(user.model_dump(), session)


@router.post("/refresh", response_model=RefreshResponseSchema)
async def user_refresh_token(refresh_token: str):
    return await user_service.refresh_access_token(refresh_token)


# ======================INVITES AND REQUESTS=================


@router.post("/me/{option}/{invite_id}")
async def user_invite_switcher(
    invite_id: UUID,
    option: str,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.invite_user_switcher(
        invite_id, option, current_user, session
    )


@router.post("/me/request")
async def send_request(
    request: RequestSentSchema,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.request_send(request, current_user, session)


@router.patch("/me/request/{request_id}")
async def cancel_request(
    request_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.request_cancel(request_id, current_user, session)


@router.delete("/me/leave/{company_id}")
async def user_leave(
    company_id: UUID,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.leave_user(company_id, current_user, session)


# ========================MANAGING REQUESTS=========


@router.get("/me/requests")
async def user_show_requests(
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.show_user_requests(current_user, session)


@router.get("/me/invites")
async def user_show_invites(
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.show_user_invites(current_user, session)


# ======================== ANSWER THE QUESTION ==============================


@router.post("/me/{company_id}/{quiz_id}/{question_id}")
async def user_answer_question(
    company_id: UUID,
    question_id: UUID,
    quiz_id: UUID,
    answers: AnswerUserSchema,
    current_user: UserModel = Depends(user_connect),
    session: AsyncSession = Depends(get_session),
):
    return await user_service.question_answer_by_user(
        company_id, question_id, quiz_id, answers, current_user, session
    )


@router.get("/me/stat", response_model=UserAverageScoreResponse)
async def get_my_global_statistic(
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    score = await user_service.get_my_statistic(
        session=session,
        user_id=current_user.id,
    )
    return UserAverageScoreResponse(average_score=score, company_id=None)


@router.get("/me/stat/{company_id}", response_model=UserAverageScoreResponse)
async def get_my_company_statistic(
    company_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(user_connect),
):
    score = await user_service.get_my_statistic(
        session=session, user_id=current_user.id, company_id=company_id
    )
    return UserAverageScoreResponse(average_score=score, company_id=company_id)
