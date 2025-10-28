from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ORIGINS: list[str] = ["http://localhost:3000"]
    DATABASE_URL: str
    REDIS_URL: str
    REDIS_HOST: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    DOCKER_DATABASE_URL: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
