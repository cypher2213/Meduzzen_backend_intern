from pydantic_settings import BaseSettings


class BaseConfig(BaseSettings):
    model_config = {"extra": "allow", "env_file": ".env", "env_file_encoding": "utf-8"}
