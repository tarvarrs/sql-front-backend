from fastapi import Depends
from database import get_db
from src.repositories.user import UserRepository

async def get_user_repository(session=Depends(get_db)) -> UserRepository:
    return UserRepository(session)
