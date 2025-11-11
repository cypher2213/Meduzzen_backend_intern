from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer
from pwdlib import PasswordHash

from app.core.jwt_config import jwt_settings

SECRET_KEY = jwt_settings.SECRET_KEY
ALGORITHM = jwt_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MIN = jwt_settings.ACCESS_TOKEN_EXPIRE_MIN
REFRESH_TOKEN_EXPIRE_DAY = jwt_settings.REFRESH_TOKEN_EXPIRE_DAY
OTHER_SECRET_KEY = jwt_settings.OTHER_SECRET_KEY

security = HTTPBearer()
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode.update({"exp": expire, "type": "access"})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
    to_encode.update({"exp": expire, "type": "refresh"})
    token = jwt.encode(to_encode, OTHER_SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_password(enter_pswrd: str, hashed_pswrd: str):
    return pwd_context.verify(enter_pswrd, hashed_pswrd)


def password_hash(password: str):
    return pwd_context.hash(password)


def decode_token(token: str, expected_type: str):
    try:
        key_to_use = SECRET_KEY if expected_type == "access" else OTHER_SECRET_KEY
        payload = jwt.decode(token, key_to_use, algorithms=[ALGORITHM])
        token_type = payload.get("type")

        if token_type != expected_type:
            raise HTTPException(
                status_code=401,
                detail=f"Invalid token type: expected '{expected_type}', got '{token_type}'",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
