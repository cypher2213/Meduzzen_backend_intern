from types import SimpleNamespace

import pytest
from utils import async_gen


@pytest.mark.asyncio
async def test_create_user(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    mock_repo.create.return_value = fake_user
    mock_redis.scan_iter.return_value = async_gen(["users:1", "users:2"])

    result = await user_service.create_user(
        mock_session, {"name": "John", "password": "123"}, mock_redis
    )

    mock_repo.create.assert_called_once()
    mock_redis.delete.assert_called()
    assert result == fake_user


@pytest.mark.asyncio
async def test_delete_user_success(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    mock_repo.get_by_id.return_value = fake_user
    mock_repo.delete.return_value = None
    mock_redis.scan_iter.return_value = async_gen(["users:1", "users:2"])

    result = await user_service.delete_user(mock_session, fake_user.id, mock_redis)

    mock_repo.delete.assert_called_once_with(mock_session, fake_user)
    assert "successfully deleted" in result["message"]


@pytest.mark.asyncio
async def test_update_user_success(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    updated_user = SimpleNamespace(
        id=fake_user.id, name="New Name", email="new@example.com"
    )
    mock_repo.get_by_id.return_value = fake_user
    mock_repo.update.return_value = updated_user
    mock_redis.scan_iter.return_value = async_gen([])

    result = await user_service.update_user(
        fake_user.id, {"name": "New Name"}, mock_session, mock_redis
    )

    mock_repo.update.assert_called_once()
    assert result["message"] == "User updated successfully"
    assert result["name"] == "New Name"
