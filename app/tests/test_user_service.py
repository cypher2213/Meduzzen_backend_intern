import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_user_success():
    user = {
        "name": "jesus",
        "email": "jesus21238@gmail.com",
        "password": "12345678",
        "age": 22,
    }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/users/", json=user)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == user["name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_create_user_invalid_payload():
    user_invalid = {"name": "jesus", "email": "jesus77@", "password": "123", "age": -2}
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        response = await ac.post("/users/", json=user_invalid)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "detail" in response.json()
