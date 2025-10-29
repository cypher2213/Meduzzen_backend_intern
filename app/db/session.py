from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.db.POSTGRES_USER}:@{settings.db.POSTGRES_HOST}:{settings.db.POSTGRES_PORT}/{settings.db.POSTGRES_DB}"
engine = create_async_engine(
    DATABASE_URL,
)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)
