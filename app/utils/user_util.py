import jwt as pyjwt
import requests
from fastapi import Depends, Header, HTTPException
from jose import jwt
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth0_config import auth0_settings
from app.core.jwt_config import jwt_settings
from app.db.session import get_session
from app.models.user_model import UserModel
from app.repository.users_repository import UserRepository


async def user_connect(
    authorization: str = Header(...), session: AsyncSession = Depends(get_session)
):
    repo = UserRepository()

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ")[1]

    try:
        not_verified_payload = jwt.get_unverified_claims(token)
        iss = not_verified_payload.get("iss")

        # =============AUTH0===============================

        if iss == f"https://{auth0_settings.AUTH0_DOMAIN}/":
            headers = jwt.get_unverified_header(token)
            kid = headers.get("kid")
            jwks = requests.get(
                f"https://{auth0_settings.AUTH0_DOMAIN}/.well-known/jwks.json"
            ).json()
            key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
            if not key:
                raise HTTPException(
                    status_code=401, detail="Auth0 public key not found"
                )
            public_key = RSAAlgorithm.from_jwk(key)
            payload = jwt.decode(
                token,
                public_key,
                audience=auth0_settings.API_AUDIENCE,
                algorithms=auth0_settings.ALGORITHMS_AUTH0,
            )
            email = payload.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in token")

            user = await repo.get_by_email(session, email)
            if not user:
                user = await repo.create(session, {"email": email})
            return user

        # ===================LOCAL JWT TOKEN==============

        else:
            try:
                decoded_token = pyjwt.decode(
                    token, jwt_settings.SECRET_KEY, algorithms=jwt_settings.ALGORITHM
                )
                user_email = decoded_token.get("sub")
                if not user_email:
                    raise HTTPException(status_code=401, detail="Invalid token")
                result = await session.execute(
                    select(UserModel).where(UserModel.email == user_email)
                )
                user = result.scalar_one_or_none()
                if not user:
                    raise HTTPException(status_code=401, detail="User not found")
                return user
            except pyjwt.ExpiredSignatureError:
                raise HTTPException(status_code=401, detail="Token expired")
            except pyjwt.InvalidTokenError:
                raise HTTPException(status_code=401, detail="Invalid token")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
