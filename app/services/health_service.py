import redis.asyncio as redis
from sqlalchemy import text

from app.core.config import settings
from app.db.session import AsyncSessionLocal

REDIS_URL = settings.redis.REDIS_URL


async def redis_main():
    async with redis.from_url(REDIS_URL, decode_responses=True) as redis_connect:
        try:
            answer = await redis_connect.ping()
            if answer:
                print("Redis successfully connected with async")
                return True
        except Exception as e:
            print("Failed to connect to the Redis =>", e)
            return False


async def posgtres_main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        print("Postgres connected successfully:", value)
        return True if value else False
