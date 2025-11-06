# app/dependencies/auth.py
from functools import wraps

from fastapi import HTTPException, Request
from jose import jwt

from app.db.session import get_session
from app.db.users_repository import UserRepository

SECRET_KEY = "your_dummy_secret"
ALGORITHM = "RS256"

repo = UserRepository()


def require_auth(func):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing Bearer token")

        token = authorization.split(" ")[1]

        try:
            payload = jwt.get_unverified_claims(token)
            email = payload.get("email")
            if not email:
                raise HTTPException(status_code=400, detail="Email not found in token")

            async with get_session() as session:
                user = await repo.get_by_email(session, email)
                if not user:
                    user = await repo.create(session, {"email": email})

            kwargs["current_user"] = user
            return await func(request, *args, **kwargs)

        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")

    return wrapper
