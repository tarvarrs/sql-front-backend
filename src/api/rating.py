from fastapi import APIRouter, Depends
from src.repositories.user import UserRepository
from src.schemas.rating import RatingResponse
from src.api.dependencies import get_user_repository

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
