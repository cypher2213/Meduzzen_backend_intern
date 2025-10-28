from pydantic_settings import BaseSettings


class DBSettings(BaseSettings):
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    DOCKER_DATABASE_URL: str = "postgresql+asyncpg://nick:@postgres:5432/mydb"
    POSTGRES_HOST_AUTH_METHOD: str = "trust"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
