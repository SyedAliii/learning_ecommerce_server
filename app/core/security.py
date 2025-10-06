from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from .config import settings
from passlib.context import CryptContext

argon_context = CryptContext(schemes=["argon2"], deprecated="auto")

def create_access_token(email: str, user_id: int, expires_delta: Optional[timedelta] = None):
    encode = {"sub": email, "id": user_id}
    utc_dt = datetime.now(timezone.utc)
    dt = utc_dt.astimezone()
    if expires_delta:
        expire = dt + expires_delta
    else:
        expire = dt + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
    
def get_password_hash(password: str) -> str:
    return argon_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return argon_context.verify(plain_password, hashed_password)