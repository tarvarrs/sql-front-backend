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


class QuestItem(BaseModel):
    id: str
    title: str
    description: str
    is_completed: bool


class QuestsListResponse(BaseModel):
    quests: List[QuestItem]


class SQLResponse(BaseModel):
    columns: List[str]
    data: List[List[Any]]
    row_count: int
