import logging

from fastapi import Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

logger = logging.getLogger(__name__)


async def error_middleware(request: Request, call_next):
    try:
        resp = await call_next(request)
        return resp
    except IntegrityError as e:
        logger.error(f"Integrity error: {e}")
        return JSONResponse(
            status_code=400, content={"error": "Integrity Error", "detail": str(e.orig)}
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error: {e}")
        return JSONResponse(
            status_code=500, content={"error": "Database Error", "detail": str(e)}
        )

    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(e)},
        )
