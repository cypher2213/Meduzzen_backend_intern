from app.core.model_config import BaseConfig


class JWT_Settings(BaseConfig):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MIN: int = 15
    REFRESH_TOKEN_EXPIRE_DAY: int = 7
    OTHER_SECRET_KEY: str


jwt_settings = JWT_Settings()
