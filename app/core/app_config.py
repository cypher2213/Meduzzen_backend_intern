from app.core.model_config import BaseConfig


class AppConfig(BaseConfig):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ORIGINS: list[str] = ["http://localhost:3000"]
