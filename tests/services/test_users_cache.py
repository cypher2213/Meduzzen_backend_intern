import json

import pytest


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
