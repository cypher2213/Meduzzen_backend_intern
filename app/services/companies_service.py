from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_invites_model import InviteStatus
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
from app.models.user_model import UserModel
from app.repository.companies_repository import CompaniesRepository
from app.schemas.company_schema import (
    CompanyCreate,
    CompanySchema,
    CompanyUpdate,
    InviteSentSchema,
    RequestSentSchema,
    UsersWithRolesResponse,
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
            raise HTTPException(
                status_code=404,
                detail="Company not found",
            )
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
            raise HTTPException(
                status_code=403,
                detail="You are not the owner of this company or it does not exist.",
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
            raise HTTPException(
                status_code=403,
                detail="You are not the owner of this company or it does not exist.",
            )
        await self.repo.delete(db, company)

    # ========================INVITES====================

    async def invite_send(
        self, invite_data: InviteSentSchema, user: UserModel, session: AsyncSession
    ):
        invited_user = await self.repo.get_by_id(session, invite_data.invited_user_id)

        if not invited_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {invite_data.invited_user_id} not found.",
            )

        company = await self.repo.get_company_by_id(session, invite_data.company_id)

        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company with id {invite_data.company_id} not found.",
            )
        membership = await self.repo.get_membership(
            session, invite_data.company_id, user.id
        )
        if not membership or membership.role != RoleEnum.OWNER:
            raise HTTPException(
                status_code=403, detail="Only company owners can send invitations."
            )

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
            raise HTTPException(
                status_code=404, detail=f"Invitation with id {invite_id} not found."
            )
        if invite.invited_by_id != user.id:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to cancel this invitation.",
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
            raise HTTPException(404, f"Request with id {request_id} does not exist!")
        if invite.status != InviteStatus.PENDING:
            raise HTTPException(400, "This request is already accepted or declined.")

        membership = await self.repo.get_membership(
            session, invite.company_id, current_user.id
        )

        if not membership or membership.role != RoleEnum.OWNER:
            raise HTTPException(
                403, "Only company owners can accept or decline requests"
            )
        if option not in (InviteStatus.ACCEPTED, InviteStatus.DECLINED):
            raise HTTPException(
                400,
                f"Option must be {InviteStatus.ACCEPTED} or {InviteStatus.ACCEPTED}",
            )
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

        return {"message": f"You have successfully {option}ed request"}

    async def remove_user_by_owner(
        self,
        user_id: UUID,
        company_data: RequestSentSchema,
        current_user: UserModel,
        session: AsyncSession,
    ):
        current_role = await self.repo.get_user_role(
            session, company_data.company_id, current_user.id
        )
        if not current_role or current_role.role != RoleEnum.OWNER:
            raise HTTPException(
                status_code=403, detail="Only company owner can remove users"
            )

        user_role = await self.repo.get_user_role(
            session, company_data.company_id, user_id
        )
        if not user_role:
            raise HTTPException(status_code=404, detail="User not found")

        if user_role.role != RoleEnum.MEMBER:
            raise HTTPException(
                status_code=400, detail="You can delete only member users"
            )

        await self.repo.delete_user_role(session, user_role)

        return {"message": "User deleted successfully!"}

    # ========================MANAGING INVITES=========
    async def invite_owner_list(self, current_user: UserModel, session: AsyncSession):
        owner_company_ids = await self.repo.get_owner_company_ids(
            session, current_user.id
        )
        if not owner_company_ids:
            raise HTTPException(403, "You are not an owner of any company")

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
            raise HTTPException(403, "You are not an owner of any company")

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
        company_data: RequestSentSchema,
        limit: int,
        offset: int,
        current_user: UserModel,
        session: AsyncSession,
    ):
        membership = await self.repo.get_membership(
            session, company_data.company_id, current_user.id
        )
        if not membership:
            raise HTTPException(403, "You do not have access to this company")

        total = await self.repo.count_users(session, company_data.company_id)

        rows = await self.repo.get_users_with_roles(
            session, company_data.company_id, limit, offset
        )

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
            "company_id": str(company_data.company_id),
            "total_users": total,
            "limit": limit,
            "offset": offset,
            "users": users,
        }


companies_service = CompaniesService(CompaniesRepository())
