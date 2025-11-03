from app.core.model_config import BaseConfig


class JWT_Settings(BaseConfig):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = 15


jwt_settings = JWT_Settings()
