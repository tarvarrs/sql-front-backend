from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from database import get_db
from src.models.task import Task
from src.schemas.task import (
    TaskInfo,
    TaskClue,
    TaskExpectedResult,
    TasksCount,
    TaskSolvedCreate
)
from src.repositories.task import TaskRepository
from src.utils.auth import get_current_user
from src.models.user import User

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("/get_info", response_model=TasksCount)
async def get_tasks_count(
    db: AsyncSession = Depends(get_db)
):
    """Возвращает общее количество задач по уровням сложности"""
    repo = TaskRepository(db)
    return await repo.get_tasks_count()

@router.get("/missions/{mission_id}/tasks/{task_id}", response_model=TaskInfo)
async def get_task_info(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Возвращает основную информацию о задаче"""
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/missions/{mission_id}/tasks/{task_id}/clue", response_model=TaskClue)
async def get_task_clue(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Возвращает подсказку к задаче"""
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"clue": task.clue}

@router.get("/missions/{mission_id}/tasks/{task_id}/expected_result", 
           response_model=TaskExpectedResult)
async def get_expected_result(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Возвращает ожидаемый результат задачи"""
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"expected_result": task.expected_result}

# @router.post("/")
# async def add_solved_task(
#     solved_data: TaskSolvedCreate,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_db)
# ):
#     """Добавляет запись о решенной задаче"""
#     repo = TaskRepository(db)
#     await repo.add_solved_task(current_user.user_id, solved_data.task_id)
#     return {"message": "Task marked as solved"}
