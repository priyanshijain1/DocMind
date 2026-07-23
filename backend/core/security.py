from datetime import datetime, timedelta, timezone

from fastapi import Depends, Header
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": user_id, "exp": expire}, settings.jwt_secret, algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> str | None:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        return payload.get("sub")
    except Exception:
        return None


async def get_current_user(
    authorization: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    from core.models import User

    if not authorization or not authorization.startswith("Bearer "):
        return await _get_or_create_anonymous(db)
    token = authorization.split(" ")[1]
    user_id = decode_access_token(token)
    if not user_id:
        return await _get_or_create_anonymous(db)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        return await _get_or_create_anonymous(db)
    return user


async def _get_or_create_anonymous(db: AsyncSession):
    from core.models import User

    result = await db.execute(
        select(User).where(User.email == "anonymous@docmind.local")
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(id="anonymous", email="anonymous@docmind.local", password_hash="")
        db.add(user)
        await db.commit()
    return user
