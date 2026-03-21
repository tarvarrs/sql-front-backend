from typing import Any, List, Optional
from pydantic import BaseModel


class QuestProgressResponse(BaseModel):
    scene_id: str
    legend: str
    task: Optional[str] = None
    has_clue: bool


class QuestRunRequest(BaseModel):
    scene_id: str
    sql_query: str


class QuestSubmitRequest(BaseModel):
    scene_id: str
    sql_query: str


class PointsInfo(BaseModel):
    earned: int
    penalty: int


class AchievementAward(BaseModel):
    achievement_id: int
    name: str
    description: str


class QuestSubmitResponse(BaseModel):
    is_correct: bool
    points: PointsInfo
    is_quest_completed: bool
    awarded_achievements: List[AchievementAward] = []


# Переиспользуем схемы из вашего проекта для SQL
class SQLResponse(BaseModel):
    columns: List[str]
    data: List[List[Any]]
    row_count: int
