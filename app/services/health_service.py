import redis.asyncio as redis
from sqlalchemy import text

from app.core.config import settings
from app.core.logger import logger
from app.db.session import AsyncSessionLocal

REDIS_URL = settings.redis.REDIS_URL


async def redis_main():
    async with redis.from_url(REDIS_URL, decode_responses=True) as redis_connect:
        try:
            answer = await redis_connect.ping()
            if answer:
                logger.info("Redis successfully connected with async")
                return True
        except Exception as e:
            logger.info("Failed to connect to the Redis =>", e)
            return False


async def posgtres_main():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        logger.info("Postgres connected successfully:")
        return True if value else False
