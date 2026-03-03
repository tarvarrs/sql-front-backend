# src/api/analytics.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from src.schemas.analytics import TaskThinkingTime
from src.models.user import User
from src.repositories.analytics import get_thinking_time_stats
from src.utils.auth import get_current_user
from database import get_db

router = APIRouter(prefix="/analytics", tags=["Аналитика"])


@router.get(
    "/first-attempt",
    response_model=List[TaskThinkingTime],
    summary="Время от первого открытия задачи до первой попытки решения",
)
async def get_my_thinking_time(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    return await get_thinking_time_stats(db, current_user.user_id)
