from pydantic import BaseModel
from typing import List


class UserRating(BaseModel):
    login: str
    fullname: str | None
    group: str | None
    total_score: int
    place: int
    achievement_icons: List[str] = []

    class Config:
        from_attributes = True


class RatingResponse(BaseModel):
    top_users: list[UserRating]
