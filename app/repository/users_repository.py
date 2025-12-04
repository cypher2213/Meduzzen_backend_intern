from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_invite_request_model import (
    CompanyInviteRequestModel,
    InviteStatus,
    InviteType,
)
from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
from app.models.results import QuizResults
from app.models.user_model import UserModel
from app.repository.base_repository import AsyncBaseRepository


class UserRepository(AsyncBaseRepository[UserModel]):
    def __init__(self):
        super().__init__(UserModel)

    async def get_by_email(self, session: AsyncSession, email: str) -> UserModel | None:
        res = await session.execute(select(UserModel).where(UserModel.email == email))
        return res.scalar_one_or_none()

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

    async def get_user_requests(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(
            select(CompanyInviteRequestModel).where(
                CompanyInviteRequestModel.invited_user_id == user_id,
                CompanyInviteRequestModel.type == InviteType.REQUEST,
            )
        )
        return result.scalars().all()

    async def get_user_invites(self, session: AsyncSession, user_id: UUID):
        result = await session.execute(
            select(CompanyInviteRequestModel).where(
                CompanyInviteRequestModel.invited_user_id == user_id,
                CompanyInviteRequestModel.type == InviteType.INVITE,
            )
        )
        return result.scalars().all()

    async def get_company(self, session: AsyncSession, company_id: UUID):
        seek_company = await session.execute(
            select(CompanyModel).where(CompanyModel.id == company_id)
        )
        return seek_company.scalar_one_or_none()

    async def get_invite(self, session: AsyncSession, invite_id: UUID):
        result = await session.execute(
            select(CompanyInviteRequestModel).where(
                CompanyInviteRequestModel.id == invite_id
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

    async def send_request(
        self,
        db: AsyncSession,
        company_id: UUID,
        invited_user_id: UUID,
    ):
        request_obj = CompanyInviteRequestModel(
            company_id=company_id,
            invited_user_id=invited_user_id,
            invited_by_id=None,
            type=InviteType.REQUEST,
            status=InviteStatus.PENDING,
        )
        db.add(request_obj)
        await db.commit()
        await db.refresh(request_obj)
        return request_obj

    async def get_result_by_user_question(
        self, session: AsyncSession, user_id: UUID, question_id: UUID
    ):
        stmt = select(QuizResults).where(
            QuizResults.user_id == user_id, QuizResults.question_id == question_id
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_result(
        self, session: AsyncSession, result: QuizResults
    ) -> QuizResults:
        session.add(result)
        await session.commit()
        await session.refresh(result)
        return result

    async def get_user_average_score(
        self, session: AsyncSession, user_id: UUID, company_id: UUID | None = None
    ) -> float:
        stmt = (
            select(QuizResults)
            .join(QuizResults.quiz)
            .where(QuizResults.user_id == user_id, QuizResults.is_done)
        )
        if company_id:
            stmt = stmt.where(QuizResults.company_id == company_id)

        results = (await session.execute(stmt)).scalars().all()

        total_correct = 0
        total_answered = 0

        for res in results:
            question = res.question
            if hasattr(res, "selected_answers"):
                if set(res.selected_answers) == set(question.correct_answers):
                    total_correct += 1
            total_answered += 1

        if total_answered == 0:
            return 0.0

        return total_correct / total_answered * 100
