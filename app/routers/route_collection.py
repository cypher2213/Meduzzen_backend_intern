from fastapi import APIRouter

from app.routers import companies, health, users

router = APIRouter()

router.include_router(health.router, tags=["Health"])
router.include_router(users.router, prefix="/users", tags=["Users"])
router.include_router(companies.router, prefix="/companies", tags=["Companies"])
