import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.error_middleware import error_middleware


@pytest.fixture
def test_main():
    app = FastAPI()
    app.middleware("http")(error_middleware)

    @app.get("/integrity-error")
    async def integrity_error():
        class DummyOrig:
            def __str__(self):
                return "duplicate key value violates unique constraint"

        raise IntegrityError("INSERT INTO users ...", {}, DummyOrig())

    @app.get("/db-err")
    async def db_error():
        raise SQLAlchemyError("database connection failed")

    @app.get("/unknown-err")
    async def unknown_err():
        raise Exception("Error happened")

    return TestClient(app)


def test_integrity_error(test_main):
    resp = test_main.get("/integrity-error")

    assert resp.status_code == 400
    data = resp.json()

    assert data["error"] == "Integrity Error"
    assert "duplicate key value" in data["detail"]


def test_db_error(test_main):
    resp = test_main.get("/db-err")
    assert resp.status_code == 500
    data = resp.json()

    assert data["error"] == "Database Error"
    assert "database connection failed" in data["detail"]


def test_unknown_err(test_main):
    resp = test_main.get("/unknown-err")
    assert resp.status_code == 500
    data = resp.json()
    assert data["error"] == "Internal Server Error"
    assert "Error happened" in data["detail"]
