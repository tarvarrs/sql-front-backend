from fastapi import APIRouter, Depends
from database import get_db
from src.models.user import User
from src.repositories.user import UserRepository
from src.schemas.rating import RatingResponse
from src.api.dependencies import get_user_repository
from src.utils.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/rating", tags=["Рейтинг"])

@router.get("/",
            summary="Топ 10 игроков",
            response_model=RatingResponse
            )
async def get_top_users(
    limit: int=10,
    user_repo: UserRepository=Depends(get_user_repository)
):
    top_users = await user_repo.get_top_users(limit)

    return {"top_users": top_users}


@router.get("/personal", summary="Место в рейтинге")
async def get_place_in_rating(
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository=Depends(get_user_repository)
):
    result = await user_repo.get_user_place(current_user.user_id)
    return result
