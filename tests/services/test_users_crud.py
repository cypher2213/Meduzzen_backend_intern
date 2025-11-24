from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.core.base_exception import (
    CompanyNotFoundError,
    InvalidCredentialsError,
    InviteInvalidOptionError,
    InviteNotFoundError,
    InvitePermissionDeniedError,
    NotCompanyMemberError,
    OwnerCannotLeaveError,
    RequestPermissionDeniedError,
    RequestWrongTypeError,
)
from app.models.company_invite_request_model import InviteStatus, InviteType
from app.models.company_user_role_model import RoleEnum
from app.schemas.user_schema import SignInSchema, SignUpSchema, UserUpdateSchema


@pytest.mark.asyncio
async def test_create_user(user_service, mock_repo, mock_session, fake_user):
    mock_repo.create.return_value = fake_user

    user_data = SignUpSchema(
        name="John", email="john@example.com", password="123456", age=25
    )

    result = await user_service.create_user(mock_session, user_data)

    mock_repo.create.assert_awaited_once()
    assert result == fake_user


@pytest.mark.asyncio
async def test_delete_user_success(user_service, mock_repo, mock_session, fake_user):
    mock_repo.get.return_value = fake_user
    mock_repo.delete.return_value = None
    current_user = SimpleNamespace(id=fake_user.id)

    await user_service.delete_user(mock_session, current_user)

    mock_repo.delete.assert_awaited_once_with(mock_session, fake_user)


@pytest.mark.asyncio
async def test_update_user_success(user_service, mock_repo, mock_session, fake_user):
    updated_user = SimpleNamespace(
        id=fake_user.id, name="New Name", email="new@example.com"
    )
    mock_repo.get_by_id.return_value = fake_user
    mock_repo.update.return_value = updated_user
    current_user = SimpleNamespace(id=fake_user.id)

    result = await user_service.update_user(
        UserUpdateSchema(name="New Name"), mock_session, current_user
    )

    mock_repo.update.assert_awaited_once()
    assert result["message"] == "User updated successfully"


@pytest.mark.asyncio
async def test_login_user_success(user_service, mock_repo, mock_session, fake_user):
    mock_repo.get_by_email.return_value = fake_user
    user_data = SignInSchema(email=fake_user.email, password="123456")

    with patch("app.services.users_service.verify_password", return_value=True), patch(
        "app.services.users_service.create_access_token", return_value="mock_token"
    ), patch(
        "app.services.users_service.create_refresh_token", return_value="mock_refresh"
    ):
        result = await user_service.login_user(user_data.model_dump(), mock_session)

    mock_repo.get_by_email.assert_awaited_once_with(mock_session, fake_user.email)
    assert result == {
        "message": "Logged in successfully!",
        "access_token": "mock_token",
        "refresh_token": "mock_refresh",
        "token_type": "bearer",
    }


@pytest.mark.asyncio
async def test_login_user_invalid_email(user_service, mock_repo, mock_session):
    mock_repo.get_by_email.return_value = None
    user_data = SignInSchema(email="notfound@example.com", password="123456")

    with pytest.raises(InvalidCredentialsError) as exc:
        await user_service.login_user(user_data.model_dump(), mock_session)

    assert exc.value.status_code == 401
    assert exc.value.message == "Invalid credentials"
    mock_repo.get_by_email.assert_awaited_once_with(mock_session, user_data.email)


@pytest.mark.asyncio
async def test_login_user_invalid_password(
    user_service, mock_repo, mock_session, fake_user
):
    mock_repo.get_by_email.return_value = fake_user
    user_data = SignInSchema(email=fake_user.email, password="wrongpass")

    with patch("app.utils.jwt_util.pwd_context.verify", return_value=False):
        with pytest.raises(InvalidCredentialsError) as exc:
            await user_service.login_user(user_data.model_dump(), mock_session)

    assert exc.value.status_code == 401
    assert exc.value.message == "Invalid credentials"


@pytest.mark.asyncio
async def test_invite_user_switcher_decline(
    user_service, mock_repo, mock_session, fake_user
):
    invite_id = uuid4()

    invite = MagicMock(
        id=invite_id, invited_user_id=fake_user.id, status=InviteStatus.PENDING
    )

    mock_repo.get_invite.return_value = invite

    result = await user_service.invite_user_switcher(
        invite_id=invite_id,
        option="declined",
        current_user=fake_user,
        session=mock_session,
    )

    mock_session.commit.assert_called_once()

    assert "decline" in result["message"]


