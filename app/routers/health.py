from fastapi import APIRouter

from app.utils.connection_util import connection_check

router = APIRouter()


@router.get("/")
async def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


@router.get("/connection")
async def connection_route():
    connection_res = await connection_check()
    return connection_res
