from app.core.model_config import BaseConfig


class Auth0_Settings(BaseConfig):
    AUTH0_DOMAIN: str
    API_AUDIENCE: str
    ALGORITHMS_AUTH0: str = "RS256"


auth0_settings = Auth0_Settings()
