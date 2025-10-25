import redis.asyncio as redis
from app.core.config import settings
import asyncio
REDIS_URL = settings.REDIS_URL

async def redis_main():
    redis_connect = redis.from_url(REDIS_URL,decode_responses=True)

    try:
        redis_answer = await redis_connect.ping()
        if(redis_answer):
            print("Redis connected successfully")
    except Exception as e:
        print("Failed to connect to the Redis =>", e)
    finally:
        await redis_connect.aclose()
        await redis_connect.connection_pool.disconnect()
        
    
    
if __name__ == "__main__":
    asyncio.run(redis_main())