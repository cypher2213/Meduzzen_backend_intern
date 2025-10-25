from app.db.session import posgtres_main
from app.db.redis_db import redis_main

async def connection_check():
    psql_ok = await posgtres_main()
    redis_ok = await redis_main()
    
    return {
        "postgres": "Postgres connected" if psql_ok else "Postgres connection failed",
        "redis": "Redis connected" if redis_ok else "Redis connection failed"
    }