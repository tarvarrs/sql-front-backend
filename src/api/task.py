from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
from src.api.dependencies import get_task_repository
from database import get_db
from src.models.task import Task
from src.models.clue import PurchasedClue
from src.schemas.task import (
    GroupedTasksResponse,
    MissionsResponse,
    SolvedTasksResponse,
    TaskInfo,
    TaskClue,
    TaskExpectedResult,
    TaskSubmissionResult,
    TasksCount,
    TaskSolvedCreate,
    SQLRequest,
    SQLResponse,
    ValidationResult,
    TaskWithStatusResponse
)
from src.repositories.task import TaskRepository
from src.utils.auth import get_current_user
from src.models.user import User
from src.utils.sql_executor import SQLExecutor
from config import settings

router = APIRouter(prefix="/api/missions", tags=["Миссии и задачи"])
sql_executor = SQLExecutor()

@router.get("/get_info", summary="Количество задач по категориям", tags=["Профиль"],response_model=TasksCount)
async def get_tasks_count(
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    return await repo.get_tasks_count()

@router.get("/{mission_id}/tasks/{task_id}",
            summary="Основная информация о задаче",
            response_model=TaskWithStatusResponse)
async def get_task_info(
    mission_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task, is_solved = await repo.get_task_info_with_status(
                                                            mission_id,
                                                            task_id,
                                                            current_user.user_id
                                                            )
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    purchased_clue1 = await repo.session.execute(
        select(PurchasedClue.clue_type)
        .where(
            (PurchasedClue.user_id == current_user.user_id) &
            (PurchasedClue.task_global_id == task.task_global_id) &
            (PurchasedClue.clue_type == 1)
            )
        )
    purchased_clue2 = await repo.session.execute(
        select(PurchasedClue.clue_type)
        .where(
            (PurchasedClue.user_id == current_user.user_id) &
            (PurchasedClue.task_global_id == task.task_global_id) &
            (PurchasedClue.clue_type == 2)
            )
        )
    has_clue1 = purchased_clue1.scalar_one_or_none()
    has_clue2 = purchased_clue2.scalar_one_or_none()

    return {"task_id": task.task_id,
            "mission_id": task.mission_id,
            "title": task.title,
            "description": task.description,
            "is_solved": is_solved,
            "has_clue1": bool(has_clue1),
            "has_clue2": bool(has_clue2)
            }

@router.get("/{mission_id}/tasks/{task_id}/clue", summary="Текстовая подсказка", response_model=TaskClue)
async def get_task_clue(
    mission_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"clue": task.clue}

@router.post("/{mission_id}/tasks/{task_id}/clue",
            summary="Купить текстовую подсказку",
            tags=["Подсказки"],
            )
async def purchase_clue(
    mission_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repository)
):
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача на найдена")
    cost = int(settings.TASK_POINTS[mission_id] * 0.1)
    purchased_clue1 = await repo.session.execute(
        select(PurchasedClue.clue_type)
        .where(
            (PurchasedClue.user_id == current_user.user_id) &
            (PurchasedClue.task_global_id == task.task_global_id) &
            (PurchasedClue.clue_type == 1)
            )
        )
    has_clue1 = purchased_clue1.scalar_one_or_none()
    if has_clue1:
        return {"points_spent": 0,
                "total_score": current_user.total_score,
                "clue": task.clue
                }
    await repo.purchase_clue(
        user_id=current_user.user_id,
        task_global_id=task.task_global_id,
        clue_type=1,
        cost=cost
    )
    return {
        "points_spent": cost,
        "total_score": current_user.total_score,
        "clue": task.clue
    }

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
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return {"expected_result": task.expected_result}

@router.post("/{mission_id}/tasks/{task_id}/expected_result",
            summary="Купить ожидаемый результат",
            tags=["Подсказки"],
            )
async def purchase_expected_result(
    mission_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repository)
):
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача на найдена")
    cost = int(settings.TASK_POINTS[mission_id] * 0.2)
    purchased_clue2 = await repo.session.execute(
        select(PurchasedClue.clue_type)
        .where(
            (PurchasedClue.user_id == current_user.user_id) &
            (PurchasedClue.task_global_id == task.task_global_id) &
            (PurchasedClue.clue_type == 2)
            )
        )
    has_clue2 = purchased_clue2.scalar_one_or_none()
    if has_clue2:
        return {"points_spent": 0,
                "total_score": current_user.total_score,
                "expected_result": task.expected_result
                }
    await repo.purchase_clue(
        user_id=current_user.user_id,
        task_global_id=task.task_global_id,
        clue_type=2,
        cost=cost
    )
    return {
        "points_spent": cost,
        "total_score": current_user.total_score,
        "expected_result": task.expected_result
    }

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
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    try:
        return await sql_executor.execute_sql(request.sql_query)
    except HTTPException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ошибка во время выполнения: {str(e.detail)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Внутренняя ошибка сервера: {str(e)}"
        )

@router.post("/{mission_id}/tasks/{task_id}/submit",
            summary="Проверка ответа",
            response_model=TaskSubmissionResult
            )
async def submit_sql_query(
    mission_id: int,
    task_id: int,
    request: SQLRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    repo = TaskRepository(db)
    task = await repo.get_task_info(mission_id, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    
    user_result = await sql_executor.execute_sql(request.sql_query)
    expected_result = task.expected_result

    if not expected_result:
        raise HTTPException(status_code=500, detail="Для этой задачи еще не добавлен ответ")
    
    is_correct = (
        user_result["columns"] == expected_result.get("columns", []) and
        user_result["data"] == expected_result.get("data", [])
    )
    try:
        result = await repo.check_and_reward_task(
            user_id=current_user.user_id,
            mission_id=mission_id,
            task_id=task_id,
            is_correct=is_correct
        )
        
        return {
            **result,
            "is_correct": is_correct
        }

    except IndexError:
        raise HTTPException(
            status_code=400,
            detail="Некорректный mission_id: должен быть от 0 до 2 включительно"
        )

# @router.get("/",
#             summary="Все задания, сгруппированные по миссиям",
#             tags=["Отображение всех задач"],
#             response_model=MissionsResponse)
# async def get_all_missions(
#     repo: TaskRepository = Depends(get_task_repository)
# ):
#     tasks = await repo.get_all_tasks_grouped()
#     return {"missions": tasks}

# @router.get("/solved",
#             summary="Решенные задачи",
#             tags=["Отображение всех задач"],
#             response_model=SolvedTasksResponse)
# async def get_solved_missions(
#     current_user: User = Depends(get_current_user),
#     repo: TaskRepository = Depends(get_task_repository)
# ):
#     solved_tasks = await repo.get_user_solved_tasks(current_user.user_id)
#     return {"solved_missions": solved_tasks}
@router.get("/tasks",
            summary="Отображение всех задач со статусом решения",
            response_model=GroupedTasksResponse)
async def get_tasks_grouped(
    current_user: User = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repository)
):
    grouped_tasks = await repo.get_all_tasks_grouped_with_status(current_user.user_id)

    return {"missions": grouped_tasks}

@router.get("/",
            summary="Задачи со статусом решения",
            response_model=MissionsResponse)
async def get_tasks_grouped(
    current_user: User = Depends(get_current_user),
    repo: TaskRepository = Depends(get_task_repository)
):
    grouped_tasks = await repo.get_tasks_grouped_by_mission(current_user.user_id)
    return {"missions": grouped_tasks}