from app.core.model_config import BaseConfig


class RedisSettings(BaseConfig):
    REDIS_HOST: str = "localhost"
    REDIS_SCHEME: str
    REDIS_PORT: str = "6379"
    REDIS_DB: str

    @property
    def url(self) -> str:
        return (
            f"{self.REDIS_SCHEME}://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        )
