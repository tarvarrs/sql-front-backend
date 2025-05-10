from datetime import datetime, timedelta
import jwt
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import ValidationError
from config import settings
from src.schemas.token import TokenData
from src.repositories.user import UserRepository
from src.api.dependencies import get_user_repository
from src.models.user import User

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode,
                            settings.SECRET_KEY,
                            algorithm=settings.ALGORITHM
                            )
    return encoded_jwt


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token,
                            settings.SECRET_KEY,
                            algorithms=[settings.ALGORITHM]
                            )
        login: str = payload.get("sub")
        if login is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не удалось валидировать данные",
            )
        return TokenData(login=login)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невозможно валидировать данные",
        )


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        user_repo: UserRepository = Depends(get_user_repository),
) -> User:
    token_data = decode_token(credentials.credentials)
    user = await user_repo.get_user_by_login(token_data.login)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
