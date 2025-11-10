from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException

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
    mock_repo.get_by_id.return_value = fake_user
    mock_repo.delete.return_value = None

    result = await user_service.delete_user(mock_session, fake_user.id)

    mock_repo.delete.assert_called_once_with(mock_session, fake_user)
    assert "successfully deleted" in result["message"]


@pytest.mark.asyncio
async def test_update_user_success(user_service, mock_repo, mock_session, fake_user):
    updated_user = SimpleNamespace(
        id=fake_user.id, name="New Name", email="new@example.com"
    )
    mock_repo.get_by_id.return_value = fake_user
    mock_repo.update.return_value = updated_user

    result = await user_service.update_user(
        fake_user.id,
        UserUpdateSchema(name="New Name"),
        mock_session,
    )

    mock_repo.update.assert_awaited_once()
    assert result["message"] == "User updated successfully"


@pytest.mark.asyncio
async def test_login_user_success(user_service, mock_repo, mock_session, fake_user):
    mock_repo.get_by_email.return_value = fake_user
    user_data = SignInSchema(email=fake_user.email, password="123456")

    with patch("app.services.users_service.verify_password", return_value=True), patch(
        "app.services.users_service.create_access_token", return_value="mock_token"
    ):
        result = await user_service.login_user(user_data.model_dump(), mock_session)

    mock_repo.get_by_email.assert_awaited_once_with(mock_session, fake_user.email)
    assert result == {
        "message": "Logged in successfully!",
        "access_token": "mock_token",
        "token_type": "bearer",
    }


@pytest.mark.asyncio
async def test_login_user_invalid_email(user_service, mock_repo, mock_session):
    mock_repo.get_by_email.return_value = None
    user_data = SignInSchema(email="notfound@example.com", password="123456")

    with pytest.raises(HTTPException) as exc:
        await user_service.login_user(user_data.model_dump(), mock_session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
    mock_repo.get_by_email.assert_awaited_once_with(mock_session, user_data.email)


@pytest.mark.asyncio
async def test_login_user_invalid_password(
    user_service, mock_repo, mock_session, fake_user
):
    mock_repo.get_by_email.return_value = fake_user
    user_data = SignInSchema(email=fake_user.email, password="wrongpass")

    with patch("app.utils.jwt_util.pwd_context.verify", return_value=False):
        with pytest.raises(HTTPException) as exc:
            await user_service.login_user(user_data.model_dump(), mock_session)

    assert exc.value.status_code == 401
    assert exc.value.detail == "Invalid credentials"
