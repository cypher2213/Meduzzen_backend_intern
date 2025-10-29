from app.core.model_config import BaseConfig


class DBSettings(BaseConfig):
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_HOST_AUTH_METHOD: str = "trust"
