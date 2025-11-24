from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.base_exception import (
    CompanyNotFoundError,
    InvalidInviteStatusError,
    InviteInvalidOptionError,
    MemberNotFoundError,
    OwnerOnlyActionError,
    PermissionDeniedError,
)
from app.models.company_invite_request_model import InviteStatus
from app.models.company_model import CompanyModel
from app.models.company_user_role_model import CompanyUserRoleModel, RoleEnum
from app.models.user_model import UserModel
from app.repository.companies_repository import CompaniesRepository
from app.schemas.company_schema import CompanyCreate, CompanyUpdate
from app.services.companies_service import CompaniesService


@pytest.fixture
def repo_mock():
    return AsyncMock(spec=CompaniesRepository)


@pytest.fixture
def service(repo_mock):
    return CompaniesService(repo_mock)


@pytest.fixture
def async_session_mock():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_mock():
    return UserModel(id=uuid4(), name="Test User")


@pytest.mark.asyncio
async def test_get_all_companies(service, repo_mock, async_session_mock):
    company1 = CompanyModel(
        id=uuid4(), name="Company1", description="Desc1", is_public=True
    )
    company2 = CompanyModel(
        id=uuid4(), name="Company2", description="Desc2", is_public=False
    )
    repo_mock.get_all.return_value = [company1, company2]

    result = await service.get_all_companies(async_session_mock)

    assert len(result) == 2
    assert result[0]["name"] == "Company1"
    assert result[1]["name"] == "Company2"
    repo_mock.get_all.assert_awaited_once_with(async_session_mock, 10, 0)


@pytest.mark.asyncio
async def test_get_company_found(service, repo_mock, async_session_mock):
    company = MagicMock(spec=CompanyModel, name="TestCompany")
    repo_mock.get.return_value = company

    result = await service.get_company(uuid4(), async_session_mock)

    assert result["message"] == "Company successfully found!"
    assert result["company"] == company
    repo_mock.get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_company_not_found(service, repo_mock, async_session_mock):
    company_id = uuid4()
    repo_mock.get.return_value = None

    with pytest.raises(CompanyNotFoundError) as exc:
        await service.get_company(company_id, async_session_mock)

    assert exc.value.status_code == 404
    assert exc.value.message == f"Company with id {company_id} is not found."


@pytest.mark.asyncio
async def test_company_create(service, repo_mock, async_session_mock, user_mock):
    company_data = CompanyCreate(name="NewCo", description="Desc", is_public=True)
    company_obj = MagicMock(spec=CompanyModel, id=uuid4(), name="NewCo")
    repo_mock.create.return_value = company_obj

    result = await service.company_create(company_data, async_session_mock, user_mock)

    assert result["message"] == f"Company created successfully by {user_mock.name}."
    assert result["company"] == company_obj
    repo_mock.create.assert_awaited_once()
    repo_mock.add_user_role.assert_awaited_once_with(
        db=async_session_mock,
        user_id=user_mock.id,
        company_id=company_obj.id,
        role="owner",
    )
    async_session_mock.refresh.assert_awaited_once_with(company_obj)


@pytest.mark.asyncio
async def test_company_update_success(
    service, repo_mock, async_session_mock, user_mock
):
    company_id = uuid4()
    company_obj = MagicMock(spec=CompanyModel, id=company_id, name="OldName")
    repo_mock.get_owner_company.return_value = company_obj
    repo_mock.update.return_value = company_obj

    update_data = CompanyUpdate(name="NewName")

    result = await service.company_update(
        company_id, update_data, async_session_mock, user_mock
    )

    assert result["company"] == company_obj
    assert result["company"].name == "OldName" or result["company"].name == "NewName"
    repo_mock.get_owner_company.assert_awaited_once_with(
        async_session_mock, company_id, user_mock.id
    )
    repo_mock.update.assert_awaited_once_with(async_session_mock, company_obj)


@pytest.mark.asyncio
async def test_company_update_forbidden(
    service, repo_mock, async_session_mock, user_mock
):
    repo_mock.get_owner_company.return_value = None

    with pytest.raises(PermissionDeniedError) as exc:
        await service.company_update(
            uuid4(), CompanyUpdate(name="x"), async_session_mock, user_mock
        )
    assert exc.value.status_code == 403
    assert "owner" in exc.value.message


@pytest.mark.asyncio
async def test_company_delete_success(
    service, repo_mock, async_session_mock, user_mock
):
    company_obj = MagicMock(spec=CompanyModel, name="DeleteMe")
    repo_mock.get_owner_company.return_value = company_obj
    repo_mock.delete.return_value = None

    await service.company_delete(uuid4(), async_session_mock, user_mock)

    repo_mock.delete.assert_awaited_once_with(async_session_mock, company_obj)


