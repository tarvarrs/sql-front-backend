from fastapi import APIRouter, Depends
from database import get_db
from src.repositories.user import UserRepository
from src.schemas.rating import RatingResponse, UserRating
from src.api.dependencies import get_user_repository

router = APIRouter(prefix="/api/rating", tags=["Рейтинг"])

@router.get("/", summary="Топ 10 игроков по баллам", response_model=RatingResponse)
async def get_top_users(
    limit: int=10,
    user_repo: UserRepository=Depends(get_user_repository)
):
    top_users = await user_repo.get_top_users(limit)
    print(f'DEBUG\n{top_users}\n')
    ranked_users = [
        UserRating(
            login=login,
            total_score=total_score,
            place=idx+1
        )
        for idx, (login, total_score) in enumerate(top_users)
    ]
    return {"top_users": ranked_users}
