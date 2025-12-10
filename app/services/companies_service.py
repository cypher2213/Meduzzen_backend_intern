from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.company_exceptions import (
    CompanyNotFoundError,
    MemberNotFoundError,
    OwnerAndAdminOnlyActionError,
    OwnerOnlyActionError,
    UserAlreadyAdminException,
    UserAlreadyOwnerException,
)
from app.core.invites_exceptions import (
    InvalidInviteStatusError,
    InviteInvalidOptionError,
    InviteNotFoundError,
)
from app.core.quiz_exceptions import (
    FewOptionsException,
    FewQuestionsException,
    NotEnoughOptionsException,
    QuestionNotFoundException,
    QuizNotFoundException,
)
from app.core.users_exceptions import PermissionDeniedError, UserNotFoundError
from app.models.company_invite_request_model import InviteStatus
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
from app.models.quiz_model import QuizModel
from app.models.user_model import UserModel
from app.repository.companies_repository import CompaniesRepository
from app.schemas.company_schema import (
    CompanyCreate,
    CompanySchema,
    CompanyUpdate,
    InviteSentSchema,
    QuestionCreateSchema,
    QuestionUpdate,
    QuizCreate,
    QuizUpdate,
    QuizzesList,
    UserWithRoleSchema,
)


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
        company = await self.repo.get(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)
        return {"message": "Company successfully found!", "company": company}

    async def company_create(
        self, company_data: CompanyCreate, db: AsyncSession, user: UserModel
    ):
        new_company = await self.repo.create(db, data=company_data.model_dump())
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
            raise PermissionDeniedError(
                "You are not the owner of this company or it does not exist."
            )
        for field, value in company_data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)

        updated_company = await self.repo.update(db, company)

        return {
            "message": f"Company {updated_company.name} updated successfully.",
            "company": updated_company,
        }

    async def company_delete(self, company_id: UUID, db: AsyncSession, user: UserModel):
        company = await self.repo.get_owner_company(db, company_id, user.id)
        if not company:
            raise PermissionDeniedError(
                "You are not the owner of this company or it does not exist."
            )
        await self.repo.delete(db, company)

    # ========================INVITES====================

    async def invite_send(
        self, invite_data: InviteSentSchema, user: UserModel, session: AsyncSession
    ):
        invited_user = await self.repo.get_by_id(session, invite_data.invited_user_id)

        if not invited_user:
            raise UserNotFoundError(invite_data.invited_user_id)

        company = await self.repo.get_company_by_id(session, invite_data.company_id)

        if not company:
            raise CompanyNotFoundError(invite_data.company_id)
        membership = await self.repo.get_membership(
            session, invite_data.company_id, user.id
        )
        if not membership or membership.role != RoleEnum.OWNER:
            raise OwnerOnlyActionError()

        invite = await self.repo.send_invite(
            session,
            company_id=invite_data.company_id,
            invited_user_id=invite_data.invited_user_id,
            invited_by_id=user.id,
        )

        return {
            "message": f"Successfully sent invitation to {invited_user.name} with id {invite.invited_user_id}"
        }

    async def invite_cancel(
        self, invite_id: UUID, user: UserModel, session: AsyncSession
    ):
        invite = await self.repo.get_invite(session, invite_id)
        if not invite:
            raise InviteNotFoundError(invite_id)
        if invite.invited_by_id != user.id:
            raise PermissionDeniedError(
                "You are not allowed to cancel this invitation."
            )
        await self.repo.cancel_invite(session, invite)
        return {"message": "Invitation canceled successfully!"}

    async def request_owner_switcher(
        self,
        request_id: UUID,
        option: str,
        current_user: UserModel,
        session: AsyncSession,
    ):
        invite = await self.repo.get_invite(session, request_id)
        if not invite:
            raise InviteNotFoundError(request_id)
        if invite.status != InviteStatus.PENDING:
            raise InvalidInviteStatusError(invite.status)

        membership = await self.repo.get_membership(
            session, invite.company_id, current_user.id
        )

        if not membership or membership.role != RoleEnum.OWNER:
            raise OwnerOnlyActionError()
        if option not in (InviteStatus.ACCEPTED, InviteStatus.DECLINED):
            raise InviteInvalidOptionError()
        if option == InviteStatus.ACCEPTED:
            invite.status = InviteStatus.ACCEPTED
            user_role = CompanyUserRoleModel(
                user_id=invite.invited_user_id,
                company_id=invite.company_id,
                role=RoleEnum.MEMBER,
            )
            session.add(user_role)
        elif option == InviteStatus.DECLINED:
            invite.status = InviteStatus.DECLINED

        await self.repo.update(session, invite)

        return {"message": f"You have successfully {option} request"}

    async def remove_user_by_owner(
        self,
        user_id: UUID,
        company_id: UUID,
        current_user: UserModel,
        session: AsyncSession,
    ):
        current_role = await self.repo.get_user_role(
            session, company_id, current_user.id
        )
        if not current_role or current_role.role != RoleEnum.OWNER:
            raise OwnerOnlyActionError()

        user_role = await self.repo.get_user_role(session, company_id, user_id)
        if not user_role:
            raise MemberNotFoundError(user_id)

        if user_role.role != RoleEnum.MEMBER:
            raise InvalidInviteStatusError("Owner cannot be removed")

        await self.repo.delete_user_role(session, user_role)

        return {"message": "User deleted successfully!"}

    # ========================MANAGING INVITES=========
    async def invite_owner_list(self, current_user: UserModel, session: AsyncSession):
        owner_company_ids = await self.repo.get_owner_company_ids(
            session, current_user.id
        )
        if not owner_company_ids:
            raise OwnerOnlyActionError()

        invited_user_ids = await self.repo.get_invited_user_ids(
            session, owner_company_ids
        )
        if not invited_user_ids:
            return {"message": "No invited users", "users": []}

        users = await self.repo.get_users_by_ids(session, invited_user_ids)

        return {"message": "Successfully found invited users", "users": users}

    async def pending_requests_list(
        self, current_user: UserModel, session: AsyncSession
    ):
        owner_company_ids = await self.repo.get_owner_company_ids(
            session, current_user.id
        )
        if not owner_company_ids:
            raise OwnerOnlyActionError()

        pending_requests = await self.repo.get_pending_requests(
            session, owner_company_ids
        )
        if not pending_requests:
            return {"message": "No pending membership requests", "requests": []}

        return {
            "message": "Successfully found pending membership requests",
            "requests": pending_requests,
        }

    async def list_company_users(
        self,
        company_id: UUID,
        limit: int,
        offset: int,
        current_user: UserModel,
        session: AsyncSession,
    ):
        membership = await self.repo.get_membership(
            session, company_id, current_user.id
        )
        if not membership:
            raise PermissionDeniedError("You do not have access to this company")

        total = await self.repo.count_users(session, company_id)

        rows = await self.repo.get_users_with_roles(session, company_id, limit, offset)

        users = [
            UserWithRoleSchema(
                id=user.id,
                email=user.email,
                name=user.name,
                age=getattr(user, "age", None),
                created_at=getattr(user, "created_at", None),
                updated_at=getattr(user, "updated_at", None),
                role=role,
            )
            for user, role in rows
        ]

        return {
            "company_id": str(company_id),
            "total_users": total,
            "limit": limit,
            "offset": offset,
            "users": users,
        }

    # ============================================ADMIN MANAGMENT==================/

    async def admin_list(
        self, company_id: UUID, current_user: UserModel, session: AsyncSession
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)
        owner_company_ids = await self.repo.get_owner_company_ids(
            session, current_user.id
        )
        if company_id not in owner_company_ids:
            raise OwnerOnlyActionError()
        admins = await self.repo.get_company_admins(session, company_id)
        return admins or []

    async def admin_add(
        self,
        user_id: UUID,
        company_id: UUID,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_company_ids = await self.repo.get_owner_company_ids(
            session, current_user.id
        )
        if company_id not in owner_company_ids:
            raise OwnerOnlyActionError()

        user_role = await self.repo.get_user_role(session, company_id, user_id)
        if not user_role:
            raise MemberNotFoundError(user_id)
        if user_role.role == RoleEnum.ADMIN:
            raise UserAlreadyAdminException()
        if user_role.role == RoleEnum.OWNER:
            raise UserAlreadyOwnerException()
        user_role.role = RoleEnum.ADMIN

        await self.repo.update(session, user_role)
        return {"message": f"User with id {user_id} successfully became an admin"}

    async def admin_role_remove(
        self,
        user_id: UUID,
        company_id: UUID,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_company_ids = await self.repo.get_owner_company_ids(
            session, current_user.id
        )
        if company_id not in owner_company_ids:
            raise OwnerOnlyActionError()

        user_role = await self.repo.get_user_role(session, company_id, user_id)
        if not user_role:
            raise MemberNotFoundError(user_id)
        if user_role.role != RoleEnum.ADMIN:
            raise InvalidInviteStatusError("User is not admin")
        user_role.role = RoleEnum.MEMBER

        await self.repo.update(session, user_role)
        return {"message": f"User with id {user_id} is not admin anymore"}

    # =================================QUIZZES MANAGMENT===========================================

    async def company_create_quiz(
        self,
        company_id: UUID,
        quiz_data: QuizCreate,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_admin_company_ids = await self.repo.get_owner_or_admin_company_ids(
            session, current_user.id
        )
        if company_id not in owner_admin_company_ids:
            raise OwnerAndAdminOnlyActionError()

        if len(quiz_data.questions) < 2:
            raise FewQuestionsException()

        for q in quiz_data.questions:
            if len(q.options) < 2:
                raise FewOptionsException()

        quiz = await self.repo.create_quiz(
            session, quiz_data.title, quiz_data.description, company_id
        )

        questions_list = [
            QuestionCreateSchema(
                quiz_id=quiz.id,
                title=q.title,
                options=q.options,
                correct_answers=q.correct_answers,
            ).model_dump()
            for q in quiz_data.questions
        ]

        await self.repo.create_questions(session, questions_list)

        await self.repo.update(session, quiz)

        return quiz

    async def company_delete_quiz(
        self,
        company_id: UUID,
        quiz_id: UUID,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_admin_company_ids = await self.repo.get_owner_or_admin_company_ids(
            session, current_user.id
        )
        if company_id not in owner_admin_company_ids:
            raise OwnerAndAdminOnlyActionError()

        quiz = await session.get(QuizModel, quiz_id)
        if not quiz or quiz.company_id != company_id:
            raise QuizNotFoundException()

        await self.repo.delete(session, quiz)

        return {"message": "Quiz deleted successfully"}

    async def company_delete_question(
        self,
        company_id: UUID,
        quiz_id: UUID,
        question_id: UUID,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_admin_company_ids = await self.repo.get_owner_or_admin_company_ids(
            session, current_user.id
        )
        if company_id not in owner_admin_company_ids:
            raise OwnerAndAdminOnlyActionError()

        quiz = await self.repo.get_quiz_by_id_and_company(session, quiz_id, company_id)
        if not quiz or quiz.company_id != company_id:
            raise QuizNotFoundException()

        question = await self.repo.get_question_by_id(session, question_id, quiz_id)
        if not question or question.quiz_id != quiz_id:
            raise QuestionNotFoundException()

        await self.repo.delete(session, question)
        return {"message": "Question deleted successfully"}

    async def company_edit_quiz(
        self,
        company_id: UUID,
        quiz_id: UUID,
        quiz_data: QuizUpdate,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_admin_company_ids = await self.repo.get_owner_or_admin_company_ids(
            session, current_user.id
        )
        if company_id not in owner_admin_company_ids:
            raise OwnerAndAdminOnlyActionError()

        quiz = await self.repo.get_quiz_by_id(session, quiz_id, company_id)
        if not quiz or quiz.company_id != company_id:
            raise QuizNotFoundException()

        update_data = quiz_data.model_dump(exclude_unset=True)
        if not update_data:
            return quiz

        for field, value in update_data.items():
            setattr(quiz, field, value)

        await self.repo.update(session, quiz)

        return quiz

    async def quiz_edit_question(
        self,
        company_id: UUID,
        quiz_id: UUID,
        question_id: UUID,
        question_data: QuestionUpdate,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        owner_admin_company_ids = await self.repo.get_owner_or_admin_company_ids(
            session, current_user.id
        )
        if company_id not in owner_admin_company_ids:
            raise OwnerAndAdminOnlyActionError()

        quiz = await self.repo.get_quiz_by_id(session, quiz_id, company_id)
        if not quiz or quiz.company_id != company_id:
            raise QuizNotFoundException()

        question = await self.repo.get_question_by_id(session, question_id, quiz_id)
        if not question or question.quiz_id != quiz_id:
            raise QuestionNotFoundException()

        update_data = question_data.model_dump(exclude_unset=True)
        if not update_data:
            return question

        if "options" in update_data:
            options = update_data["options"]
            if not options or len(options) < 2:
                raise NotEnoughOptionsException()

        for field, value in update_data.items():
            setattr(question, field, value)

        await self.repo.update(session, question)

        return {"message": "Sucessfully updated question"}

    async def company_all_quizzes(
        self, company_id: UUID, session: AsyncSession, limit: int = 10, offset: int = 0
    ):
        company = await self.repo.get_company_by_id(session, company_id)
        if not company:
            raise CompanyNotFoundError(company_id)

        quizzes = await self.repo.get_all_quizzes(company_id, session, limit, offset)

        return [
            QuizzesList.model_validate(quiz).model_dump(mode="json") for quiz in quizzes
        ]


companies_service = CompaniesService(CompaniesRepository())
