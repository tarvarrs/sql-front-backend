# src/api/analytics.py
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from src.models.user import User
from src.repositories.analytics import get_thinking_time_stats
from src.schemas.analytics import TaskThinkingTime
from src.utils.auth import get_current_user

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
