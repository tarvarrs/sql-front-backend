from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
from typing import Annotated

from src.schemas.user import UserCreate, UserPublic, UserLogin
from src.schemas.token import Token
from src.utils.auth import create_access_token, get_current_user, security
from src.repositories.user import UserRepository
from src.models.user import User
from src.api.dependencies import get_user_repository

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/register", response_model=UserPublic)
async def register(
    user_data: UserCreate,
    user_repo: UserRepository = Depends(get_user_repository),
):
    if await user_repo.get_user_by_login(user_data.login):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким логином уже существует.",
        )
    
    try:
        user = await user_repo.create_user(
            user_data={"login": user_data.login, "email": user_data.email},
            password=user_data.password,
        )
        return user
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует.",
        )


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    user_repo: UserRepository = Depends(get_user_repository),
):
    user = await user_repo.get_user_by_login(user_data.login)
    if not user or not await user_repo.verify_password(user_data.login, user_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect login or password",
        )
    
    access_token = create_access_token(
        data={"sub": user.login},
        expires_delta=timedelta(minutes=30),
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout():
    return {"message": "Successfully logged out"}

# @router.get("/me", response_model=UserPublic)
# async def read_current_user(
#     current_user: User = Depends(get_current_user),
# ):
#     return current_user