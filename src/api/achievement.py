from fastapi import APIRouter, Depends
from database import get_db
from src.api.dependencies import get_achievement_repository
from src.repositories.achievement import AchievementRepository
from src.schemas.achievement import AchievementsResponse
from src.utils.auth import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/achievements", tags=["Достижения"])

@router.get("/", summary="Достижения со статусом наличия", response_model=AchievementsResponse)
async def get_achievements_grouped(
    current_user: User = Depends(get_current_user),
    repo: AchievementRepository = Depends(get_achievement_repository)
):
    """Возвращает все достижения, сгруппированные по категориям"""
    grouped_achievements = await repo.get_achievements_grouped(current_user.user_id)
    return {"categories": grouped_achievements}
