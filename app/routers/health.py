from fastapi import APIRouter

from app.services.connect_service import connection_check

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/connection")
async def redis_connection():
    connection_res = await connection_check()
    return connection_res
