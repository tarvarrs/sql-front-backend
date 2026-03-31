from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import re

from config import settings
from database import get_db
from src.models.user import User
from src.repositories.quest import QuestRepository
from src.schemas.quest import (
    QuestProgressResponse,
    QuestRunRequest,
    QuestSubmitRequest,
    QuestSubmitResponse,
    SQLResponse,
    QuestsListResponse,
)
from src.utils.auth import get_current_user
from src.utils.sql_executor import SQLExecutor
from src.utils.quest_loader import QuestLoader
from src.utils.scoring_service import ScoringService

router = APIRouter(prefix="/api/quests", tags=["Квесты"])
sql_executor = SQLExecutor(settings.QUEST_DATABASE_URL)


def get_quest_repository(db: AsyncSession = Depends(get_db)) -> QuestRepository:
    return QuestRepository(db)


def _extract_update_value(sql_query: str) -> str:
    """Упрощенный парсер для извлечения значения из UPDATE запроса."""
    match = re.search(
        r"SET\s+\w+\s*=\s*'?(.*?)'?\s*(?:WHERE|$|;)", sql_query, re.IGNORECASE
    )
    if match:
        return match.group(1).strip()
    return ""

@router.get(
    "",
    summary="Получение списка всех квестов",
    response_model=QuestsListResponse,
)
async def get_all_quests(
    current_user: User = Depends(get_current_user),
    repo: QuestRepository = Depends(get_quest_repository),
):
    all_quests = QuestLoader.get_all_quests()

    completed_quests = await repo.get_user_completed_quests(current_user.user_id)

    quests_response = []
    for q in all_quests:
        quests_response.append({
            "id": q["id"],
            "title": q["title"],
            "description": q["description"],
            "is_completed": q["id"] in completed_quests
        })

    return {"quests": quests_response}


@router.get(
    "/{quest_id}/progress",
    summary="Инициализация или продолжение квеста",
    response_model=QuestProgressResponse,
)
async def get_quest_progress(
    quest_id: str,
    current_user: User = Depends(get_current_user),
    repo: QuestRepository = Depends(get_quest_repository),
):
    try:
        scene_data = await repo.get_user_current_scene(current_user.user_id, quest_id)
    except HTTPException as e:
        if e.status_code == 404:
            await repo.start_quest(current_user.user_id, quest_id)
            scene_data = await repo.get_user_current_scene(
                current_user.user_id, quest_id
            )
        else:
            raise e

    return {
        "scene_id": scene_data["scene_id"],
        "legend": scene_data["legend"],
        "task": scene_data["task"],
        "has_clue": scene_data["has_clue"],
    }


@router.post(
    "/{quest_id}/run",
    summary="Выполнение SQL запроса в квесте",
    response_model=SQLResponse,
)
async def run_quest_sql(
    quest_id: str,
    request: QuestRunRequest,
    current_user: User = Depends(get_current_user),
    repo: QuestRepository = Depends(get_quest_repository),
):
    scene_data = await repo.get_user_current_scene(current_user.user_id, quest_id)
    if scene_data["scene_id"] != request.scene_id:
        raise HTTPException(status_code=400, detail="Неверная сцена для выполнения")

    try:
        if scene_data["is_branching"]:
            raise HTTPException(
            status_code=403, detail=f"Пока низя"
            )
        return await sql_executor.execute_sql(request.sql_query)
    except HTTPException as e:
        raise HTTPException(
            status_code=400, detail=f"Ошибка выполнения: {str(e.detail)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}"
        )


@router.post(
    "/{quest_id}/submit",
    summary="Отправка решения квеста на проверку",
    response_model=QuestSubmitResponse,
)
async def submit_quest_solution(
    quest_id: str,
    request: QuestSubmitRequest,
    current_user: User = Depends(get_current_user),
    repo: QuestRepository = Depends(get_quest_repository),
    db: AsyncSession = Depends(get_db),
):
    scene = await repo.get_user_current_scene(current_user.user_id, quest_id)

    user_answer_value = ""
    is_correct = False

    if scene["is_branching"]:
        user_answer_value = _extract_update_value(request.sql_query)
        is_correct = user_answer_value in scene.get("branches", {})
    else:
        if scene.get("expected_result"):
            user_result = await sql_executor.execute_sql(request.sql_query)
            expected = scene["expected_result"]
            is_correct = user_result["columns"] == expected.get(
                "columns", []
            ) and user_result["data"] == expected.get("data", [])
        else:
            is_correct = True

    is_quest_completed = False

    scoring_service = ScoringService(db)

    if is_correct:
        result = await repo.submit_answer(
            user_id=current_user.user_id,
            quest_id=quest_id,
            user_answer=user_answer_value,
            is_correct=is_correct,
        )
        await scoring_service.add_points(current_user.user_id, 100)
        is_quest_completed = result.get("status") == "completed"
    else:
        await scoring_service.deduct_points(current_user.user_id, 10)
    await db.commit()

    return {
        "is_correct": is_correct,
        "points": {
            "earned": 100 if is_correct else 0,
            "penalty": 0 if is_correct else 10,
        },
        "is_quest_completed": is_quest_completed,
        "awarded_achievements": [],  # TODO: integrate achievements with quest module
    }
