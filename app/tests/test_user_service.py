import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.users_service import UserService


async def async_gen(items):
    for i in items:
        yield i


@pytest.fixture
def mock_repo():
    repo = AsyncMock()
    return repo


@pytest.fixture
def mock_redis():
    redis = AsyncMock()

    async def fake_scan_iter(*args, **kwargs):
        if False:
            yield None

    redis.scan_iter = fake_scan_iter

    return redis


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def user_service(mock_repo):
    return UserService(mock_repo)


@pytest.fixture
def fake_user():
    user = MagicMock()
    user.id = uuid4()
    user.name = "John Doe"
    user.email = "john@example.com"
    user.password = "hashedpwd"
    return user


# ====================== TESTS ======================


@pytest.mark.asyncio
async def test_get_all_users_from_cache(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    users_list = [{"id": str(fake_user.id), "name": fake_user.name}]
    mock_redis.get.return_value = json.dumps(users_list)

    result = await user_service.get_all_users(mock_session, mock_redis)

    mock_repo.get_all.assert_not_called()
    assert result == users_list


@pytest.mark.asyncio
async def test_get_all_users_from_db_and_cache(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    mock_redis.get.return_value = None
    mock_repo.get_all.return_value = [fake_user]

    result = await user_service.get_all_users(mock_session, mock_redis)

    mock_repo.get_all.assert_called_once()
    mock_redis.set.assert_called_once()
    assert isinstance(result, list)
    assert result[0].name == "John Doe"


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
    mock_redis.delete.assert_called()  # очистка кеша
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
async def test_delete_user_not_found(user_service, mock_repo, mock_session, mock_redis):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await user_service.delete_user(mock_session, uuid4(), mock_redis)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_user_by_id_from_cache(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    cached = {"id": str(fake_user.id), "name": fake_user.name}
    mock_redis.get.return_value = json.dumps(cached)

    result = await user_service.get_user_by_id(mock_session, fake_user.id, mock_redis)

    mock_repo.get_by_id.assert_not_called()
    assert result == cached


@pytest.mark.asyncio
async def test_get_user_by_id_from_db(
    user_service, mock_repo, mock_session, mock_redis, fake_user
):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = fake_user

    result = await user_service.get_user_by_id(mock_session, fake_user.id, mock_redis)

    mock_repo.get_by_id.assert_called_once()
    mock_redis.set.assert_called_once()
    assert result["message"] == "User Found"


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(
    user_service, mock_repo, mock_session, mock_redis
):
    mock_redis.get.return_value = None
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await user_service.get_user_by_id(mock_session, uuid4(), mock_redis)

    assert exc.value.status_code == 404


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


@pytest.mark.asyncio
async def test_update_user_not_found(user_service, mock_repo, mock_session, mock_redis):
    mock_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException):
        await user_service.update_user(uuid4(), {"name": "X"}, mock_session, mock_redis)
