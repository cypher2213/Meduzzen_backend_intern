from fastapi import Depends, Header, HTTPException
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.repository.users_repository import UserRepository


async def auth0_connect(
    authorization: str = Header(...), session: AsyncSession = Depends(get_session)
):
    repo = UserRepository()
    print("🔹 Header received:", authorization)  # 👈 проверяем заголовок

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ")[1]
    print("🔹 Extracted token:", token[:30], "...")  # 👈 выводим начало токена

    try:
        payload = jwt.get_unverified_claims(token)
        print("🔹 Payload:", payload)  # 👈 смотрим, что реально внутри токена

        email = payload.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not found in token")

        user = await repo.get_by_email(session, email)
        if not user:
            user = await repo.create(session, {"email": email})
        return user

    except Exception as e:
        print("❌ Error:", e)
        raise HTTPException(status_code=401, detail="Invalid token")
