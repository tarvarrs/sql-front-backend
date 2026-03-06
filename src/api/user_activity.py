from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.utils.auth import get_current_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.dependencies import get_task_repository
from src.repositories.task import TaskRepository
from src.utils.analytics import log_user_event

router = APIRouter(prefix="/util")


@router.post(
    "/{mission_id}/tasks/{task_id}/inactive",
    summary="Пользователь покинул страницу",
)
async def log_user_inactive(
    mission_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repository),
    db: AsyncSession = Depends(get_db),
):
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача на найдена")
    await log_user_event(
        session=db,
        user_id=current_user.user_id,
        event_type="user_inactive",
        task_id=task.task_global_id,
        payload={"mission_id": mission_id, "task_id": task_id},
    )
