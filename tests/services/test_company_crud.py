from unittest.mock import ANY, AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.company_model import CompanyModel
from app.models.user_model import UserModel
from app.repository.companies_repository import CompaniesRepository
from app.schemas.company_schema import CompanyCreate, CompanyUpdate
from app.services.companies_service import CompaniesService


@pytest.fixture
def repo_mock():
    return AsyncMock(spec=CompaniesRepository)


@pytest.fixture
def service(repo_mock):
    return CompaniesService(repo_mock)


@pytest.fixture
def async_session_mock():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_mock():
    return UserModel(id=uuid4(), name="Test User")


@pytest.mark.asyncio
async def test_get_all_companies(service, repo_mock, async_session_mock):
    company1 = CompanyModel(
        id=uuid4(), name="Company1", description="Desc1", is_public=True
    )
    company2 = CompanyModel(
        id=uuid4(), name="Company2", description="Desc2", is_public=False
    )
    repo_mock.get_all.return_value = [company1, company2]

    result = await service.get_all_companies(async_session_mock)

    assert len(result) == 2
    assert result[0]["name"] == "Company1"
    assert result[1]["name"] == "Company2"
    repo_mock.get_all.assert_awaited_once_with(async_session_mock, 10, 0)


@pytest.mark.asyncio
async def test_get_company_found(service, repo_mock, async_session_mock):
    company = MagicMock(spec=CompanyModel, name="TestCompany")
    repo_mock.company_get.return_value = company

    result = await service.get_company(uuid4(), async_session_mock)

    assert result["message"] == "Company successfully found!"
    assert result["company"] == company
    repo_mock.company_get.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_company_not_found(service, repo_mock, async_session_mock):
    repo_mock.company_get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.get_company(uuid4(), async_session_mock)
    assert exc.value.status_code == 404
    assert exc.value.detail == "Company not found"


@pytest.mark.asyncio
async def test_company_create(service, repo_mock, async_session_mock, user_mock):
    company_data = CompanyCreate(name="NewCo", description="Desc", is_public=True)
    company_obj = MagicMock(spec=CompanyModel, id=uuid4(), name="NewCo")
    repo_mock.create_company.return_value = company_obj

    result = await service.company_create(company_data, async_session_mock, user_mock)

    assert result["message"] == f"Company created successfully by {user_mock.name}."
    assert result["company"] == company_obj
    repo_mock.create_company.assert_awaited_once()
    repo_mock.add_user_role.assert_awaited_once_with(
        db=async_session_mock,
        user_id=user_mock.id,
        company_id=company_obj.id,
        role="owner",
    )
    async_session_mock.refresh.assert_awaited_once_with(company_obj)


@pytest.mark.asyncio
async def test_company_update_success(
    service, repo_mock, async_session_mock, user_mock
):
    company_id = uuid4()
    company_obj = MagicMock(spec=CompanyModel, id=company_id, name="OldName")
    repo_mock.get_owner_company.return_value = company_obj
    repo_mock.update_company.return_value = company_obj

    update_data = CompanyUpdate(name="NewName")

    result = await service.company_update(
        company_id, update_data, async_session_mock, user_mock
    )

    assert result["company"] == company_obj
    assert result["company"].name == "OldName" or result["company"].name == "NewName"
    repo_mock.get_owner_company.assert_awaited_once_with(
        async_session_mock, company_id, user_mock.id
    )
    repo_mock.update_company.assert_awaited_once_with(async_session_mock, company_obj)


@pytest.mark.asyncio
async def test_company_update_forbidden(
    service, repo_mock, async_session_mock, user_mock
):
    repo_mock.get_owner_company.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.company_update(
            uuid4(), CompanyUpdate(name="x"), async_session_mock, user_mock
        )
    assert exc.value.status_code == 403
    assert "owner" in exc.value.detail


@pytest.mark.asyncio
async def test_company_delete_success(
    service, repo_mock, async_session_mock, user_mock
):
    company_obj = MagicMock(spec=CompanyModel, name="DeleteMe")
    repo_mock.delete_company.return_value = company_obj

    result = await service.company_delete(uuid4(), async_session_mock, user_mock)

    assert result["message"] == f"Company {company_obj.name} deleted successfully."
    repo_mock.delete_company.assert_awaited_once_with(
        async_session_mock, ANY, user_mock
    )


@pytest.mark.asyncio
async def test_company_delete_forbidden(
    service, repo_mock, async_session_mock, user_mock
):
    repo_mock.delete_company.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.company_delete(uuid4(), async_session_mock, user_mock)
    assert exc.value.status_code == 403
    assert "owner" in exc.value.detail
