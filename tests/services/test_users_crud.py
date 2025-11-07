from types import SimpleNamespace

import pytest


@pytest.mark.asyncio
async def test_create_user(user_service, mock_repo, mock_session, fake_user):
    mock_repo.create.return_value = fake_user

    result = await user_service.create_user(
        mock_session,
        {"name": "John", "password": "123"},
    )

    mock_repo.create.assert_called_once()
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
        {"name": "New Name"},
        mock_session,
    )

    mock_repo.update.assert_called_once()
    assert result["message"] == "User updated successfully"
    assert result["name"] == "New Name"
