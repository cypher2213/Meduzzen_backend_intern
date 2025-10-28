from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "redis"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
