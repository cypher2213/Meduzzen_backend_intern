from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.db.user_model import UserModel
from app.services.users_service import UserSerivce


@pytest.mark.asyncio
async def test_get_all_users_returns_list():
    mock_session = AsyncMock()
    fake_users = [UserModel(id=1, name="Nick"), UserModel(id=2, name="Jane")]

    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = fake_users
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    service = UserSerivce()
    users = await service.get_all_users(mock_session)

    assert users == fake_users
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_hashes_password_and_commits():
    mock_session = AsyncMock()
    mock_user = UserModel(id=1, name="Nick")
    with patch("app.services.users_service.UserModel", return_value=mock_user):
        service = UserSerivce()
        data = {"name": "Nick", "password": "12345"}
        user = await service.create_user(mock_session, data)

    assert user is mock_user
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
    assert data["password"] != "12345"


@pytest.mark.asyncio
async def test_delete_user_not_found_raises_http_404():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    service = UserSerivce()

    with pytest.raises(HTTPException) as exc:
        await service.delete_user(mock_session, user_id=999)

    assert exc.value.status_code == 404
    assert exc.value.detail == "User not found"


@pytest.mark.asyncio
async def test_update_user_hashes_password_and_commits():
    mock_user = UserModel(id=1, name="OldNick", password="old")
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    service = UserSerivce()
    updated = {"username": "NewNick", "password": "newpass"}
    user = await service.update_user(1, updated, mock_session)

    assert user.username == "NewNick"
    assert user.password != "newpass"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()
