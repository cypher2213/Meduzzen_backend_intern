from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_exception import (
    CompanyNotFoundError,
    EmailChangeForbiddenError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
    InviteAlreadyProcessedError,
    InviteInvalidOptionError,
    InviteNotFoundError,
    InvitePermissionDeniedError,
    NotCompanyMemberError,
    OwnerCannotLeaveError,
    RequestAlreadyCanceledError,
    RequestNotFoundError,
    RequestPermissionDeniedError,
    RequestWrongTypeError,
    UserNotFoundError,
)
from app.core.logger import logger
from app.models.company_invite_request_model import InviteStatus, InviteType
from app.models.company_user_role_model import RoleEnum
from app.models.user_model import UserModel
from app.repository.users_repository import UserRepository
from app.schemas.company_schema import RequestSentSchema
from app.schemas.user_schema import SignUpSchema, UserSchema, UserUpdateSchema
from app.utils.jwt_util import (
    create_access_token,
    create_refresh_token,
    decode_token,
    password_hash,
    verify_password,
)


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def get_all_users(
        self, session: AsyncSession, limit: int = 10, offset: int = 0
    ):
        users = await self.repo.get_all(session, limit, offset)
        if users:
            user_list = [
                UserSchema.model_validate(user).model_dump(mode="json")
                for user in users
            ]
        return user_list or []

    async def create_user(self, session: AsyncSession, user_data: SignUpSchema):
        data = user_data.model_dump()
        if "password" in data:
            data["password"] = password_hash(data["password"])
        user = await self.repo.create(session, data)
        logger.info(f"User created: id={user.id}, name={user.name}")
        return user

    async def delete_user(self, session: AsyncSession, current_user: UserModel):
        user = await self.repo.get(session, current_user.id)
        if not user:
            logger.warning(f"Attempted delete — user not found: id={current_user.id}")
            raise UserNotFoundError(current_user.id)
        await self.repo.delete(session, user)
        logger.info(f"User deleted: id={current_user.id}, name={user.name}")

    async def get_user_by_id(self, session: AsyncSession, user_id: UUID):
        user = await self.repo.get(session, user_id)
        if not user:
            raise UserNotFoundError(user_id)
        return {"message": "User Found", "user": user}

    async def update_user(
        self,
        updated_user: UserUpdateSchema,
        session: AsyncSession,
        current_user: UserModel,
    ):
        user = await self.repo.get(session, current_user.id)
        if not user:
            raise UserNotFoundError(current_user.id)
        filtered_data = updated_user.model_dump(exclude_none=True)
        if "email" in filtered_data:
            raise EmailChangeForbiddenError()
        if "password" in filtered_data:
            filtered_data["password"] = password_hash(filtered_data["password"])

        for key, value in filtered_data.items():
            setattr(user, key, value)
        updated_user_obj = await self.repo.update(session, user)
        logger.info(f"User updated: id={user.id}")
        return {
            "message": "User updated successfully",
            "id": updated_user_obj.id,
            "name": updated_user_obj.name,
            "email": updated_user_obj.email,
        }

    async def login_user(self, user_data: dict, session: AsyncSession):
        email = user_data.get("email")
        password = user_data.get("password")
        user = await self.repo.get_by_email(session, email)
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password):
            raise InvalidCredentialsError()
        access_token = create_access_token({"sub": user.email})
        refresh_token = create_refresh_token({"sub": user.email})
        return {
            "message": "Logged in successfully!",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user_email = payload.get("sub")
            if not user_email:
                raise InvalidRefreshTokenError()

            new_access = create_access_token({"sub": user_email})
            return {"access_token": new_access, "token_type": "bearer"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    # =====================================INVITES==========================================

    async def invite_user_switcher(
        self,
        invite_id: UUID,
        option: str,
        current_user: UserModel,
        session: AsyncSession,
    ):
        invite = await self.repo.get_invite(session, invite_id)
        if not invite:
            raise InviteNotFoundError()
        if invite.status != InviteStatus.PENDING:
            raise InviteAlreadyProcessedError()
        if current_user.id != invite.invited_user_id:
            raise InvitePermissionDeniedError()

        if option not in (InviteStatus.ACCEPTED, InviteStatus.DECLINED):
            raise InviteInvalidOptionError()
        elif option == InviteStatus.ACCEPTED:
            invite.status = InviteStatus.ACCEPTED
            await self.repo.add_user_role(
                session,
                user_id=current_user.id,
                company_id=invite.company_id,
                role=RoleEnum.MEMBER,
            )
        elif option == InviteStatus.DECLINED:
            invite.status = InviteStatus.DECLINED
            await session.commit()

        return {"message": f"You have successfully {option} invitation"}

    # =======================REQUEST=======================
    async def request_send(
        self,
        request_data: RequestSentSchema,
        current_user: UserModel,
        session: AsyncSession,
    ):
        company = await self.repo.get_company(session, request_data.company_id)
        if not company:
            raise CompanyNotFoundError(request_data.company_id)
        await self.repo.send_request(
            session,
            company_id=request_data.company_id,
            invited_user_id=current_user.id,
        )

        return {"message": f"Successfully sent request to {company.name} "}

    async def request_cancel(
        self, request_id: UUID, current_user: UserModel, session: AsyncSession
    ):
        request = await self.repo.get_invite(session, request_id)
        if not request:
            raise RequestNotFoundError(request_id)
        if request.type != InviteType.REQUEST:
            raise RequestWrongTypeError()
        if request.status != InviteStatus.PENDING:
            raise RequestAlreadyCanceledError()
        if request.invited_user_id != current_user.id:
            raise RequestPermissionDeniedError()
        request.status = InviteStatus.CANCELED
        await session.commit()
        return {"message": "Your invitation was successfully canceled"}

    async def leave_user(
        self,
        company_id: UUID,
        current_user: UserModel,
        session: AsyncSession,
    ):
        user_role = await self.repo.get_user_role(session, company_id, current_user.id)
        if not user_role:
            raise NotCompanyMemberError()
        if user_role.role == RoleEnum.OWNER:
            owners = await self.repo.get_users_with_roles(
                session, company_id, limit=1000, offset=0
            )
            if len(owners) == 1:
                raise OwnerCannotLeaveError()
        await self.repo.delete_user_role(session, user_role)
        return {"message": "You have successfully left the company."}

    # ========================MANAGING REQUESTS=========

    async def show_user_requests(self, current_user: UserModel, session: AsyncSession):
        user_requests = await self.repo.get_user_requests(session, current_user.id)
        if not user_requests:
            return {"message": "No requests from you"}
        return {"message": "Successfully found requests", "requests": user_requests}

    async def show_user_invites(self, current_user: UserModel, session: AsyncSession):
        user_invites = await self.repo.get_user_invites(session, current_user.id)
        if not user_invites:
            return {"message": "No invites were sent to you"}
        return {"message": "Successfully found invites", "invites": user_invites}


user_service = UserService(UserRepository())
