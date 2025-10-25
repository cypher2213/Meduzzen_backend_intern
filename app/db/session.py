from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import asyncio
from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL
engine = create_async_engine(
    DATABASE_URL,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False 
)

async def connection_test():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        print("Postgres connected successfully:",value)

asyncio.run(connection_test())

