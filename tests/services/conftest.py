from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.services.users_service import UserService


@pytest.fixture
def mock_repo():
    return AsyncMock()


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
