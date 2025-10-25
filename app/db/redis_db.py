import redis.asyncio as redis
from app.core.config import settings
import asyncio
REDIS_URL = settings.REDIS_URL

async def redis_main():
    async with redis.from_url(REDIS_URL,decode_responses=True) as redis_connect:
        try:
            answer = await redis_connect.ping()
            if answer:
                print("Redis successfully connected with async")
        except Exception as e:
            print("Failed to connect to the Redis =>", e)
            
        
    
    
if __name__ == "__main__":
    asyncio.run(redis_main())