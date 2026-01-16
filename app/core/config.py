from pydantic_settings import BaseSettings

from app.core.app_config import AppConfig
from app.core.database_config import DBSettings
from app.core.redis_config import RedisSettings


class Settings(BaseSettings):
    app: AppConfig = AppConfig()
    db: DBSettings = DBSettings()
    redis: RedisSettings = RedisSettings()


settings = Settings()
