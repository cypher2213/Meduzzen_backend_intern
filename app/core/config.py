from app.core.app_config import App_Config
from app.core.database_config import DBSettings
from app.core.redis_config import RedisSettings


class Settings(App_Config, DBSettings, RedisSettings):
    pass


settings = Settings()
