from typing import Dict, List
from pydantic import BaseModel


class AchievementInfo(BaseModel):
    achievement_id: int
    icon: str
    name: str
    description: str
    historical_info: str
    is_earned: bool


class AchievementsResponse(BaseModel):
    categories: Dict[str, List[AchievementInfo]]
