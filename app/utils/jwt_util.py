from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import HTTPBearer
from pwdlib import PasswordHash

from app.core.jwt_config import jwt_settings

SECRET_KEY = jwt_settings.SECRET_KEY
ALGORITHM = jwt_settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MIN = jwt_settings.ACCESS_TOKEN_EXPIRE_MIN
REFRESH_TOKEN_EXPIRE_DAY = jwt_settings.REFRESH_TOKEN_EXPIRE_DAY

security = HTTPBearer()
pwd_context = PasswordHash.recommended()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MIN)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAY)
    to_encode.update({"exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_password(enter_pswrd: str, hashed_pswrd: str):
    return pwd_context.verify(enter_pswrd, hashed_pswrd)


def password_hash(password: str):
    return pwd_context.hash(password)
