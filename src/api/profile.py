from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List

from database import get_db
from src.models.user import User
from src.models.progress import UserProgress
from src.models.achievement import Achievement, UsersAchievements, UserAchievementProgress
from src.utils.auth import get_current_user
from src.schemas.user import UserPublic

router = APIRouter(prefix="/api/profile", tags=["Профиль"])

@router.get("/me", summary="Логин и баллы", response_model=UserPublic)
async def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user

@router.get("/tasks_progress", summary="Прогресс по задачам")
async def get_my_progress(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(UserProgress).where(UserProgress.user_id == current_user.user_id))
    progress = result.scalars().first()
    
    if not progress:
        return {
            "easy_solved": 0,
            "medium_solved": 0,
            "hard_solved": 0
        }
    
    return {
        "easy_solved": progress.easy_tasks_solved,
        "medium_solved": progress.medium_tasks_solved,
        "hard_solved": progress.hard_tasks_solved
    }

@router.get("/achievements", summary="Имеющиеся ачивки")
async def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(
            Achievement.category_name,
            Achievement.icon,
            Achievement.name,
            Achievement.description,
            Achievement.historical_info
        )
        .join(UsersAchievements)
        .where(UsersAchievements.user_id == current_user.user_id)
    )
    achievements = result.all()
    
    grouped_achievements: Dict[str, List] = {}
    
    for ach in achievements:
        category = ach.category_name
        achievement_data = {
            "icon": ach.icon,
            "name": ach.name,
            "description": ach.description,
            "historical_info": ach.historical_info
        }
        
        if category not in grouped_achievements:
            grouped_achievements[category] = []
        
        grouped_achievements[category].append(achievement_data)
    
    return grouped_achievements
