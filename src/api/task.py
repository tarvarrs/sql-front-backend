from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from src.api.dependencies import get_task_repository
from database import get_db
from src.models.task import Task
from src.schemas.task import (
    MissionsResponse,
    SolvedTasksResponse,
    TaskInfo,
    TaskClue,
    TaskExpectedResult,
    TasksCount,
    TaskSolvedCreate,
    SQLRequest,
    SQLResponse,
    ValidationResult
)
from src.repositories.task import TaskRepository
from src.utils.auth import get_current_user
from src.models.user import User
from src.utils.sql_executor import SQLExecutor

router = APIRouter(prefix="/api/missions", tags=["Миссии и задачи"])
sql_executor = SQLExecutor()

@router.get("/get_info", summary="Количество задач по категориям", tags=["Профиль"],response_model=TasksCount)
async def get_tasks_count(
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    return await repo.get_tasks_count()

@router.get("/{mission_id}/tasks/{task_id}", summary="Основная информация о задаче", response_model=TaskInfo)
async def get_task_info(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.get("/{mission_id}/tasks/{task_id}/clue", summary="Текстовая подсказка", response_model=TaskClue)
async def get_task_clue(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"clue": task.clue}

@router.get("/{mission_id}/tasks/{task_id}/expected_result",
            summary="Ожидаемый результат", 
            response_model=TaskExpectedResult)
async def get_expected_result(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
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

@router.post("/{mission_id}/tasks/{task_id}/run",
            summary="Выполнение SQL",
            response_model=SQLResponse)
async def run_sql_query(
    mission_id: int,
    task_id: int,
    request: SQLRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    try:
        return await sql_executor.execute_sql(request.sql_query)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/{mission_id}/tasks/{task_id}/submit",
            summary="Проверка ответа",
            response_model=ValidationResult)
async def submit_sql_query(
    mission_id: int,
    task_id: int,
    request: SQLRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    user_result = await sql_executor.execute_sql(request.sql_query)

    expected_result = task.expected_result

    if not expected_result:
        raise HTTPException(status_code=500, detail="No solution for this task yet")

    is_correct = (
        user_result["columns"] == expected_result.get("columns", []) and
        user_result["data"] == expected_result.get("data", [])
    )
    return ValidationResult(
        is_correct=is_correct,
        message="Correct!" if is_correct else "Results don't match"
    )

@router.get("/", summary="Все задания, сгруппированные по миссиям", tags=["Отображение всех задач"], response_model=MissionsResponse)
async def get_all_missions(
    repo: TaskRepository = Depends(get_task_repository)
):
    tasks = await repo.get_all_tasks_grouped()
    return {"missions": tasks}

@router.get("/solved",
            summary="Решенные задачи",
            tags=["Отображение всех задач"],
            response_model=SolvedTasksResponse)
async def get_solved_missions(
    current_user: User = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repository)
):
    solved_tasks = await repo.get_user_solved_tasks(current_user.user_id)
    return {"solved_missions": solved_tasks}
