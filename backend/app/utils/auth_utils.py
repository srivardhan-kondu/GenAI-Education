import bcrypt
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from bson import ObjectId

from app.config import settings
from app.database.connection import get_database

_bearer = HTTPBearer()


# ── Password helpers ──────────────────────────────────────────────────────────

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def get_password_hash(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    payload = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload["exp"] = expire
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# ── FastAPI dependency ────────────────────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise exc
    except JWTError:
        raise exc

    db = get_database()
    try:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        raise exc

    if user is None:
        raise exc

    user["id"] = str(user["_id"])
    return user
