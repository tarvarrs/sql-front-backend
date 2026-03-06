from fastapi import APIRouter, Depends, HTTPException

from src.api.dependencies import get_progress_repository
from src.repositories.progress import ProgressRepository
from src.schemas.progress import UserProgressInDB

router = APIRouter(prefix="/api/progress", tags=["progress"])


@router.get("/{user_id}", response_model=UserProgressInDB)
async def get_progress(
    user_id: int, repo: ProgressRepository = Depends(get_progress_repository)
):
    progress = await repo.get_user_progress(user_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Информация о прогрессе не найдена")
    return progress
