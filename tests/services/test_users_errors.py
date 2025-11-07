from uuid import uuid4

import pytest
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_delete_user_not_found(user_service, mock_repo, mock_session):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await user_service.delete_user(mock_session, uuid4())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(user_service, mock_repo, mock_session):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await user_service.get_user_by_id(mock_session, uuid4())

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_user_not_found(user_service, mock_repo, mock_session):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException):
        await user_service.update_user(uuid4(), {"name": "X"}, mock_session)