@pytest.mark.asyncio
async def test_invite_user_switcher_not_found(
    user_service, mock_repo, mock_session, fake_user
):
    invite_id = uuid4()
    mock_repo.get_invite.return_value = None

    with pytest.raises(InviteNotFoundError) as exc:
        await user_service.invite_user_switcher(
            invite_id=invite_id,
            option="accept",
            current_user=fake_user,
            session=mock_session,
        )

    assert exc.value.status_code == 404
    assert str(exc.value) == f"Invite with id {invite_id} does not exist!"


@pytest.mark.asyncio
async def test_invite_user_switcher_forbidden(
    user_service, mock_repo, mock_session, fake_user
):
    invite = MagicMock(
        invited_user_id=uuid4(),
        status=InviteStatus.PENDING,
    )

    mock_repo.get_invite.return_value = invite

    with pytest.raises(InvitePermissionDeniedError) as exc:
        await user_service.invite_user_switcher(
            invite_id=uuid4(),
            option="accept",
            current_user=fake_user,
            session=mock_session,
        )

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_invite_user_switcher_invalid_option(
    user_service, mock_repo, mock_session, fake_user
):
    invite = MagicMock(
        invited_user_id=fake_user.id,
        status=InviteStatus.PENDING,
    )

    mock_repo.get_invite.return_value = invite

    with pytest.raises(InviteInvalidOptionError) as exc:
        await user_service.invite_user_switcher(
            invite_id=uuid4(),
            option="bad",
            current_user=fake_user,
            session=mock_session,
        )

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_request_send_company_not_found(
    user_service, mock_repo, mock_session, fake_user
):
    mock_repo.get_company.return_value = None

    with pytest.raises(CompanyNotFoundError) as exc:
        await user_service.request_send(
            request_data=MagicMock(company_id=uuid4()),
            current_user=fake_user,
            session=mock_session,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_request_cancel_success(user_service, mock_repo, mock_session, fake_user):
    request = MagicMock(
        type=InviteType.REQUEST,
        status=InviteStatus.PENDING,
        invited_user_id=fake_user.id,
    )

    mock_repo.get_invite.return_value = request

    result = await user_service.request_cancel(
        request_id=uuid4(),
        current_user=fake_user,
        session=mock_session,
    )

    assert "successfully canceled" in result["message"].lower()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_request_cancel_wrong_type(
    user_service, mock_repo, mock_session, fake_user
):
    request = MagicMock(type=InviteType.INVITE)
    mock_repo.get_invite.return_value = request

    with pytest.raises(RequestWrongTypeError) as exc:
        await user_service.request_cancel(uuid4(), fake_user, mock_session)

    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_request_cancel_forbidden(
    user_service, mock_repo, mock_session, fake_user
):
    request = MagicMock(
        type=InviteType.REQUEST, status=InviteStatus.PENDING, invited_user_id=uuid4()
    )
    mock_repo.get_invite.return_value = request

    with pytest.raises(RequestPermissionDeniedError) as exc:
        await user_service.request_cancel(uuid4(), fake_user, mock_session)

    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_leave_user_success(user_service, mock_repo, mock_session, fake_user):
    role = MagicMock(role=RoleEnum.MEMBER)
    mock_repo.get_user_role.return_value = role

    result = await user_service.leave_user(
        MagicMock(company_id=uuid4()), fake_user, mock_session
    )

    mock_repo.delete_user_role.assert_called_once()
    assert "successfully left" in result["message"].lower()


@pytest.mark.asyncio
async def test_leave_user_not_member(user_service, mock_repo, mock_session, fake_user):
    mock_repo.get_user_role.return_value = None

    with pytest.raises(NotCompanyMemberError) as exc:
        await user_service.leave_user(
            MagicMock(company_id=uuid4()),
            fake_user,
            mock_session,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_leave_user_last_owner_forbidden(
    user_service, mock_repo, mock_session, fake_user
):
    mock_repo.get_user_role.return_value = MagicMock(role=RoleEnum.OWNER)

    mock_repo.get_users_with_roles.return_value = [("user", RoleEnum.OWNER)]

    with pytest.raises(OwnerCannotLeaveError) as exc:
        await user_service.leave_user(
            MagicMock(company_id=uuid4()),
            fake_user,
            mock_session,
        )

    assert exc.value.status_code == 400
