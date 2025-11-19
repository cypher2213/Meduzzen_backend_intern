from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_invites_model import (
    CompanyInvitesModel,
    InviteStatus,
    InviteType,
)
from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
from app.models.user_model import UserModel
from app.repository.companies_repository import CompaniesRepository
from app.schemas.company_schema import (
    CompanyCreate,
    CompanySchema,
    CompanyUpdate,
    InviteSentSchema,
    RequestSentSchema,
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
        seek_user = await session.execute(
            select(UserModel).where(UserModel.id == invite_data.invited_user_id)
        )
        invited_user = seek_user.scalar_one_or_none()
        if not invited_user:
            raise HTTPException(
                status_code=404,
                detail=f"User with id {invite_data.invited_user_id} is not found.",
            )
        seek_company = await session.execute(
            select(CompanyModel).where(CompanyModel.id == invite_data.company_id)
        )
        company = seek_company.scalar_one_or_none()
        if not company:
            raise HTTPException(
                status_code=404,
                detail=f"Company with company_id {invite_data.company_id} is not found.",
            )
        invite_sending = CompanyInvitesModel(
            company_id=invite_data.company_id,
            invited_user_id=invite_data.invited_user_id,
            invited_by_id=user.id,
            type=InviteType.INVITE,
            status=InviteStatus.PENDING,
        )
        session.add(invite_sending)
        await session.commit()
        await session.refresh(invite_sending)

        return {"message": f"Successfully sent invitation to {invited_user.name} "}

    async def invite_cancel(
        self, invite_id: UUID, user: UserModel, session: AsyncSession
    ):
        invite_seek = await session.execute(
            select(CompanyInvitesModel).where(CompanyInvitesModel.id == invite_id)
        )
        invitation = invite_seek.scalar_one_or_none()
        if not invitation:
            raise HTTPException(
                status_code=404, detail=f"Invitation with id {invite_id} is not found."
            )
        if invitation.invited_by_id != user.id:
            raise HTTPException(
                status_code=403, detail="You are not allowed to delete this invitation."
            )
        await session.delete(invitation)
        await session.commit()
        return {"message": "Invitation deleted successfully!"}

    async def request_owner_switcher(
        self,
        request_id: UUID,
        option: str,
        current_user: UserModel,
        session: AsyncSession,
    ):
        request_seek = await session.execute(
            select(CompanyInvitesModel).where(CompanyInvitesModel.id == request_id)
        )
        request = request_seek.scalar_one_or_none()
        if not request:
            raise HTTPException(
                status_code=404, detail=f"Request with id {request_id} does not exist!"
            )
        if request.status != InviteStatus.PENDING:
            raise HTTPException(
                status_code=400, detail="This request is already accepted or declined."
            )
        if option not in ("accept", "decline"):
            raise HTTPException(
                status_code=400, detail="Option must be 'accept' or 'decline'"
            )
        elif option == "accept":
            request.status = InviteStatus.ACCEPTED
            user_addition_to_company = CompanyUserRoleModel(
                user_id=request.invited_user_id,
                company_id=request.company_id,
                role=RoleEnum.MEMBER,
            )
            session.add(user_addition_to_company)
            await session.commit()
        elif option == "decline":
            request.status = InviteStatus.DECLINED
            await session.commit()

        return {"message": f"You have successfully {option}ed request"}

    async def remove_owner_user(
        self,
        user_id: UUID,
        company_data: RequestSentSchema,
        current_user: UserModel,
        session: AsyncSession,
    ):
        current_role_seek = await session.execute(
            select(CompanyUserRoleModel).where(
                CompanyUserRoleModel.company_id == company_data.company_id,
                CompanyUserRoleModel.user_id == current_user.id,
            )
        )
        current_role = current_role_seek.scalar_one_or_none()

        if not current_role or current_role.role != RoleEnum.OWNER:
            raise HTTPException(
                status_code=403, detail="Only company owner can remove users"
            )

        user_seek = await session.execute(
            select(CompanyUserRoleModel).where(CompanyUserRoleModel.user_id == user_id)
        )
        user = user_seek.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        if user.role != RoleEnum.MEMBER:
            raise HTTPException(
                status_code=400, detail="You can delete only member users"
            )
        await session.delete(user)
        await session.commit()
        return {"message": "User deleted successfully!"}


companies_service = CompaniesService(CompaniesRepository())