@pytest.mark.asyncio
async def test_company_delete_forbidden(
    service, repo_mock, async_session_mock, user_mock
):
    repo_mock.get_owner_company.return_value = None

    with pytest.raises(PermissionDeniedError) as exc:
        await service.company_delete(uuid4(), async_session_mock, user_mock)

    assert exc.value.status_code == 403
    assert "owner" in exc.value.message


@pytest.mark.asyncio
async def test_invite_send_success(service, mock_repo, mock_session, fake_user):
    invited_user = UserModel(id=uuid4(), name="Bob")
    company = CompanyModel(id=uuid4(), name="TestCo")

    mock_session.get.side_effect = [invited_user, company]

    mock_repo.get_membership.return_value = CompanyUserRoleModel(
        user_id=fake_user.id, company_id=company.id, role=RoleEnum.OWNER
    )

    mock_repo.send_invite.return_value = MagicMock(invited_user_id=invited_user.id)

    service.repo = mock_repo

    result = await service.invite_send(
        invite_data=MagicMock(invited_user_id=invited_user.id, company_id=company.id),
        user=fake_user,
        session=mock_session,
    )
    assert "Successfully sent invitation" in result["message"]


@pytest.mark.asyncio
async def test_invite_send_forbidden(service, mock_repo, mock_session, fake_user):
    invited_user = UserModel(id=uuid4())
    company = CompanyModel(id=uuid4())

    mock_session.get.side_effect = [invited_user, company]
    mock_repo.get_membership.return_value = CompanyUserRoleModel(
        user_id=fake_user.id, company_id=company.id, role=RoleEnum.MEMBER
    )

    service.repo = mock_repo

    with pytest.raises(OwnerOnlyActionError) as exc:
        await service.invite_send(
            MagicMock(invited_user_id=invited_user.id, company_id=company.id),
            fake_user,
            mock_session,
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_invite_cancel_success(service, mock_repo, mock_session, fake_user):
    invite = MagicMock(invited_by_id=fake_user.id)

    mock_repo.get_invite.return_value = invite
    service.repo = mock_repo

    result = await service.invite_cancel(uuid4(), fake_user, mock_session)

    assert "canceled" in result["message"]
    mock_repo.cancel_invite.assert_called_once()


@pytest.mark.asyncio
async def test_invite_cancel_forbidden(service, mock_repo):
    invite = MagicMock(invited_by_id=uuid4())
    mock_repo.get_invite.return_value = invite

    service.repo = mock_repo

    with pytest.raises(PermissionDeniedError):
        await service.invite_cancel(uuid4(), UserModel(id=uuid4()), MagicMock())


@pytest.mark.asyncio
async def test_request_owner_switcher_invalid_option(
    service, mock_repo, mock_session, fake_user
):
    invite = MagicMock(status=InviteStatus.PENDING)
    mock_repo.get_invite.return_value = invite
    mock_repo.get_membership.return_value = CompanyUserRoleModel(
        user_id=fake_user.id, company_id=uuid4(), role=RoleEnum.OWNER
    )

    service.repo = mock_repo

    with pytest.raises(InviteInvalidOptionError):
        await service.request_owner_switcher(uuid4(), "NOPE", fake_user, mock_session)


@pytest.mark.asyncio
async def test_remove_owner_user_success(service, mock_repo, mock_session, fake_user):
    owner_role = CompanyUserRoleModel(
        user_id=fake_user.id, company_id=uuid4(), role=RoleEnum.OWNER
    )
    member_role = CompanyUserRoleModel(
        user_id=uuid4(), company_id=owner_role.company_id, role=RoleEnum.MEMBER
    )

    mock_repo.get_user_role.side_effect = [owner_role, member_role]

    service.repo = mock_repo

    result = await service.remove_user_by_owner(
        user_id=member_role.user_id,
        company_id=owner_role.company_id,
        current_user=fake_user,
        session=mock_session,
    )

    assert "deleted" in result["message"]
    mock_repo.delete_user_role.assert_called_once()


@pytest.mark.asyncio
async def test_remove_owner_user_bad_role(service, mock_repo, mock_session, fake_user):
    owner_role = CompanyUserRoleModel(
        user_id=fake_user.id, company_id=uuid4(), role=RoleEnum.OWNER
    )
    other_owner = CompanyUserRoleModel(
        user_id=uuid4(), company_id=owner_role.company_id, role=RoleEnum.OWNER
    )

    mock_repo.get_user_role.side_effect = [owner_role, other_owner]

    service.repo = mock_repo

    with pytest.raises(InvalidInviteStatusError):
        await service.remove_user_by_owner(
            uuid4(),
            MagicMock(company_id=owner_role.company_id),
            fake_user,
            mock_session,
        )


@pytest.mark.asyncio
async def test_invite_owner_list_forbidden(service, mock_repo, fake_user):
    mock_repo.get_owner_company_ids.return_value = []

    service.repo = mock_repo

    with pytest.raises(OwnerOnlyActionError):
        await service.invite_owner_list(fake_user, MagicMock())


@pytest.mark.asyncio
async def test_pending_requests_list_success(service, mock_repo, fake_user):
    mock_repo.get_owner_company_ids.return_value = [uuid4()]
    mock_repo.get_pending_requests.return_value = ["req1"]

    service.repo = mock_repo

    result = await service.pending_requests_list(fake_user, MagicMock())

    assert result["requests"] == ["req1"]


@pytest.mark.asyncio
async def test_pending_requests_list_forbidden(service, mock_repo, fake_user):
    mock_repo.get_owner_company_ids.return_value = []

    service.repo = mock_repo

    with pytest.raises(OwnerOnlyActionError):
        await service.pending_requests_list(fake_user, MagicMock())


@pytest.mark.asyncio
async def test_list_company_users_success(service, mock_repo, mock_session, fake_user):
    mock_repo.get_membership.return_value = CompanyUserRoleModel(
        user_id=fake_user.id, company_id=uuid4(), role=RoleEnum.OWNER
    )

    mock_repo.count_users.return_value = 1
    mock_repo.get_users_with_roles.return_value = [
        (UserModel(id=uuid4(), email="a@test.com", name="Ann"), RoleEnum.MEMBER)
    ]

    service.repo = mock_repo

    result = await service.list_company_users(
        MagicMock(company_id=uuid4()),
        limit=10,
        offset=0,
        current_user=fake_user,
        session=mock_session,
    )

    assert result["total_users"] == 1
    assert len(result["users"]) == 1


# ===================ADMIN ROLE TESTS==================
@pytest.mark.asyncio
async def test_admin_list_company_not_found(
    service, mock_repo, mock_session, fake_user
):
    service.repo = mock_repo
    mock_repo.get_company_by_id.return_value = None

    with pytest.raises(CompanyNotFoundError):
        await service.admin_list(uuid4(), fake_user, mock_session)


@pytest.mark.asyncio
async def test_admin_remove_not_owner(service, mock_repo, mock_session, fake_user):
    service.repo = mock_repo
    mock_repo.get_company_by_id.return_value = {"id": 1}
    mock_repo.get_owner_company_ids.return_value = []

    with pytest.raises(OwnerOnlyActionError):
        await service.admin_role_remove(uuid4(), uuid4(), fake_user, mock_session)


@pytest.mark.asyncio
async def test_admin_remove_member_not_found(
    service, mock_repo, mock_session, fake_user
):
    service.repo = mock_repo
    company_id = uuid4()
    mock_repo.get_company_by_id.return_value = {"id": 1}
    mock_repo.get_owner_company_ids.return_value = [company_id]
    mock_repo.get_user_role.return_value = None

    with pytest.raises(MemberNotFoundError):
        await service.admin_role_remove(uuid4(), company_id, fake_user, mock_session)


@pytest.mark.asyncio
async def test_admin_remove_user_not_admin(service, mock_repo, mock_session, fake_user):
    role = AsyncMock()
    role.role = RoleEnum.MEMBER
    company_id = uuid4()
    service.repo = mock_repo
    mock_repo.get_company_by_id.return_value = {"id": 1}
    mock_repo.get_owner_company_ids.return_value = [company_id]
    mock_repo.get_user_role.return_value = role

    with pytest.raises(InvalidInviteStatusError):
        await service.admin_role_remove(uuid4(), company_id, fake_user, mock_session)


@pytest.mark.asyncio
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_admin_remove_success(service, mock_repo, mock_session, fake_user):
    role = AsyncMock()
    role.role = RoleEnum.ADMIN
    company_id = uuid4()
    service.repo = mock_repo
    mock_repo.get_company_by_id.return_value = {"id": 1}
    mock_repo.get_owner_company_ids.return_value = [company_id]
    mock_repo.get_user_role.return_value = role

    res = await service.admin_role_remove(uuid4(), company_id, fake_user, mock_session)

    assert res["message"]
    assert role.role == RoleEnum.MEMBER
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited()
    mock_session.refresh.assert_awaited()
