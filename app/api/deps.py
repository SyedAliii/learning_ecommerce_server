from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends
from jose import jwt, JWTError
from ..core.config import settings
from ..core.exceptions.exception_main import InvalidCredentialsException

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("id")
        if user_id is None:
            raise InvalidCredentialsException(user_id=user_id, reason="Invalid token payload")
        return user_id
    except JWTError as e:
        raise InvalidCredentialsException(reason=str(e))
