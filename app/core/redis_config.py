from app.core.model_config import BaseConfig


class RedisSettings(BaseConfig):
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "redis"
