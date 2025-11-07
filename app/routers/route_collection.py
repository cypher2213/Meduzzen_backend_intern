from fastapi import APIRouter

from app.routers import health, users

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(users.router, prefix="/users", tags=["Users"])
