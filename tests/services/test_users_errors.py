from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.schemas.user_schema import UserUpdateSchema


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_repo, mock_session):
    mock_repo.get.return_value = None
    current_user = SimpleNamespace(id=uuid4())
    with pytest.raises(HTTPException) as exc:
        await user_service.delete_user(mock_session, current_user)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, mock_repo, mock_session):
    mock_repo.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await user_service.get_user_by_id(mock_session, uuid4())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_user_not_found(user_service, mock_repo, mock_session):
    mock_repo.get.return_value = None
    current_user = SimpleNamespace(id=uuid4())

    with pytest.raises(HTTPException):
        await user_service.update_user({"name": "X"}, mock_session, current_user)


@pytest.mark.asyncio
async def test_update_user_cannot_change_email(
    user_service, mock_repo, mock_session, fake_user
):
    current_user = SimpleNamespace(id=fake_user.id)
    mock_repo.get_by_id.return_value = fake_user

    updated_data = UserUpdateSchema(email="new@example.com")

    with pytest.raises(HTTPException) as exc:
        await user_service.update_user(
            updated_data,
            mock_session,
            current_user,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Email cannot be changed"
    mock_repo.update.assert_not_awaited()
