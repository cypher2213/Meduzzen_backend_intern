from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ORIGINS: list[str] = ["http://localhost:3000"]
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379/0"
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        

settings = Settings()
        