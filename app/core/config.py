from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    host: str="0.0.0.0"
    port: int="8000"
    origins: list[str]=["http://localhost:3000"]

    class Config:
        env_file=".env"
        env_file_encoding="utf-8"
        
@lru_cache    
def get_settings():
    return Settings()
        